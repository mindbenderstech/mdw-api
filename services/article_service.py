import logging
import re
from datetime import datetime
from models.article_model import ArticleModel


class ArticleService:
    def __init__(self):
        self.articleModel = ArticleModel()

    def get_articles_by_date(self, datestr):
        """
        Return a list of articles published on a given date,
        sorted by article_date_and_time in ascending order.
        """
        try:
            request_date = self.validate_date(datestr)
            logging.info(f"Fetching articles for date: {request_date}")

            all_articles = self.articleModel.get_all_articles()
            filtered_sorted = self.filter_and_sort_articles(all_articles, request_date)

            logging.info(f"Found {len(filtered_sorted)} articles for date {request_date}")
            return [self.format_article(article) for article in filtered_sorted]

        except ValueError as ve:
            logging.error(f"Date validation error: {ve}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error in getArticlesByDate: {e}")
            raise

    def get_article_by_unique_id(self, unique_id):
        """Return a specific article by unique_id."""
        try:
            logging.info(f"Fetching article by unique_id: {unique_id}")
            article = self.articleModel.get_article_by_unique_id(unique_id)
            if article:
                return self.format_article(article)
            else:
                return None
        except Exception as e:
            logging.exception(f"Unexpected error in getArticleByUniqueId: {e}")
            raise

    def get_articles_by_category(self, category_keyword):
        """Return articles where the source URL contains the given category keyword"""
        try:
            logging.info(f"Filtering articles by category: {category_keyword}")
            all_articles = self.articleModel.get_all_articles()
            filtered = [
                a for a in all_articles
                if a.get("news_source_url") and category_keyword.lower() in a["news_source_url"].lower()
            ]
            sorted_articles = self.filter_and_sort_articles(filtered, None)
            return [self.format_article(article) for article in sorted_articles]
        except Exception as e:
            logging.exception(f"Error filtering articles by category '{category_keyword}': {e}")
            raise

    def get_all_articles(self):
        """
        Return all articles, sorted by article_date_and_time in ascending order.
        """
        try:
            logging.info("Fetching all articles")
            # Fetch all articles without filtering by date
            all_articles = self.articleModel.get_all_articles()
            sorted_articles = self.filter_and_sort_articles(all_articles, None)

            logging.info(f"Found {len(sorted_articles)} articles.")
            return [self.format_article(article) for article in sorted_articles]

        except Exception as e:
            logging.exception("Unexpected error in getAllArticles: {e}")
            raise

    def validate_date(self, datestr):
        """Validate and convert a date string to a date object"""
        try:
            return datetime.strptime(datestr, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Invalid date format. Use 'YYYY-MM-DD'.")

    def filter_and_sort_articles(self, articles, target_date):
        """Filter by date and sort by article_date_and_time ascending"""
        if target_date:
            # Filter by date only if a target date is provided
            filtered = [a for a in articles if a["article_date"] == target_date]
        else:
            # If no date is provided, we simply return all articles (i.e., no filtering)
            filtered = articles

        # Always sort by article_date_and_time
        return sorted(filtered, key=lambda a: a.get("article_date_and_time") or datetime.min, reverse=True)

    def format_article(self, article):
        """Prepare the article dictionary for JSON output"""
        return {
            "id": article["id"],
            "unique_id": article["unique_id"],
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
        """Normalize whitespace and trim"""
        return re.sub(r'\s+', ' ', text).strip() if text else ''

    @staticmethod
    def format_date_time(dt):
        """Convert a datetime object to string"""
        return dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None
