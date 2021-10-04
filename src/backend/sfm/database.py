from sqlmodel import SQLModel, Session, create_engine

import os
import config
import logging
import pyodbc
import urllib

# SECRET_KEY = os.environ("SECRET_KEY")
# server = os.environ["DBHOST"]
# database = os.environ["DBNAME"]
# user = os.environ["DBUSER"]
# password = os.environ["DBPASS"]
# driver = "{ODBC Driver 17 for SQL Server}"

# Uncomment this line for local dev in sqlite
conn_str = "sqlite:///./issues.db"

# conn = f"""Driver={driver};Server=tcp:{server},1433;Database={database};Uid={user};Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""
# params = urllib.parse.quote_plus(conn)
# conn_str = "mssql+pyodbc:///?autocommit=true&odbc_connect={}".format(params)

# # check_same_thread = false only works in sqlite, not postgres or others
if "sqlite" in conn_str:
    print("Using a sqlite database")
    connect_args = {"check_same_thread": False}
    engine = create_engine(conn_str, connect_args=connect_args)
else:
    engine = create_engine(conn_str, echo=True)

# logging.basicConfig(
#     filename="logs.log",
#     level=logging.DEBUG,
#     format="%(levelname)s %(name)s %(asctime)s %(message)s",
# )
# logger = logging.getLogger(__name__)


def create_db_and_tables():
    # logger.info('func="create_db_and_tables" info="Database created"')
    SQLModel.metadata.create_all(engine)
