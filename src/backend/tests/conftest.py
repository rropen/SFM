from typing import AsyncIterable
import pytest
from sqlmodel import SQLModel, create_engine, Session
from starlette.testclient import TestClient
from sqlalchemy.engine import Engine as Database

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


@pytest.fixture(scope="session", autouse=True)
def setup_database():

    SQLModel.metadata.create_all(engine)

    # client = TestClient(app)
    # client.post("/utilities/populate_mock_data")
    # utilities.populate_db(Session(engine))


# Creates a new connection
@pytest.fixture(scope="module")
def test_app():
    client = TestClient(app)
    yield client
