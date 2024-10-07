import feedparser
import spacy
import mysql.connector
from mysql.connector import Error
from celery import Celery
from dateutil import parser
import logging

#Celery setup
app = Celery('news_parser', broker='redis://localhost:6380/0', backend='redis://localhost:6380/0')

#Logging setup
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("tasks.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

#RSS feeds to parse
rss_feeds = [
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://qz.com/feed",
    "http://feeds.foxnews.com/foxnews/politics",
    "http://feeds.reuters.com/reuters/businessNews",
    "http://feeds.feedburner.com/NewshourWorld",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
]

#Load spaCy model
nlp = spacy.load("en_core_web_sm")

#Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='qazwsx123',
        database='newsarticles'
    )
    return connection

#Celery task to classify and insert/update articles in the database
@app.task
def classify_article(article):
    logger.info(f"Processing article: {article['title']}")
    #Define keywords for classification
    categories = {
        "Terrorism / protest / political unrest / riot": [
            "terrorism", "protest", "riot", "violence", "unrest", "attack", "militant", "demonstration", "march", "civil unrest",
            "uprising", "revolt", "election", "democracy", "government", "law", "court", "legal", "lawsuit", "trial", "judge",
            "politician", "policy", "voting", "defamation", "settlement", "democrats", "republicans"
        ],
        "Positive/Uplifting": [
            "happy", "joy", "success", "celebration", "achievement", "inspiring", "good news", "uplifting", "positive", 
            "motivation", "hero", "progress", "hope", "victory", "breakthrough", "compassion", "love", "kindness", "charity", 
            "support", "peace", "recovery", "healing", "solution", "growth", "innovation", "discovery"
        ],
        "Natural Disasters": [
            "earthquake", "flood", "hurricane", "disaster", "tsunami", "wildfire", "storm", "devastation", "natural disaster", 
            "catastrophe", "landslide", "volcano", "drought", "tornado", "blizzard", "cyclone", "evacuation", "emergency", 
            "destruction", "famine", "mudslide", "tidal wave", "eruption", "fire", "global warming", "climate change", 
            "heatwave", "hazard"
        ],
        "Others": []
    }

  #Classification
    doc = nlp(article['content'].lower())
    article_category = "Others"  # Default category

    for category, keywords in categories.items():
        if any(keyword in article['content'].lower() for keyword in keywords):
            article_category = category
            break

    article['category'] = article_category
    logger.info(f"Assigned category '{article['category']}' to article: {article['title']}")

    #Insert or update article in databse
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        sql_insert_query = """INSERT INTO articles (title, content, pub_date, source_url, category) 
                              VALUES (%s, %s, %s, %s, %s) 
                              ON DUPLICATE KEY UPDATE category = VALUES(category)"""
        pub_date = parser.parse(article['pub_date']) if article['pub_date'] != 'No publication date available' else None
        cursor.execute(sql_insert_query, (article['title'], article['content'], pub_date,
                                          article['source_url'], article['category']))
        connection.commit()
        logger.info(f"Article '{article['title']}' successfully updated in the database.")
    except mysql.connector.Error as e:
        logger.error(f"Error updating database for article '{article['title']}': {e}")
    finally:
        cursor.close()
        connection.close()

    return article

# Fetch and parse RSS feeds
articles = []
for url in rss_feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        article = {
            'title': entry.get('title', 'No title available'),
            'content': entry.get('summary', entry.get('content', [{'value': 'No content available'}])[0]['value']),
            'pub_date': entry.get('published', 'No publication date available'),
            'source_url': entry.get('link', 'No source URL available')
        }
        articles.append(article)

# Remove duplicate articles based on source URL
seen_urls = set()
unique_articles = []
for article in articles:
    if article['source_url'] not in seen_urls:
        unique_articles.append(article)
        seen_urls.add(article['source_url'])

# Process articles
for article in unique_articles:
    classify_article.delay(article)  # Send the article to Celery for classification and database insertion
    
