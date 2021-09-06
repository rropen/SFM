from fastapi.exceptions import HTTPException
from sfm.models import Project
from sqlmodel import Session, select


def get_all(db: Session, skip: int = 0, limit: int = 25):
    """Get all the projects and return them."""

    return db.exec(select(Project).offset(skip).limit(limit)).all()


def create_project(db: Session, project_data):
    """Take data from request and create a new project in the database."""
    project_db = Project.from_orm(project_data)
    db.add(project_db)
    db.commit()

    # Check the new record
    new_project = db.get(Project, project_db.id)
    if new_project.name == project_data.name:
        return True  # successfully created record
    else:
        return False  # didn't store correctly


def delete_project(db: Session, project_id):
    """Take a project_name and remove the row from the database."""
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    # Check our work
    row = db.get(Project, project_id)
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # Successful deletion
