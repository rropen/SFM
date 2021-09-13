from fastapi.param_functions import Header
from sfm.routes.projects import crud
from sfm.models import (
    ProjectRead,
    ProjectCreate,
    ProjectUpdate,
)
from typing import List
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path
from sfm.database import engine

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.get("/", response_model=List[ProjectRead])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get Projects

    Get a list of all the projects stored in the database
    """
    projects = crud.get_all(db, skip=skip, limit=limit)
    if not projects:
        raise HTTPException(status_code=404, detail="Projects not found")
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    ## Get Project by Id

    Get a the project with matching id stored in the database
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
    ## Create Project

    Create a new project in the database from the data provided in the request.
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

    Pass a project_id value and the project will be deleted from the database.
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
    ## Refresh a project auth token

    Pass a project_id value and admin key and the project auth token will be refreshed.
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
