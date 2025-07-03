# services/article_service.py
import logging
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from models.article_model import ArticleModel

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
