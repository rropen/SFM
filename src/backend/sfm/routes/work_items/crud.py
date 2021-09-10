from os import stat
from fastapi.exceptions import HTTPException
from sqlalchemy.sql.expression import false
from sfm.models import WorkItem, Project
from sqlmodel import Session, select, and_
from sfm.utils import verify_project_auth_token


def get_all(db: Session, skip: int, limit: int, project_id: int, project_name: str):
    """Get all the WorkItems and return them."""
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            return False
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            return False
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            return False

    if project:
        return project.work_items

    return db.exec(select(WorkItem).offset(skip).limit(limit)).all()


def get_by_id(db: Session, work_item_id):
    """Get a specified WorkItem and return it."""

    return db.get(WorkItem, work_item_id)


def create_work_item(db: Session, work_item_data, project_auth_token):
    """Take data from request and create a new WorkItem in the database."""
    intended_project = db.get(Project, work_item_data.project_id)
    if not intended_project:
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token
    )
    if verified:
        work_item_db = WorkItem.from_orm(work_item_data)
        db.add(work_item_db)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check the new record exists
    db.refresh(work_item_db)
    if work_item_db:
        return work_item_db.id  # successfully created record
    else:
        return False  # didn't store correctly


def delete_work_item(db: Session, work_item_id, project_auth_token):
    """Take a issueTitle and remove the row from the database."""
    work_item = db.get(WorkItem, work_item_id)
    if not work_item:
        raise HTTPException(status_code=404, detail="Issue not found")
    intended_project = db.get(Project, work_item.project_id)
    if not intended_project:
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token
    )
    if verified:
        db.delete(work_item)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = db.get(WorkItem, work_item_id)
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_work_item(db: Session, work_item_id, work_item_data, project_auth_token):
    """Take data from request and update an existing WorkItem in the database."""
    work_item = db.get(WorkItem, work_item_id)
    if not work_item:
        raise HTTPException(status_code=404, detail="Item not found")

    intended_project = db.get(Project, work_item.project_id)
    if not intended_project:
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token
    )
    if verified:
        work_item_newdata = work_item_data.dict(exclude_unset=True)
        for key, value in work_item_newdata.items():
            setattr(work_item, key, value)

        db.add(work_item)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    db.refresh(work_item)
    if work_item:
        return work_item  # updated record
    else:
        return False  # didn't store correctly
