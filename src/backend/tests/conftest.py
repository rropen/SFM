from typing import AsyncIterable
import pytest
from sqlmodel import SQLModel, create_engine, Session
from starlette.testclient import TestClient
from sqlalchemy.engine import Engine as Database
from sqlalchemy_utils import database_exists, drop_database, create_database

from sfm.main import app
from sfm.routes.utilities import routes as utilities

from sfm.models import *

DATABASE_URL = "sqlite:///./test.db"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)


def get_test_db_conn() -> Database:
    assert engine is not None
    return engine


def get_test_db() -> AsyncIterable[Session]:
    sess = Session(bind=engine)

    try:
        yield sess
    finally:
        sess.close()


@pytest.fixture(scope="module", autouse=True)
def setup_database():

    if database_exists(DATABASE_URL):
        drop_database(DATABASE_URL)

    SQLModel.metadata.create_all(engine)

    app.dependency_overrides[utilities.get_db] = get_test_db

    client = TestClient(app)
    client.post("/utilities/populate_mock_data")

    drop_database(DATABASE_URL)


@pytest.yield_fixture
def test_db_session():
    """Returns an sqlalchemy session, and after the test tears down everything properly."""

    session = Session(bind=engine)

    yield session
    # Drop all data after each test
    for tbl in reversed(SQLModel.metadata.sorted_tables):
        engine.execute(tbl.delete())
    # put back the connection to the connection pool
    session.close()


# Creates a new connection
@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client
