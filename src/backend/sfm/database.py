from sqlmodel import SQLModel, Session, create_engine
import os
import config
import logging

# This is the Database Connection for Azure
# server = ''
# database = ''
# username = ''
# password = ''
# driver= '{ODBC Driver 17 for SQL Server}'

# SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-key'
# SQL_SERVER = os.environ.get('SQL_SERVER') or server
# SQL_DATABASE = os.environ.get('SQL_DATABASE') or database
# SQL_USER_NAME = os.environ.get('SQL_USER_NAME') or username
# SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or password
# SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://' + SQL_USER_NAME + '@' + SQL_SERVER + ':' + SQL_PASSWORD + '@' + SQL_SERVER + ':1433/' + SQL_DATABASE + '?driver=ODBC+Driver+17+for+SQL+Server'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(levelname)s %(name)s %(asctime)s %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = config.DATABASE_URL
assert DATABASE_URL != ""

# check_same_thread = false only works in sqlite, not postgres or others
if "sqlite" in DATABASE_URL:
    print("Using a sqlite database")
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    logger.info('func="create_db_and_tables" info="Database created"')
    SQLModel.metadata.create_all(engine)
