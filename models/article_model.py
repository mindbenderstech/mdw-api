# models/article_model.py
from db import get_db_connection

class ArticleModel:
    def __init__(self):
        self.db_config = get_db_connection()  # Use db connection in instance

    @staticmethod
    def get_all_articles():
        """Fetch all articles from the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, slug, image_path, byline_author, article_detail, created_at, article_date, article_date_and_time FROM news_articles;")
            articles = cursor.fetchall()
            cursor.close()
            conn.close()
            return articles
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []
