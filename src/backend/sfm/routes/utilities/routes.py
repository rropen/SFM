from sqlalchemy.sql.expression import false
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate, ProjectCreate
from typing import List, Optional
from sqlmodel import SQLModel, Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header
from sfm.database import engine
from datetime import datetime, timedelta

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.post("/create_local_db/deployment_frequency")
def populate_db(
    db: Session = Depends(get_db),
):
    """
    ## Populate standardized local db for deployment frequency metric testing

    """
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
            + timedelta(
                days=25
            ),  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
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
            + timedelta(
                days=25
            ),  # ADDED TIME DELTA SHIFT TO BRING CLOSER TO CURRENT DATE
            "project_id": project2.id,
        }

        work_item_data = WorkItemCreate(**deployment_dict)
        crud.create_work_item(db, work_item_data, project_auth_token2)

    all_projects = proj_crud.get_all(db)

    print(all_projects)
    print(len(all_projects))

    if len(all_projects) != 2:
        return "Incorrect number of projects present. Clear database and rerun."
    else:
        pass

    all_deployments = crud.get_all(db)
    if len(all_deployments) != (len(dates) + len(dates2)):
        return "Incorrect number of deployments present. Clear database and rerun."
    else:
        pass

    return (
        "Successfully created local database. Project Auth tokens are:",
        project_auth_token,
        project_auth_token2,
    )


@router.delete("/clear_local_db")
def clear_db():
    SQLModel.metadata.drop_all(engine)
    return "Database cleared"
