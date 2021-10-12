from fastapi.exceptions import HTTPException
from sfm.models import Project, WorkItem
from sqlmodel import Session, select
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings
from sfm.utils import (
    create_project_auth_token,
    hash_project_auth_token,
    verify_admin_key,
)

app_settings = get_settings()

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

# logger.addHandler(
#     AzureLogHandler(connection_string=app_settings.AZURE_LOGGING_CONN_STR)
# )


def get_all(db: Session, skip: int = None, limit: int = None):
    """Get all the projects and return them."""
    projects = db.exec(
        select(Project).order_by(Project.id).offset(skip).limit(limit)
    ).all()
    if not projects:
        logger.warning('func="get_all" warning="Projects not found"')
        raise HTTPException(status_code=404, detail="Projects not found")
    return projects


def get_by_id(db: Session, project_id: int):
    """Get the project with corresponding id and return it."""
    project = db.get(Project, project_id)
    if not project:
        logger.warning('func="get_by_id" warning="Projects not found"')
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def create_project(db: Session, project_data, admin_key):
    """Take data from request and create a new project in the database."""
    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project_temp = project_data.dict()
        token = create_project_auth_token()
        hashed_token = hash_project_auth_token(token)
        project_temp.update({"project_auth_token_hashed": hashed_token})
        project_db = Project(**project_temp)
        db.add(project_db)
        db.commit()
    else:
        logger.warning('func="create_project" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    project_name_repeat = db.exec(
        select(Project).where(Project.name == project_data.name)
    )
    if project_name_repeat is None:
        logger.warning('func="create_project" warning="Database entry already exists"')
        raise HTTPException(status_code=409, detail="Database entry already exists")

    # Check the new record
    db.refresh(project_db)
    new_project = db.get(Project, project_db.id)
    if new_project.name == project_data.name:
        return [new_project, token]  # successfully created record
    else:
        logger.error('func="create_project" error="Project did not store correctly"')
        return False  # didn't store correctly


def delete_project(db: Session, project_id, admin_key):
    """Take a project_name and remove the row from the database."""
    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project = db.get(Project, project_id)
        if not project:
            logger.warning('func="delete_project" warning="Project not found"')
            raise HTTPException(status_code=404, detail="Project not found")

        for item in project.work_items:
            db.delete(item)
        db.delete(project)
        db.commit()
    else:
        logger.warning('func="delete_project" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = db.get(Project, project_id)
    if row:
        logger.error('func="delete_project" error="Project did not delete correctly"')
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # Successful deletion


def refresh_project_key(db: Session, project_id, admin_key):
    verified_admin = verify_admin_key(admin_key)

    if verified_admin:
        project_db = db.get(Project, project_id)
        if not project_db:
            logger.warning(
                'func="refresh_project_key" warning="Project with matching id not found"'
            )
            raise HTTPException(
                status_code=404, detail="Project with matching id not found"
            )
        new_token = create_project_auth_token()
        hashed_token = hash_project_auth_token(new_token)
        project_db.project_auth_token_hashed = hashed_token
        db.add(project_db)
        db.commit()
    else:
        logger.warning('func="refresh_project_key" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    check = db.exec(
        select(Project).where(Project.project_auth_token_hashed == hashed_token)
    )
    if check:
        return new_token
    else:
        logger.error(
            'func="refresh_project_key" error="Project auth token did not update correctly"'
        )
        return False


def update_project(db: Session, project_id, project_data, admin_key):
    """Take data from request and update an existing Project in the database."""

    verified_admin = verify_admin_key(admin_key)
    if verified_admin:
        project = db.get(Project, project_id)
        if not project:
            logging.warning('func="update_project" warning="Project not found"')
            raise HTTPException(status_code=404, detail="Project not found")

        project_newdata = project_data.dict(exclude_unset=True, exclude_defaults=True)
        for key, value in project_newdata.items():
            setattr(project, key, value)

        db.add(project)
        db.commit()

    else:
        logger.warning('func="update_project" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    db.refresh(project)
    if project:
        return project  # updated record
    else:
        logger.warning(
            'func="update_project" warning="Project did not store correctly"'
        )
        return False  # didn't store correctly
