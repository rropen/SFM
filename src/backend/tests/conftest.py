from enum import auto
import pytest
import os
import datetime
from passlib.context import CryptContext
from sqlalchemy.sql.roles import StatementOptionRole
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sfm.main import app
from sfm.dependencies import get_db

from sfm.models import WorkItem, Project, Commit


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
token1 = "Catalyst1"
token2 = "Catalyst2"
hashed_token1 = pwd_context.hash(token1)
hashed_token2 = pwd_context.hash(token2)


@pytest.fixture(scope="function", name="db")
def init_database(session):

    """
    Add document types to the database
    """

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
            "project_auth_token_hashed": hashed_token1,
        }
    )
    proj2 = Project(
        **{
            "name": "Test Project 2",
            "lead_name": "Sergio Garcia",
            "lead_email": "team-europe@pga.com",
            "description": "A second test project for testing",
            "location": "Kohler",
            "repo_url": "github.com/pgaGolf",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token2,
        }
    )

    session.add(proj1)
    session.add(proj2)
    session.commit()

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

    session.add(work_item1)
    session.commit()

    work_item2 = WorkItem(
        **{
            "category": "Pull Request",
            "start_time": datetime.datetime(2021, 7, 23, 9, 37, 17, 94309),
            "end_time": datetime.datetime(2021, 8, 23, 9, 37, 17, 94309),
            "duration_open": datetime.timedelta(days=31),
            "comments": "new Test description for test work item in the database",
            "project_id": 2,
        }
    )

    session.add(work_item2)
    session.commit()

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

    session.add(commit1)
    session.commit()

    yield session
