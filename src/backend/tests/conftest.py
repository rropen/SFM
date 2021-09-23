from typing import AsyncIterable
import pytest
import os
import datetime
from sqlmodel import SQLModel, create_engine, Session
from starlette.testclient import TestClient

from sfm.main import app
from sfm.routes.utilities import routes as utilities

from sfm.models import WorkItem, Project, Commit

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "sqlite:///:memory"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    os.remove("issues.db")
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
    work_item1 = WorkItem(
        **{
            "category": "Deployment",
            "start_time": datetime.datetime(2021, 8, 23, 9, 37, 17, 94309),
            "end_time": datetime.datetime(2021, 9, 23, 9, 37, 17, 94309),
            "duration_open": datetime.timedelta(days=31),
            "comments": "Test description for test work item in the database",
            "project_id": 1,
        }
    )

    _db.add(work_item1)
    _db.commit()

    # [Creat Commit model here]
    commit1 = Commit(
        **{
            "sha": "daffasdfsjfoie3039j33j882ji2jhsdaf",
            "date": datetime.datetime(2021, 9, 10, 9, 43, 8, 41351),
            "message": "feat(test): test commit message for testing commit",
            "author": "Spider-boy",
            "work_item_id": 1,
            "time_to_pull": int(
                (
                    datetime.timedelta(days=12, seconds=86049, microseconds=52958)
                ).total_seconds()
            ),
        }
    )

    _db.add(commit1)
    _db.commit()

    yield _db
