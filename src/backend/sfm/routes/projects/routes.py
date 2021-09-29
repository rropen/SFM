from fastapi.param_functions import Header
from sfm.routes.projects import crud
from sfm.dependencies import get_db
from sfm.models import (
    ProjectRead,
    ProjectCreate,
    ProjectUpdate,
)
from typing import List, Optional
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sfm.database import engine

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(levelname)s %(name)s %(asctime)s %(message)s",
)
logger = logging.getLogger(__name__)
"""TODO: ADD AZURE INSTRUMENTATION KEY ONCE WE SETUP SFM ON AZURE"""
# logger.addHandler(AzureLogHandler(
#     connection_string='InstrumentationKey=00000000-0000-0000-0000-000000000000')
# )


router = APIRouter()


class CustomGetParams:
    """Custom parameter class for the GET projects route.

    skip = 0 & limit = 100 by default.
    This format enables a custom description field for each parameter that will display
    in the backend swagger docs.
    """

    def __init__(
        self,
        skip: int = Query(
            0,
            description="This parameter sets the number of projects to *skip* at the beginning of the listing.",
        ),
        limit: int = Query(
            1000,
            description="This parameter sets the maximum number of projects to display in the response.",
        ),
    ):
        self.skip = skip
        self.limit = limit


@router.get("/", response_model=List[ProjectRead])
def get_projects(params: CustomGetParams = Depends(), db: Session = Depends(get_db)):
    """
    ## Get Multiple Projects

    ---

    Query Parameters:

    - **skip**: sets the number of projects to *skip* at the beginning of the listing
    - **limit**: sets the maximum number of projects to display in the listing

    >When used together, *skip* and *limit* facilitate serverside pagination support.

    """
    logger.info('method=GET path="projects/"')
    projects = crud.get_all(db, skip=params.skip, limit=params.limit)
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project_by_id(project_id: int, db: Session = Depends(get_db)):
    """
    ## Get Project by Id

    Get a single project with matching **project_id** stored in the database

    ---

    Path Parameters:

    - **project_id**: Unique identifier that links to the project in the database

    """
    logger.info('method=GET path="projects/{project_id}"')
    project = crud.get_by_id(db, project_id=project_id)
    return project


@router.post("/")
def create_project(
    project_data: ProjectCreate,
    admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Create a Project

    Create a new project in the database from the data provided in the request.

    ---

    Request Headers:

    - **admin_key**: Authorization key that allows for large changes to items in the database

    ---

    Request Body Parameters:
    - **name**: Name of the project or repository
    - **lead_name**: Name of the person in charge of the project
    - **lead_email**: Email of the person in charge of the project
    - **description**: Long string describing what the project/repo is about
    - **location**: Location of the owner's group. (E.g. Indianapolis, UK, Germany, etc.)
    - **repo_url**: Github or Gitlab url to the corresponding project
    - **on_prem**: Boolean describing if the repo is located on a "on-premises" server
    """
    logger.info('method=POST path="projects/"')
    # Creates the database row and stores it in the table

    new_project_arr = crud.create_project(db, project_data, admin_key)

    if new_project_arr:
        new_project = new_project_arr[0]
        token = new_project_arr[1]
        return {
            "code": "success",
            "id": new_project.id,
            "token": token,
        }
    else:
        logger.error('method=POST path="projects/" error="Row Not Created"')
        return {"code": "error", "message": "Row Not Created"}  # pragma: no cover


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Delete a project

    Pass a **project_id** value and the project will be deleted from the database.

    ---

    Path Parameters:

    - **project_id**: Unique identifier that links to the object in the database to be deleted

    """
    logger.info('method=DELETE path="projects/{project_id}"')
    response = crud.delete_project(db, project_id, admin_key)

    if response:
        return {
            "code": "success",
            "message": "Project {} and associated workItems deleted".format(project_id),
        }
    else:  # pragma: no cover
        logger.error(
            'method=POST path="projects/{project_id}" error="Project not deleted or multiple projects with same project_id existed."'
        )
        return {
            "code": "error",
            "message": "Project not deleted or multiple projects with same project_id existed.",
        }


@router.post("/{project_id}")
def refresh_project_key(
    project_id: int,
    admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Refresh a Project's Auth Token

    Pass a project_id value and admin key and the project auth token will be refreshed and returned.

    ---

    Request Headers:

    - **admin_key**: Authorization key that allows for large changes to items in the database

    ---

    Path Parameters:

    - **project_id**: Unique identifier that links to the project to be deleted

    """
    logger.info('method=POST path="projects/{project_id}"')
    if not project_id:
        logger.error(
            'method=POST path="projects/{project_id}" error="Project_id not provided"'
        )
        raise HTTPException(status_code=404, detail="project_id not provided")

    refreshed_token = crud.refresh_project_key(db, project_id, admin_key)
    if refreshed_token:
        return {
            "code": "success",
            "token": refreshed_token,
        }
    else:
        logger.error(
            'method=POST path="projects/{project_id}" error="Token  Not Refresh"'
        )
        return {"code": "error", "message": "Token Not Refreshed"}  # pragma: no cover


@router.patch("/{project_id}")
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    admin_key: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Update Project

    Update an existing Project in the database from the data provided in the request.

    ---

    Request Headers:

    - **admin_key**: Authorization key that allows for large changes to items in the database

    ---

    Path Parameters:

    - **project_id**: Unique identifier that links to the project to be updated

    ---

    Request Body Parameters:

    - **name**: Name of the project or repository
    - **lead_name**: Name of the person in charge of the project
    - **lead_email**: Email of the person in charge of the project
    - **description**: Long string describing what the project/repo is about
    - **location**: Location of the owner's group. (E.g. Indianapolis, UK, Germany, etc.)
    - **repo-url**: Github or Gitlab url to the corresponding project
    - **on_prem**: Boolean describing if the repo is located on a "on-premises" server

    """
    logger.info('method=PATCH path="projects/{project_id}"')
    update_project_success = crud.update_project(
        db, project_id, project_data, admin_key
    )

    if update_project_success:
        return {
            "code": "success",
            "id": update_project_success.id,
        }
    else:
        logger.error(
            'method=PATCH path="projects/{project_id}" error="Row not updated"'
        )
        return {"code": "error", "message": "Row not updated"}  # pragma: no cover
