from sfm.routes.work_items import crud
from sfm.models import WorkItemRead, WorkItemCreate
from typing import List, Optional
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header
from sfm.database import engine

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.get("/", response_model=List[WorkItemRead])
def get_work_items(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    ## Get WorkItems

    Get a list of all the WorkItems stored in the database
    """
    work_items = crud.get_all(
        db, skip=skip, limit=limit, project_id=project_id, project_name=project_name
    )
    if not work_items:
        raise HTTPException(status_code=404, detail="WorkItems not found")
    return work_items


@router.get("/{work_item_id}")
def get_work_item(work_item_id: int, db: Session = Depends(get_db)):
    """
    ## Get WorkItem Specified by ID

    Get a WorkItem stored in the database
    """
    work_item = crud.get_by_id(db, work_item_id)
    if not work_item:
        raise HTTPException(status_code=404, detail="WorkItem not found")
    return work_item


@router.post("/")
def create_work_item(
    work_item_data: WorkItemCreate,
    project_auth_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Create WorkItem

    Create a new WorkItem in the database from the data provided in the request.
    """
    if not work_item_data:
        raise HTTPException(status_code=404, detail="WorkItem data not provided")

    # Creates the database row and stores it in the table

    new_work_item_success = crud.create_work_item(
        db, work_item_data, project_auth_token
    )

    if new_work_item_success:
        return {
            "code": "success",
            "id": new_work_item_success,
        }
    else:
        return {"code": "error", "message": "Row Not Created"}


# Since  WorkItem has no name, use database id to delete item
@router.delete("/{work_item_id}")
def delete_work_item(
    work_item_id: int,
    project_auth_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Delete a WorkItem

    Pass a WorkItem database id value and the WorkItem will be deleted from the database.
    """
    if not work_item_id:
        raise HTTPException(status_code=404, detail="work_item_id not provided")

    response = crud.delete_work_item(db, work_item_id, project_auth_token)

    if response:
        return {
            "code": "success",
            "message": "WorkItem {} Deleted".format(work_item_id),
        }
    else:
        return {
            "code": "error",
            "message": "WorkItem not deleted or multiple WorkItems with same work_item_id existed.",
        }
