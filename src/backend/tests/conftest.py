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
from sfm.config import Settings, get_settings
from sfm.models import WorkItem, Project, Commit, ProjectCreate, WorkItemCreate


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

    def get_settings_override():
        return Settings(
            APP_NAME="sfm",
            ENV="test",
            DEBUG=False,
            TESTING=True,
            SECRET_KEY="secret_key",
        )

    app.dependency_overrides[get_db] = get_session_override
    app.dependency_overrides[get_settings] = get_settings_override

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
    empty_proj = Project(
        **{
            "name": "Test Project with no WorkItems",
            "lead_name": "Sergio Manuel",
            "lead_email": "team-europe@pga.com",
            "description": "A third test project for testing",
            "location": "Kohler",
            "repo_url": "github.com/pgaGolf",
            "on_prem": False,
            "project_auth_token_hashed": hashed_token2,
        }
    )

    session.add(proj1)
    session.add(proj2)
    session.add(empty_proj)
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

    # time_shift = datetime.timedelta(days=32)
    time_shift = datetime.datetime.now().date() - datetime.datetime(2021, 8, 19).date()

    # Creates the deployment items:
    dates = [
        datetime.datetime(2021, 5, 31),  # Week 1
        datetime.datetime(2021, 6, 7),  # Week 2
        datetime.datetime(2021, 6, 12),
        datetime.datetime(2021, 6, 14),  # Week 3
        datetime.datetime(2021, 6, 16),
        datetime.datetime(2021, 6, 18),
        datetime.datetime(2021, 6, 21),  # Week 4
        datetime.datetime(2021, 6, 22),
        datetime.datetime(2021, 6, 25),
        datetime.datetime(2021, 6, 26),
        datetime.datetime(2021, 6, 28),  # Week 5
        datetime.datetime(2021, 6, 29),
        datetime.datetime(2021, 6, 30),
        datetime.datetime(2021, 7, 5),  # Week 6
        datetime.datetime(2021, 7, 8),
        datetime.datetime(2021, 7, 12),  # Week 7
        datetime.datetime(2021, 7, 14),
        datetime.datetime(2021, 7, 16),
        datetime.datetime(2021, 7, 19),  # Week 8
        datetime.datetime(2021, 7, 21),
        datetime.datetime(2021, 7, 26),  # Week 9
        datetime.datetime(2021, 7, 27),
        datetime.datetime(2021, 7, 29),
        datetime.datetime(2021, 7, 30),
        datetime.datetime(2021, 8, 2),  # Week 10
        datetime.datetime(2021, 8, 9),  # Week 11
        datetime.datetime(2021, 8, 11),
        datetime.datetime(2021, 8, 11),  # purposeful duplicate day
        datetime.datetime(2021, 8, 12),
        datetime.datetime(2021, 8, 13),
        datetime.datetime(2021, 8, 16),  # Week 12
        datetime.datetime(2021, 8, 18),
        datetime.datetime(2021, 8, 19),
    ]

    for date in dates:
        deployment_dict = {
            "category": "Deployment",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": 1,
        }

        work_item_data = WorkItem(**deployment_dict)
        session.add(work_item_data)
    session.commit()

    # Creates the deployment items:
    dates2 = [
        datetime.datetime(2021, 5, 31),  # Week 1
        datetime.datetime(2021, 6, 7),  # Week 2
        datetime.datetime(2021, 8, 4),  # Week 10
        datetime.datetime(2021, 8, 10),  # Week 11
        datetime.datetime(2021, 8, 11),
        datetime.datetime(2021, 8, 16),  # Week 12
    ]

    for date in dates2:
        deployment_dict = {
            "category": "Deployment",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": 2,
        }

        work_item_data = WorkItem(**deployment_dict)
        session.add(work_item_data)
    session.commit()

    # Create Pull Request Items
    pull_dates = [
        datetime.datetime(2021, 8, 11),
        datetime.datetime(2021, 8, 19),
    ]

    pull_req_work_items = []
    work_items = []
    project_ids = [1, 2]
    proj_iter = 0
    for date in pull_dates:
        pull_dict = {
            "category": "Pull Request",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": project_ids[proj_iter],
        }

        work_item_data = WorkItem(**pull_dict)
        work_items.append(work_item_data)
        proj_iter += 1

    session.add_all(work_items)
    session.commit()
    for work_item_sing in work_items:
        session.refresh(work_item_sing)
        pull_req_work_items.append(work_item_sing.id)

    commit_dates = [
        datetime.datetime(2021, 8, 8),
        datetime.datetime(2021, 8, 9),
        datetime.datetime(2021, 8, 10),
        datetime.datetime(2021, 8, 11),
    ]

    i = 0
    proj_iter = 0
    for item_id in pull_req_work_items:
        for date in commit_dates:
            commit_dict = {
                "sha": i,  # not representative of actual sha sting
                "date": date + time_shift,
                "author": "Gabe Geiger",
                "work_item_id": item_id,
                "time_to_pull": (proj_iter + i)
                * 1000,  # not representative of acutal time to pull
            }

            commit_data = Commit(**commit_dict)
            session.add(commit_data)
            i += 1
    proj_iter += 1

    session.commit()

    yield session
