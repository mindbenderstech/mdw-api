# models/article_model.py
from db import get_db_connection

class ArticleModel:
    def __init__(self):
        self.db_config = get_db_connection()  # Use db connection in an instance

    @staticmethod
    def get_all_articles():
        """Fetch all articles from the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, unique_id, news_source_url, title, slug, image_path, byline_author, article_detail, created_at, article_date, article_date_and_time FROM news_articles;")
            columns = [column[0] for column in cursor.description]  # Get column names
            rows = cursor.fetchall()

            # Convert each row to a dictionary
            articles = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            print("Fetched Articles:", articles)

            return articles
        except Exception as e:
            print(f"Error fetching articles: {e}")
            return []

    @staticmethod
    def get_article_by_unique_id(unique_id):
        """Fetch a specific article from the database by unique_id."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, news_source_url, unique_id, slug, image_path, byline_author, article_detail, created_at, article_date, article_date_and_time FROM news_articles WHERE unique_id = %s;",
                (unique_id,))
            row = cursor.fetchone()

            if row:
                columns = [column[0] for column in cursor.description]  # Get column names
                article = dict(zip(columns, row))
                cursor.close()
                conn.close()
                return article
            else:
                cursor.close()
                conn.close()
                return None
        except Exception as e:
            print(f"Error fetching article by unique_id: {e}")
            return None