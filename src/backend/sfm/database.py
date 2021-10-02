from sqlmodel import SQLModel, Session, create_engine
import os
import config
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import pyodbc
import urllib
from .config import get_settings

app_settings = get_settings()

# check_same_thread = false only works in sqlite, not postgres or others
if "sqlite" in app_settings.CONN_STR:
    # print("Using a sqlite database")
    connect_args = {"check_same_thread": False}
    engine = create_engine(app_settings.CONN_STR, connect_args=connect_args)
else:
    engine = create_engine(app_settings.CONN_STR, echo=True)

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(levelname)s %(name)s %(asctime)s %(message)s",
)
logger = logging.getLogger(__name__)
# logger.addHandler(AzureLogHandler(connection_string=app_settings.AZURELOGGING_CONN_STR))


def create_db_and_tables():
    logger.info('func="create_db_and_tables" info="Database created"')
    SQLModel.metadata.create_all(engine)
