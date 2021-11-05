from sqlmodel import SQLModel, Session, create_engine
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.logger import create_logger
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
        conn = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
            DBHOST, DBUSER, DBNAME, DBPASS, "require"
        )
        conn = f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}"

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
if "sqlite" in CONN_STR:
    print("Using a sqlite database")
    connect_args = {"check_same_thread": False}
    engine = create_engine(CONN_STR, connect_args=connect_args)
else:
    engine = create_engine(CONN_STR, echo=False)


logger = create_logger(__name__)


def create_db_and_tables():
    logger.info('func="create_db_and_tables" info="before table create"')
    SQLModel.metadata.create_all(engine)
    logger.info('func="create_db_and_tables" info="after table create"')
