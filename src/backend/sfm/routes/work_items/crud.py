from fastapi.exceptions import HTTPException
from sfm.models import WorkItem
from sqlmodel import Session, select


def get_all(db: Session, skip: int = 0, limit: int = 25):
    """Get all the WorkItems and return them."""

    return db.exec(select(WorkItem).offset(skip).limit(limit)).all()


def create_work_item(db: Session, work_item_data):
    """Take data from request and create a new WorkItem in the database."""
    work_item_db = WorkItem.from_orm(work_item_data)
    db.add(work_item_db)
    db.commit()
    db.refresh(work_item_db)

    # Check the new record exists
    new_work_item = db.get(WorkItem, work_item_db.id)
    if new_work_item:
        return new_work_item.id  # successfully created record
    else:
        return False  # didn't store correctly


def delete_work_item(db: Session, work_item_id):
    """Take a issueTitle and remove the row from the database."""
    work_item = db.get(WorkItem, work_item_id)
    if not work_item:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(work_item)
    db.commit()

    # Check our work
    row = db.get(WorkItem, work_item_id)
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful
