# services/article_service.py
import logging
import random
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from models.article_model import ArticleModel
from lang_config import LANGUAGE_TABLES

load_dotenv()

class ArticleService:
    def __init__(self, default_language="hindi"):
        self.articleModel = ArticleModel()
        # Load default language from environment variable if not provided
        self.default_language =default_language or os.getenv("DEFAULT_LANGUAGE", "hindi")

    def get_articles_by_date(self, datestr, language=None):
        """
        Return a list of articles published on a given date,
        sorted by article_date_and_time in ascending order.
        """
        try:
            if language is None:
                language = self.default_language

            request_date = self.validate_date(datestr)
            logging.info(f"Fetching articles for date: {request_date} and language: {language}")

            all_articles = self.articleModel.get_all_articles(language)
            filtered_sorted = self.filter_and_sort_articles(all_articles, request_date)

            logging.info(f"Found {len(filtered_sorted)} articles for date {request_date} and language {language}")
            return [self.format_article(article) for article in filtered_sorted]

        except ValueError as ve:
            logging.error(f"Date validation error: {ve}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error in get_articles_by_date: {e}")
            raise

    def get_article_by_unique_id_url(self, unique_id_url, language=None):
        """Return a specific article by unique_id_url, filtered by language."""
        try:
            if language is None:
                language = self.default_language

            logging.info(f"Fetching article by unique_id_url: {unique_id_url} and language: {language}")
            article = self.articleModel.get_article_by_unique_id_url(unique_id_url, language)
            if article:
                return self.format_article(article)
            else:
                return None
        except Exception as e:
            logging.exception(f"Unexpected error in get_article_by_unique_id_url: {e}")
            raise

    def get_articles_by_category(self, category_keyword, language=None):
        """Return articles filtered by category keyword and language."""
        try:
            if language is None:
                language = self.default_language

            logging.info(f"Filtering articles by category: {category_keyword} and language: {language}")
            all_articles = self.articleModel.get_all_articles(language)
            filtered = [
                a for a in all_articles
                if a.get("news_source_url") and category_keyword.lower() in a["news_source_url"].lower()
            ]
            sorted_articles = self.filter_and_sort_articles(filtered, None)
            return [self.format_article(article) for article in sorted_articles]
        except Exception as e:
            logging.exception(f"Error filtering articles by category '{category_keyword}' and language '{language}': {e}")
            raise

    def get_all_articles(self, language=None):
        """
        Return all articles, sorted by article_date_and_time in ascending order, filtered by language.
        """
        try:
            if language is None:
                language = self.default_language

            logging.info(f"Fetching all articles for language: {language}")
            # Fetch all articles from the model, passing the language parameter
            all_articles = self.articleModel.get_all_articles(language)
            sorted_articles = self.filter_and_sort_articles(all_articles, None)

            logging.info(f"Found {len(sorted_articles)} articles for language {language}.")
            return [self.format_article(article) for article in sorted_articles]

        except Exception as e:
            logging.exception(f"Unexpected error in get_all_articles: {e}")
            raise

    def validate_date(self, datestr):
        """Validate and convert a date string to a date object"""
        try:
            return datetime.strptime(datestr, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")

    def filter_and_sort_articles(self, articles, target_date):
        """Filter by date and sort by article_date_and_time ascending."""
        if target_date:
            # Filter by date only if a target date is provided
            filtered = [a for a in articles if a["article_date"] == target_date]
        else:
            # If no date is provided, we simply return all articles (i.e., no filtering)
            filtered = articles

        # Always sort by article_date_and_time
        return sorted(filtered, key=lambda a: a.get("article_date_and_time") or datetime.min, reverse=True)

    def save_custom_article(self, data):
        from db import get_db_connection
        import uuid
        import time
        import random

        language = data["language"]
        table_name = LANGUAGE_TABLES.get(language)
        if not table_name:
            raise ValueError(f"Unsupported language: {language}")

        conn = get_db_connection()
        cur = conn.cursor()

        # Generate UUID and unique_id_url
        unique_id = str(uuid.uuid4())
        url_tail = data["news_source_url"].split("/")[-1].rsplit("-", 1)[0]
        timestamp = int(time.time())
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        unique_id_url = f"{url_tail}-hdn{timestamp}{random_digits}"

        # Optional fields
        image_path = data.get("image_path", "")
        article_datetime = datetime.now()

        cur.execute(f"""
            INSERT INTO {table_name} 
            (news_source_url, title, slug, image_path, byline_author, article_detail, article_date, article_date_and_time, unique_id, unique_id_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """, (
            data["news_source_url"], data["title"], data["slug"], image_path,
            data["byline_author"], data["article_detail"], data["article_date"],
            article_datetime, unique_id, unique_id_url
        ))
        conn.commit()
        cur.close()
        conn.close()

        return {
            "unique_id": unique_id,
            "unique_id_url": unique_id_url,
            "title": data["title"]
        }

    def format_article(self, article):
        """Prepare the article dictionary for JSON output."""
        return {
            "id": article["id"],
            "unique_id": article["unique_id"],
            "unique_id_url": article["unique_id_url"],
            "news_source_url": article["news_source_url"],
            "title": self.clean(article["title"]),
            "slug": self.clean(article["slug"]),
            "image_path": article["image_path"],
            "byline_author": self.clean(article["byline_author"]),
            "article_detail": self.clean(article["article_detail"]),
            "created_at": self.format_date_time(article.get("created_at")),
            "article_date": str(article["article_date"]),
            "article_date_and_time": self.format_date_time(article.get("article_date_and_time"))
        }

    @staticmethod
    def clean(text):
        """Normalize whitespace and trim."""
        return re.sub(r'\s+', ' ', text).strip() if text else ''

    @staticmethod
    def format_date_time(dt):
        """Convert a datetime object to string."""
        return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None

    def latest(self, language=None, limit=6, offset=0):
        language = language or self.default_language
        rows = self.articleModel.get_latest_articles(language, limit, offset)
        return [self.format_article(r) for r in rows]

    def category(self, category_keyword, language=None, limit=8):
        language = language or self.default_language
        rows = self.articleModel.get_category_articles(language, category_keyword, limit)
        return [self.format_article(r) for r in rows]

    def trending(self, language=None, pick=5):
        language = language or self.default_language
        pool = self.articleModel.get_random_from_recent(language, recent_count=100, pick=pick)
        # sample in memory (cheap; pool is small)
        chosen = random.sample(pool, k=min(pick, len(pool)))
        return [self.format_article(r) for r in chosen]
