import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_ENV = os.getenv("FLASK_ENV")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST")
    FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT")
    SERVER_NAME = os.getenv("SERVER_NAME") if os.getenv("SERVER_NAME") else None
    DEBUG = bool(os.getenv("DEBUG"))
    PROPAGATE_EXCEPTIONS = True

    # MySQL configuration
    MYSQL_DATABASE_USER = os.getenv("MYSQL_DATABASE_USER")
    MYSQL_DATABASE_PASSWORD = os.getenv("MYSQL_DATABASE_PASSWORD")
    MYSQL_DATABASE_DB = os.getenv("MYSQL_DATABASE_DB")
    MYSQL_DATABASE_HOST = os.getenv("MYSQL_DATABASE_HOST")

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI")
        if os.getenv("SQLALCHEMY_DATABASE_URI")
        else f"mysql+pymysql://{MYSQL_DATABASE_USER}:{MYSQL_DATABASE_PASSWORD}@{MYSQL_DATABASE_HOST}/{MYSQL_DATABASE_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = bool(os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"))

    # JWT configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES")))

    # Other configurations
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH"))
    STORAGE_TYPE = os.getenv("STORAGE_TYPE")
    STORAGE_PATH = os.getenv("STORAGE_PATH")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")