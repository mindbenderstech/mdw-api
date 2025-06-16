# config.py

import os

class Config:

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Mindbenderstech020305@headliness-mdw-postgres.cv4ocsocwxy0.ap-south-1.rds.amazonaws.com:5432/postgres"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
