from enum import auto
import pytest
import os
import datetime
from passlib.context import CryptContext
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sfm.main import app
from sfm.routes.projects.routes import get_db

from sfm.models import WorkItem, Project, Commit


DATABASE_URL = "sqlite:///./test.db"
connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
# engine = create_engine(DATABASE_URL)


@pytest.fixture(scope="function")
def test_app(init_database):
    app.dependency_overrides[get_db] = init_database
    client = TestClient(app)
    print(os.listdir("."))
    if "issues.db" in os.listdir("."):
        os.remove("issues.db")
    yield client


@pytest.fixture(scope="session")
def db():
    """Session-wide test database"""

    SQLModel.metadata.create_all(engine)
    _db = Session(engine)

    yield _db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token = "Catalyst"
hashed_token = pwd_context.hash(token)


@pytest.fixture(scope="function")
def init_database():

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    _db = Session(autocommit=False, autoflush=False, bind=engine)

    """
    Add document types to the database
    """

    # [create project here]
    proj1 = Project(
        **{
            "name": "Test Project 1",
            "leadName": "Peter Parker",
            "leadEmail": "spider-person@stark.com",
            "description": "A test project for testing",
            "location": "Strangeville",
            "repoUrl": "github.com/starkEnterprises",
            "onPrem": False,
            "projectAuthTokenHashed": hashed_token,
        }
    )

    _db.add(proj1)
    _db.commit()

    # [create work_items here]
    work_item1 = WorkItem(
        **{
            "category": "Deployment",
            "startTime": datetime.datetime(2021, 8, 23, 9, 37, 17, 94309),
            "endTime": datetime.datetime(2021, 9, 23, 9, 37, 17, 94309),
            "durationOpen": datetime.timedelta(days=31),
            "comments": "Test description for test work item in the database",
            "projectId": 1,
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
            "workItemId": 1,
            "timeToPull": int(
                (
                    datetime.timedelta(days=12, seconds=86049, microseconds=52958)
                ).total_seconds()
            ),
        }
    )

    _db.add(commit1)
    _db.commit()

    yield _db
