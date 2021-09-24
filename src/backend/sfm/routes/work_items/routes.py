from sfm.routes.work_items import crud
from sfm.dependencies import get_db
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate
from typing import List, Optional
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header
from sfm.database import engine


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

    Get a list of all the WorkItems stored in the database.

    Query Parmeters:

    ---

    - **skip**: sets the number of items to skip at the beginning of the listing
    - **limit**: sets the max number of items to be displayed when called
    - **project_id**: specifying **project_id** returns only work items in a given project
    - **project_name**: specifying **project_name** returns only work items in a given project
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
    ## Get WorkItem by ID

    Get a specific WorkItem by specifying the ID in the path.

    ---

    Path Parameters:

    -**work_item_id**: id of the work item to be requested

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
    ## Create WorkItem entry in db

    Create a new WorkItem in the database by specifying data in the request.

    ---

    Request Headers:

    - **project_auth_token**: authentication key to allow for major changes to occur to project data (specific to the WorkItem's project)

    ---

    Request Body Parameters:

    - **category**: event category for the work item. Must be one of the following options:
        1. "Deployment"
        2. "Issue"
        3. "Pull Request"
    - **start_time**: sets the start time of the WorkItem
    - **end_time**: sets the end time of the WorkItem (could be merged date or closed date depending on metric needs for the specified WorkItem category)
    - **duration_open**: sets duration of WorkItem being open
    - **project_id**: sets project the WorkItem belongs to

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

    Pass a WorkItem database id value in the path and the WorkItem will be deleted from the database.

    ---

    Path Parameters:

    - **work_item_id**: selects WorkItem being open

    ---

    Request Headers:

    - **project_auth_token**: authentication key to allow for major changes to occur to project data (specific to the WorkItem's project)
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


@router.patch("/{work_item_id}")
def update_work_item(
    work_item_id: int,
    work_item_data: WorkItemUpdate,
    project_auth_token: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    ## Update WorkItem

    Update an existing WorkItem in the database from the data provided in the request.

    ---

    Path Parameters:

    - **work_item_id**: selects WorkItem being open

    ---

    Request Headers:

    - **project_auth_token**: authentication key to allow for major changes to occur to project data (specific to the WorkItem's project)

    ---

    Request Body Parameters:

    - **category**: event category for the work item. Must be one of the following options:
        1. "Deployment"
        2. "Issue"
        3. "Pull Request"
    - **start_time**: sets the start time of the WorkItem
    - **end_time**: sets the end time of the WorkItem (could be merged date or closed date depending on metric needs for the specified WorkItem category)
    - **project_id**: sets project the WorkItem belongs to
    """
    if not work_item_data:
        raise HTTPException(status_code=404, detail="WorkItem data not provided")

    update_work_item_success = crud.update_work_item(
        db, work_item_id, work_item_data, project_auth_token
    )

    if update_work_item_success:
        return {
            "code": "success",
            "id": update_work_item_success,
        }
    else:
        return {"code": "error", "message": "Row not updated"}
