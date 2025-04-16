# db.py
import psycopg2
import psycopg2.extras
from config import Config

def get_db_connection():
    """Create a database connection with DictCursor."""
    conn = psycopg2.connect(
        Config.SQLALCHEMY_DATABASE_URI,
        cursor_factory=psycopg2.extras.DictCursor  # 👈 This makes row access by name
    )
    return conn
