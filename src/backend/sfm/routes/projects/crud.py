from fastapi.exceptions import HTTPException
from sfm.models import Project, WorkItem
from sqlmodel import Session, select

from sfm.utils import (
    create_project_auth_token,
    hash_project_auth_token,
    verify_admin_key,
)


def get_all(db: Session, skip: int = None, limit: int = None):
    """Get all the projects and return them."""
    projects = db.exec(select(Project).offset(skip).limit(limit)).all()
    return projects


def get_by_id(db: Session, project_id: int):
    """Get the project with corresponding id and return it."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def create_project(db: Session, project_data, admin_key):
    """Take data from request and create a new project in the database."""
    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project_temp = project_data.dict()
        token = create_project_auth_token()
        hashed_token = hash_project_auth_token(token)
        project_temp.update({"projectAuthTokenHashed": hashed_token})
        project_db = Project(**project_temp)
        db.add(project_db)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check the new record
    db.refresh(project_db)
    new_project = db.get(Project, project_db.id)
    if new_project.name == project_data.name:
        return [new_project, token]  # successfully created record
    else:
        return False  # didn't store correctly


def delete_project(db: Session, project_id, admin_key):
    """Take a project_name and remove the row from the database."""
    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        for item in project.workItems:
            db.delete(item)
        db.delete(project)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = db.get(Project, project_id)
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # Successful deletion


def refresh_project_key(db: Session, project_id, admin_key):
    verified_admin = verify_admin_key(admin_key)

    if verified_admin:
        project_db = db.get(Project, project_id)
        if not project_db:
            raise HTTPException(
                status_code=404, detail="Project with matching id not found"
            )
        new_token = create_project_auth_token()
        hashed_token = hash_project_auth_token(new_token)
        project_db.projectAuthTokenHashed = hashed_token
        db.add(project_db)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    check = db.exec(
        select(Project).where(Project.projectAuthTokenHashed == hashed_token)
    )
    if check:
        return new_token
    else:
        return False


def update_project(db: Session, project_id, project_data, admin_key):
    """Take data from request and update an existing Project in the database."""

    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        project_newdata = project_data.dict(exclude_unset=True, exclude_defaults=True)
        for key, value in project_newdata.items():
            setattr(project, key, value)

        db.add(project)
        db.commit()

    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    db.refresh(project)
    if project:
        return project  # updated record
    else:
        return False  # didn't store correctly
