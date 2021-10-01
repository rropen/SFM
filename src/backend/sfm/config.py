from pydantic import BaseSettings
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str = "sfm"
    ENV: str = os.environ.get("ENV") or "unset"
    DEBUG: bool = os.environ.get("DEBUG", "False") == "True"
    TESTING: bool = os.environ.get("TESTING", "False") == "True"
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "unset"
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL") or "unset"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") == "True"
    )
    DBHOST: str = os.environ.get("DBHOST") or "unset"
    DBNAME: str = os.environ.get("DBNAME") or "unset"
    DBUSER: str = os.environ.get("DBUSER") or "unset"
    DBPASS: str = os.environ.get("DBPASS") or "unset"
