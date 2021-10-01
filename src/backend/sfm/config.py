from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    APP_NAME: str = "sfm"
    # DEBUG: str =
    # WTF_CSRF_ENABLED
    # TESTING: str = os.environ.get("TESTING") or False
    ENV: str = os.environ.get("ENV") or "unset"
    # SQLALCHEMY_DATABASE_URI: str = os.environ.get("SQLALCHEMY_DATABASE_URI") or ""
    SECRET_KEY: str = os.environ.get("") or ""
    # SQLALCHEMY_TRACK_MODIFICATIONS: str =
    # DBHOST: str = os.environ.get("") or ""
    # DBNAME: str = os.environ.get("") or ""
    # DBUSER: str = os.environ.get("") or ""
    # DBPASS: str = os.environ.get("") or ""
