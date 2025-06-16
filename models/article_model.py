from db import get_db_connection
from lang_config import LANGUAGE_TABLES  # Import the language configuration

class ArticleModel:
    def __init__(self):
        self.db_config = get_db_connection()  # Use db connection in an instance

    @staticmethod
    def get_all_articles(language):
        """Fetch all articles from the database based on language."""
        table_name = LANGUAGE_TABLES.get(language)  # Get the table name dynamically
        if not table_name:
            raise ValueError(f"Language '{language}' is not supported.")  # Raise error if language is not supported

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Dynamically use the correct table based on the language
            cursor.execute(f"""
                SELECT id, unique_id, news_source_url, title, slug, image_path, byline_author, article_detail, created_at, article_date, article_date_and_time
                FROM {table_name};""")
            columns = [column[0] for column in cursor.description]  # Get column names
            rows = cursor.fetchall()

            # Convert each row to a dictionary
            articles = [dict(zip(columns, row)) for row in rows]

            cursor.close()
            conn.close()
            return articles
        except Exception as e:
            print(f"Error fetching articles from {table_name}: {e}")
            return []

    @staticmethod
    def get_article_by_unique_id(unique_id, language):
        """Fetch a specific article from the database by unique_id and language."""
        table_name = LANGUAGE_TABLES.get(language)  # Get the table name dynamically
        if not table_name:
            raise ValueError(f"Language '{language}' is not supported.")  # Raise error if language is not supported

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Dynamically use the correct table based on the language
            cursor.execute(f"""
                SELECT id, title, news_source_url, unique_id, slug, image_path, byline_author, article_detail, created_at, article_date, article_date_and_time
                FROM {table_name} WHERE unique_id = %s;""",
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
            print(f"Error fetching article by unique_id from {table_name}: {e}")
            return None
