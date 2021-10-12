from pydantic import BaseSettings
import os
from dotenv import load_dotenv
import urllib
from functools import lru_cache
import psycopg2

load_dotenv()


class Settings(BaseSettings):
    """
    App settings class.  These values should be exposed as environment variables.  If running locally, this can be a `.env` file (see included `.env.example` file).  If running in another enviornment you should use a modern approach to manage secrets.  Many of these values are secrets and should not be exposed in the source code or to a user of the application.  Many settings and decisions are based on the `ENV` variable's value.

    APP_NAME: name of the app hard-coded here
    ENV: Marker of the environment.  acceptable values are test, local, development, and production
    DEBUG: Boolean on whether debugging log messages should be visible.
    TESTING: Boolean on whether you are running unit or integration tests.  Among other things, this will drive an in-memory database to be used.
    SECRET_KEY: Long random string of characters to use in hashing and encryption.  Don't expose this value.
    ADMIN_KEY: Long string that will set the admin key used to generate new project keys.
    FRONTEND_URL: Location from which API requests will be made by the frontend.  This will need refactored if we start to have other tools using this API.
    GITHUB_API_TOKEN: Token used for authentication with Github to increase rate limit of API calls
    DBHOST: Hostname for a database used in building a connection string
    DBNAME: Database name used in building a connection string
    DBUSER: Username used in building a connection string
    DBPASS: User's Password used in building a connection string
    AZURELOGGING_CONN_STR: Connection string to azure log handler
    """

    APP_NAME: str = "sfm"
    # dev or test
    ENV: str = os.environ.get("ENV") or "test"
    DEBUG: bool = (os.environ.get("DEBUG", "False") == "True") or False
    TESTING: bool = os.environ.get("TESTING", "False") == "True"
    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "unset"
    ADMIN_KEY: str = os.environ.get("ADMIN_KEY") or "unset"
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL") or "unset"
    GITHUB_API_TOKEN: str = os.environ.get("GITHUB_API_TOKEN") or "unset"
    DBHOST: str = os.environ.get("DBHOST") or "unset"
    DBNAME: str = os.environ.get("DBNAME") or "unset"
    DBUSER: str = os.environ.get("DBUSER") or "unset"
    DBPASS: str = os.environ.get("DBPASS") or "unset"
    AZURE_LOGGING_CONN_STR: str = os.environ.get("AZURE_LOGGING_CONN_STR") or "unset"


#     CONN_STR: str = generate_db_string(ENV, DBHOST, DBNAME, DBUSER, DBPASS)


@lru_cache()
def get_settings() -> Settings:
    return Settings()  # reads environment variables
