from fastapi.param_functions import Header
from sfm.routes.projects import crud
from sfm.models import (
    ProjectRead,
    ProjectCreate,
    ProjectUpdate,
)
from typing import List
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sfm.database import engine

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


class CustomGetParams:
    def __init__(
        self,
        skip: int = Query(
            ...,
            description="This parameter sets the number of projects to *skip* at the beginning of the listing.",
        ),
        limit: int = Query(
            ...,
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
    projects = crud.get_all(db, skip=params.skip, limit=params.limit)
    if not projects:
        raise HTTPException(status_code=404, detail="Projects not found")
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
    project = crud.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
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
    - **repo-url**: Github or Gitlab url to the corresponding project
    - **on_prem**: Boolean describing if the repo is located on a "on-premises" server
    """
    if not project_data:
        raise HTTPException(status_code=404, detail="Project data not provided")

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
        return {"code": "error", "message": "Row Not Created"}


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
    if not project_id:
        raise HTTPException(status_code=404, detail="project_id not provided")

    response = crud.delete_project(db, project_id, admin_key)

    if response:
        return {
            "code": "success",
            "message": "Project {} and associated workItems deleted".format(project_id),
        }
    else:
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
    if not project_id:
        raise HTTPException(status_code=404, detail="project_id not provided")

    refreshed_token = crud.refresh_project_key(db, project_id, admin_key)
    if refreshed_token:
        return {
            "code": "success",
            "token": refreshed_token,
        }
    else:
        return {"code": "error", "message": "Token Not Refreshed"}


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
    if not project_data:
        raise HTTPException(status_code=404, detail="Project data not provided")

    update_project_success = crud.update_project(
        db, project_id, project_data, admin_key
    )

    if update_project_success:
        return {
            "code": "success",
            "id": update_project_success.id,
        }
    else:
        return {"code": "error", "message": "Row not updated"}
