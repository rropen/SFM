from fastapi.exceptions import HTTPException
from sfm.models import WorkItem, Project
from sqlmodel import Session, select, and_
from sfm.utils import verify_project_auth_token
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from sfm.config import get_settings


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


def get_all(
    db: Session,
    skip: int = None,
    limit: int = None,
    project_id: int = None,
    project_name: str = None,
):
    """Get all the WorkItems and return them."""
    project = None
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            logger.warning('func="get_all" warning="Project not found"')
            raise HTTPException(status_code=404, detail="Project not found")

    if project:
        return db.exec(select(WorkItem).where(WorkItem.project_id == project.id)).all()

    return db.exec(
        select(WorkItem).order_by(WorkItem.id).offset(skip).limit(limit)
    ).all()


def get_by_id(db: Session, work_item_id):
    """Get a specified WorkItem and return it."""
    workitem = db.get(WorkItem, work_item_id)
    if workitem:
        return workitem
    if not workitem:
        logger.warning('func="get_by_id" warning="Item not found"')
        raise HTTPException(status_code=404, detail="Item not found")


def create_work_item(db: Session, work_item_data, project_auth_token):
    """Take data from request and create a new WorkItem in the database."""
    intended_project = db.get(Project, work_item_data.project_id)
    if not intended_project:
        logger.warning('func="create_work_item" warning="Project not found"')
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        work_temp = work_item_data.dict()
        if work_temp["start_time"] and work_temp["end_time"]:
            duration_open = int(
                (work_temp["end_time"] - work_temp["start_time"]).total_seconds()
            )
            work_temp.update({"duration_open": duration_open})

        work_item_db = WorkItem(**work_temp)
        db.add(work_item_db)
        db.commit()
    else:
        logger.warning('func="create_work_item" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check the new record exists
    db.refresh(work_item_db)
    if work_item_db:
        return work_item_db.id  # successfully created record
    else:
        logger.error('func="create_work_item" error="Item did not store correctly"')
        raise HTTPException(
            status_code=404, detail="Item did not store correctly"
        )  # didn't store correctly


def delete_work_item(db: Session, work_item_id, project_auth_token):
    """Take a issueTitle and remove the row from the database."""
    work_item = db.get(WorkItem, work_item_id)
    if not work_item:
        logger.warning('func="delete_work_item" warning="Item not found"')
        raise HTTPException(status_code=404, detail="Item not found")

    intended_project = db.get(Project, work_item.project_id)
    if not intended_project:
        logger.warning('func="delete_work_item" warning="Project not found"')
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        db.delete(work_item)
        db.commit()
    else:
        logger.warning('func="delete_work_item" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # Check our work
    row = db.get(WorkItem, work_item_id)
    if row:
        logger.error('func="delete_work_item" error="Item did not delete correctly"')
        raise HTTPException(
            status_code=404, detail="Item did not delete correctly"
        )  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful


def update_work_item(db: Session, work_item_id, work_item_data, project_auth_token):
    """Take data from request and update an existing WorkItem in the database."""
    work_item = db.get(WorkItem, work_item_id)
    if not work_item:
        logger.warning('func="update_work_item" warning="Item not found"')
        raise HTTPException(status_code=404, detail="Item not found")

    intended_project = db.get(Project, work_item.project_id)
    if not intended_project:
        logger.warning('func="update_work_item" warning="Project not found"')
        raise HTTPException(status_code=404, detail="Project not found")
    verified = verify_project_auth_token(
        project_auth_token, intended_project.project_auth_token_hashed
    )
    if verified:
        # work_item_dict = work_item.dict()

        # for key, value in work_item_dict:
        #     if work_item_data[key]:
        #         setattr(work_item_dict, key, work_item_data[key])

        work_item_newdata = work_item_data.dict(exclude_unset=True)
        for key, value in work_item_newdata.items():
            setattr(work_item, key, value)

        db.add(work_item)
        db.commit()
        db.refresh(work_item)
        if work_item.start_time and work_item.end_time:
            work_item.duration_open = int(
                (work_item.end_time - work_item.start_time).total_seconds()
            )
            db.add(work_item)
            db.commit()

    else:
        logger.warning('func="update_work_item" warning="Credentials are incorrect"')
        raise HTTPException(status_code=401, detail="Credentials are incorrect")

    # return updated item
    db.refresh(work_item)
    if work_item:
        return work_item  # updated record
    else:
        logger.error('func="update_work_item" error="Item did not store correctly"')
        raise HTTPException(status_code=404, detail="Item did not store correctly")
