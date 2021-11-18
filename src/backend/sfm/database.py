from sqlmodel import SQLModel, create_engine
from sqlalchemy.orm import sessionmaker
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.logger import create_logger
from sfm.config import get_settings
import psycopg2


# def generate_db_string(ENV: str, DBHOST: str, DBNAME: str, DBUSER: str, DBPASS: str):
#     """Take in env variables and generate correct db string."""

#     # if ENV == "test":
#     #     return "sqlite://"  # in-memory database for unit tests

#     if ENV == "local":
#         return "postgres+asyncpg://postgres:postgres@db:5432/sfm"  # local sqlite for local development

#     if ENV == "development" or "production":
#         # need all four parameters available
#         if "unset" in [DBNAME, DBPASS]:
#             raise ValueError(
#                 "Missing database parameter in the environment.  Please specify DBHOST, DBNAME, DBUSER, and DBPASS"
#             )
#         conn = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(
#             DBHOST, DBUSER, DBNAME, DBPASS, "require"
#         )
#         conn = f"postgresql+asyncpg://{DBUSER}:{DBPASS}@{DBHOST}/{DBNAME}"

#         # return conn
#         return conn


app_settings = get_settings()
# CONN_STR = generate_db_string(
#     app_settings.ENV,
#     app_settings.DBHOST,
#     app_settings.DBNAME,
#     app_settings.DBUSER,
#     app_settings.DBPASS,
# )

# check_same_thread = false only works in sqlite, not postgres or others
# if "sqlite" in CONN_STR:
#     # print("Using a sqlite database")
#     connect_args = {"check_same_thread": False}
#     engine = create_engine(CONN_STR, connect_args=connect_args)
# else:
logger = create_logger(__name__)

engine = create_engine(app_settings.DATABASE_URL, echo=False)

# async def init_db():
#     async with engine.begin() as conn:
#         # await conn.run_sync(SQLModel.metadata.drop_all)
#         await conn.run_sync(SQLModel.metadata.create_all)
#         logger.info("Database tables have been created")


# async def get_session() -> AsyncSession:
#     async_session = sessionmaker(
#         engine, class_=AsyncSession, expire_on_commit=False
#     )
#     async with async_session() as session:
#         yield session


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)
