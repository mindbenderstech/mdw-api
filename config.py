# config.py

import os

class Config:
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:1234@localhost/news_db'

    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@host.docker.internal/news_db'

    # SQLALCHEMY_DATABASE_URI= 'postgresql://postgres:d:JA9hNPoR5ZH97lCnh)GoSRg<G<@news-website-postgres.cv4ocsocwxy0.ap-south-1.rds.amazonaws.com:5432/postgres'

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Mindbenderstech020305@headliness-mdw-postgres.cv4ocsocwxy0.ap-south-1.rds.amazonaws.com:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
