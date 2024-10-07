# News Classification Application

This project collects news articles from various RSS feeds, classifies them into predefined categories, and stores them in a MySQL database. The application is built using Python, Celery, and MySQL, utilizing libraries such as `feedparser` for parsing RSS feeds, `SQLAlchemy` for database interaction, and `spaCy` for Natural Language Processing (NLP) classification.

## Table of Contents
- [Project Overview](#project-overview)
- [Technologies Used](#technologies-used)
- [Installation and Setup](#installation-and-setup)
- [How to Use](#how-to-use)
- [Database Schema](#database-schema)
- [Error Handling](#error-handling)
- [Logging](#logging)
- [Celery Task Queue](#celery-task-queue)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [Conclusion](#conclusion)

## Project Overview
The News Classification Application fetches news articles from various RSS feeds, classifies them into predefined categories using Natural Language Processing (NLP), and stores them in a MySQL database. The application uses asynchronous task processing (Celery) to manage the classification and database updates in a scalable manner.

The predefined categories are:
- **Terrorism / protest / political unrest / riot**
- **Positive/Uplifting**
- **Natural Disasters**
- **Others**

Additionally, the application allows exporting articles from the database to a CSV file for reporting or analysis.

## Technologies Used
- **Python**: Core language for data processing and database interaction.
- **MySQL**: Relational database for storing articles.
- **Celery**: Task queue to handle asynchronous classification.
- **Redis**: Message broker for Celery tasks.
- **feedparser**: Library for parsing RSS feeds.
- **spaCy**: NLP library for text classification.
- **MySQL Connector**: For connecting Python with MySQL.

## Installation and Setup

### Prerequisites
- Python 3.x
- MySQL Server
- Redis (for Celery)
- pip (Python package manager)

### Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd news-classification-app

2. **Install Required Dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Set Up MySQL Database**:
    ```sql
    CREATE DATABASE newsarticles;
    USE newsarticles;
    CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    pub_date DATETIME,
    source_url VARCHAR(255),
    category VARCHAR(100),
    UNIQUE KEY unique_article (title)
    );

4. **Run Redis Server**:
    ```bash
    redis-server

5. **Start the Celery Worker**:
    ```bash
    celery -A main worker --loglevel=info

## How to Use

1. **Run the Main Application**:
    Execute the main Python script to fetch and classify articles from the specified RSS feeds.
    ```bash
    python main.py

2. **Export to CSV**

## Database Schema

The database consists of a single table articles with the following structure:

```sql
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    pub_date DATETIME,
    source_url VARCHAR(255),
    category VARCHAR(100),
    UNIQUE KEY unique_article (title)
);
```
## Error Handling

The application implements basic error handling for database connections and data parsing. Errors are logged for review and debugging.

## Logging

Logging is configured to capture all significant events and errors. Logs are stored in tasks.log.

##Celery Task Queue

Celery is used to manage the classification of articles asynchronously. Articles are sent to the Celery worker for processing.

## Testing

Test the application by running the main script and verifying that articles are fetched, classified, and stored correctly in the MySQL database.

## Future Improvements

1. Enhance the classification logic with more sophisticated machine learning models.
2. Implement a web interface for easier interaction with the application.
3. Add support for more RSS feeds and additional categories.

## Conclusion

The News Classification Application serves as a robust solution for automating the collection and classification of news articles. By utilizing a combination of Python, MySQL, and Celery, it efficiently processes and stores data while allowing for easy access and analysis.
