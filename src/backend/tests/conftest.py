from typing import AsyncIterable
import pytest
import os
import sqlalchemy
from sqlmodel import SQLModel, create_engine, Session
from starlette.testclient import TestClient

from sfm.main import app
from sfm.routes.utilities import routes as utilities

from sfm.models import WorkItem, Project

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "sqlite:///:memory"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    yield client


@pytest.fixture(scope="session")
def db(test_app, request):
    """Session-wide test database"""

    SQLModel.metadata.create_all(engine)
    _db = Session(engine)

    yield _db


@pytest.fixture(scope="function")
def init_database():

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    _db = Session(engine)

    """
    Add document types to the database
    """
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    token = "Catalyst"
    hashed_token = pwd_context.hash(token)

    # [create project here]
    proj1 = Project(
        **{
            "name": "Test Project 1",
            "lead_name": "Peter Parker",
            "lead_email": "spider-person@stark.com",
            "description": "A test project for testing",
            "location": "Strangeville",
            "repo_url": "github.com/starkEnterprises",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token,
        }
    )
    _db.add(proj1)
    _db.commit()

    # [create work_items here]

    work_item1 = WorkItem(**{"category": "Deployment", "project_id": 1})
    _db.add(work_item1)
    _db.commit()

    yield _db
