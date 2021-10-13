from sqlmodel import SQLModel, Session, create_engine
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from sfm.config import get_settings
import psycopg2


def generate_db_string(ENV: str, DBHOST: str, DBNAME: str, DBUSER: str, DBPASS: str):
    """Take in env variables and generate correct db string."""

    if ENV == "test":
        return "sqlite://"  # in-memory database for unit tests

    if ENV == "local":
        return "sqlite:///./issues.db"  # local sqlite for local development

    if ENV == "development" or "production":
        # need all four parameters available
        if "unset" in [DBNAME, DBPASS]:
            raise ValueError(
                "Missing database parameter in the environment.  Please specify DBHOST, DBNAME, DBUSER, and DBPASS"
            )

        # driver = "{ODBC Driver 17 for SQL Server}"
        # conn = f"""dbname='{DBNAME}' user='sfadmin@psql-sfm' host='psql-sfm.postgres.database.usgovcloudapi.net'
        # password='{DBPASS}' port='5432' sslmode='true'"""
        conn = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
            DBHOST, DBUSER, DBNAME, DBPASS, "require"
        )
        conn = f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}"

        # conn = f"""Driver={driver};Server=tcp:{DBHOST},1433;Database={DBNAME};
        # Uid={DBUSER};Pwd={DBPASS};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"""
        # params = urllib.parse.quote_plus(conn)
        # conn_str = psycopg2.connect(conn)

        # return conn
        return conn


app_settings = get_settings()
CONN_STR = generate_db_string(
    app_settings.ENV,
    app_settings.DBHOST,
    app_settings.DBNAME,
    app_settings.DBUSER,
    app_settings.DBPASS,
)

# check_same_thread = false only works in sqlite, not postgres or others
# if "sqlite" in CONN_STR:
#    # print("Using a sqlite database")
#    connect_args = {"check_same_thread": False}
#    engine = create_engine(CONN_STR, connect_args=connect_args)
# else:
engine = create_engine(CONN_STR, echo=False)

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(levelname)s %(name)s %(asctime)s %(message)s",
)
logger = logging.getLogger(__name__)
# logger.addHandler(AzureLogHandler(connection_string=app_settings.AZURE_LOGGING_CONN_STR))


def create_db_and_tables():
    logger.info('func="create_db_and_tables" info="before table create"')
    SQLModel.metadata.create_all(engine)
    logger.info('func="create_db_and_tables" info="after table create"')
