from fastapi.exceptions import HTTPException
from sfm.models import WorkItem, Project, Commit
from sqlmodel import Session, select, and_
from sfm.utils import verify_project_auth_token
from sfm.config import get_settings
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.logger import create_logger

logger = create_logger(__name__)

app_settings = get_settings()


def get_all(
    db: Session,
    skip: int = None,
    limit: int = None,
    project_id: int = None,
    project_name: str = None,
):
    """Get all the Commits and return them."""
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            logger.debug("Project not found")
            raise HTTPException(status_code=404, detail="Project not found")
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            logger.debug("Project not found")
            raise HTTPException(status_code=404, detail="Project not found")
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            logger.debug("Project not found")
            raise HTTPException(status_code=404, detail="Project not found")

    if project:
        workitems = project.work_items
        project_commits = []
        for item in workitems:
            project_commits.extend(item.commits)
        project_commits = project_commits[skip:limit]
        return project_commits

    return db.exec(select(Commit).order_by(Commit.id).offset(skip).limit(limit)).all()


def get_by_sha(db: Session, commit_sha):
    """Get a specified Commit and return it."""
    return db.exec(select(Commit).where(Commit.sha == commit_sha)).first()


def get_by_id(db: Session, commit_id):
    """Get a specified Commit and return it."""
    return db.get(Commit, commit_id)


def create_commit(db: Session, commit_data, project_auth_token):
    """Take data from request and create a new Commit in the database."""
    work_item = db.get(WorkItem, commit_data.work_item_id)
    intended_project = db.get(Project, work_item.project_id)
    if not intended_project:
        logger.debug("Project not found")
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        commit_temp = commit_data.dict()
        time_to_pull = int((work_item.end_time - commit_temp["date"]).total_seconds())
        commit_temp.update({"time_to_pull": time_to_pull})
        commit_db = Commit(**commit_temp)
        db.add(commit_db)
        db.commit()
    else:
        logger.warning("Attempted to access project with incorrect project auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check the new record exists
    db.refresh(commit_db)
    if commit_db:
        return commit_db.sha  # successfully created record
    else:
        logger.error("Item did not store correctly in database")
        raise HTTPException(
            status_code=404, detail="Item did not store correctly"
        )  # didn't store correctly


def delete_commit(db: Session, commit_sha, project_auth_token):
    """Take a commit and remove the row from the database."""
    commit = db.exec(select(Commit).where(Commit.sha == commit_sha)).first()
    if not commit:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")
    intended_project = db.get(Project, commit.work_item.project.id)
    if not intended_project:
        logger.debug("Project not found")
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        db.delete(commit)
        db.commit()
    else:
        logger.warning("Attempted to access project with incorrect project auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = db.exec(select(Commit).where(Commit.sha == commit_sha)).first()
    if row:
        logger.error("Item did not delete correctly and still exists")
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly and still exists"
        )  # Row didn't successfully delete or another one exists  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_commit(db: Session, commit_sha, commit_data, project_auth_token):
    """Take data from request and update an existing Commit in the database."""
    commit = db.exec(select(Commit).where(Commit.sha == commit_sha)).first()
    if not commit:
        logger.debug("Item not found")
        raise HTTPException(status_code=404, detail="Item not found")

    intended_project = db.get(Project, commit.work_item.project.id)
    if not intended_project:
        logger.debug("Project not found")
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        commit_newdata = commit_data.dict(exclude_unset=True, exclude_defaults=True)

        for key, value in commit_newdata.items():
            setattr(commit, key, value)

        time_to_pull = int((commit.work_item.end_time - commit.date).total_seconds())

        setattr(commit, "time_to_pull", time_to_pull)

        db.add(commit)
        db.commit()
    else:
        logger.warning("Attempted to access project with incorrect project auth token")
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    db.refresh(commit)
    if commit:
        return commit  # updated record
    else:
        logger.error("Item did not store correctly")
        raise HTTPException(status_code=404, detail="Item did not store correctly")
