from time import time
from sqlalchemy.sql.expression import false
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
from sfm.routes.commits import crud as commit_crud
from sfm.dependencies import get_db
from sfm.models import WorkItemCreate, ProjectCreate, CommitCreate
from typing import List, Optional
from sqlmodel import SQLModel, Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header
from sfm.database import engine
from datetime import datetime, timedelta
from sfm.utils import create_project_auth_token
import string
import random


def random_sha(seed):
    N = 20
    random.seed(a=seed)
    res = "".join(random.choices(string.ascii_uppercase + string.digits, k=N))
    return res


router = APIRouter()


@router.post("/populate_mock_data")
def populate_db(
    db: Session = Depends(get_db),
):
    """
    ## Populate Local Database to house Mock Data

    Calling this endpoint creates a database at SFM/src/backend/sfm/issues.db. This database is set in .env and created in database.py. Sample work items, projects, and commits are generated to be used in metrics testing. A date offset can be manually set on the mock data to allow the dates of the data to be shifted nearer the current date for a more realistic mock data set.

    """

    time_shift = timedelta(days=32)

    # fIRST PROJECT: Create project to file deployments under:
    project_dict = {
        "name": "Project for Deployments Testing",
        "lead_name": "Gabe",
        "description": "Project to hold deployment frequency data for local testing",
        "location": "Indianapolis",
        "repo_url": "a_sample_url",
        "on_prem": False,
    }

    proj_data = ProjectCreate(**project_dict)
    [project, project_auth_token] = proj_crud.create_project(
        db, proj_data, admin_key="admin_key"
    )

    # Creates the deployment items:
    dates = [
        datetime(2021, 5, 31),  # Week 1
        datetime(2021, 6, 7),  # Week 2
        datetime(2021, 6, 12),
        datetime(2021, 6, 14),  # Week 3
        datetime(2021, 6, 16),
        datetime(2021, 6, 18),
        datetime(2021, 6, 21),  # Week 4
        datetime(2021, 6, 22),
        datetime(2021, 6, 25),
        datetime(2021, 6, 26),
        datetime(2021, 6, 28),  # Week 5
        datetime(2021, 6, 29),
        datetime(2021, 6, 30),
        datetime(2021, 7, 5),  # Week 6
        datetime(2021, 7, 8),
        datetime(2021, 7, 12),  # Week 7
        datetime(2021, 7, 14),
        datetime(2021, 7, 16),
        datetime(2021, 7, 19),  # Week 8
        datetime(2021, 7, 21),
        datetime(2021, 7, 26),  # Week 9
        datetime(2021, 7, 27),
        datetime(2021, 7, 29),
        datetime(2021, 7, 30),
        datetime(2021, 8, 2),  # Week 10
        datetime(2021, 8, 9),  # Week 11
        datetime(2021, 8, 11),
        datetime(2021, 8, 11),  # purposeful duplicate day
        datetime(2021, 8, 12),
        datetime(2021, 8, 13),
        datetime(2021, 8, 16),  # Week 12
        datetime(2021, 8, 18),
        datetime(2021, 8, 19),
    ]

    for date in dates:
        deployment_dict = {
            "category": "Deployment",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": project.id,
        }

        work_item_data = WorkItemCreate(**deployment_dict)
        crud.create_work_item(db, work_item_data, project_auth_token)

    # SECOND PROJECT
    project_dict2 = {
        "name": "2nd Project for testing",
        "lead_name": "Gabe",
        "description": "Second project",
        "location": "Indianapolis",
        "repo_url": "a_different_sample_url",
        "on_prem": False,
    }

    proj_data2 = ProjectCreate(**project_dict2)
    [project2, project_auth_token2] = proj_crud.create_project(
        db, proj_data2, admin_key="admin_key"
    )

    # Creates the deployment items:
    dates2 = [
        datetime(2021, 5, 31),  # Week 1
        datetime(2021, 6, 7),  # Week 2
        datetime(2021, 8, 4),  # Week 10
        datetime(2021, 8, 10),  # Week 11
        datetime(2021, 8, 11),
        datetime(2021, 8, 16),  # Week 12
    ]

    for date in dates2:
        deployment_dict = {
            "category": "Deployment",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": project2.id,
        }

        work_item_data = WorkItemCreate(**deployment_dict)
        crud.create_work_item(db, work_item_data, project_auth_token2)

    # Create Pull Request Items
    pull_dates = [
        datetime(2021, 8, 11),
        datetime(2021, 8, 19),
    ]

    pull_req_work_items = []
    project_ids = [project.id, project2.id]
    print(project_ids)
    project_auth_tokens = [project_auth_token, project_auth_token2]
    print(project_auth_tokens)
    proj_iter = 0
    for date in pull_dates:
        pull_dict = {
            "category": "Pull Request",
            "end_time": date
            + time_shift,  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": project_ids[proj_iter],
        }
        work_item_data = WorkItemCreate(**pull_dict)
        work_item_id = crud.create_work_item(
            db, work_item_data, project_auth_tokens[proj_iter]
        )
        pull_req_work_items.append(work_item_id)
        proj_iter += 1

    commit_dates = [
        datetime(2021, 8, 8),
        datetime(2021, 8, 9),
        datetime(2021, 8, 10),
        datetime(2021, 8, 11),
    ]

    i = 0
    proj_iter = 0
    for item_id in pull_req_work_items:
        for date in commit_dates:
            commit_dict = {
                "sha": random_sha(
                    i
                ),  # used for random string generation (not actually a proj auth token)
                "date": date + time_shift,
                "author": "Gabe Geiger",
                "work_item_id": item_id,
            }

            commit_data = CommitCreate(**commit_dict)
            commit_crud.create_commit(db, commit_data, project_auth_tokens[proj_iter])
            i += 1
        proj_iter += 1

    all_projects = proj_crud.get_all(db)

    if len(all_projects) != 2:
        return "Incorrect number of projects present. Clear database and rerun."
    else:
        pass

    all_work_items = crud.get_all(db)

    if len(all_work_items) != (len(dates) + len(dates2) + len(pull_dates)):
        return "Incorrect number of work items present. Clear database and rerun."
    else:
        pass

    return (
        "Successfully created local database. Project Auth tokens are:",
        project_auth_token,
        project_auth_token2,
    )


@router.delete("/clear_local_db")
def clear_db():

    """
    ## Clear Local Database

    Calling this endpoint drops all entries from all tables present in the local issues.db database.

    """
    SQLModel.metadata.drop_all(engine)
    return "Database cleared"
