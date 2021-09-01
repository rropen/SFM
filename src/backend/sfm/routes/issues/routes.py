from sfm.routes.issues import crud
from sfm.models import IssueRead, IssueCreate 
from typing import List
from sqlmodel import Session, select
from fastapi import APIRouter, HTTPException, Depends, Path
from sfm.database import engine
import json

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.get("/", response_model=List[IssueRead])
def get_issues(skip: int = 2, limit: int = 100, db: Session = Depends(get_db)):
    """
    ## Get Issues

    Get a list of all the issues stored in the database
    """
    issues = crud.get_all(db, skip=skip, limit=limit)
    if not issues:
        raise HTTPException(status_code=404, detail="Issues not found")
    return issues


@router.post("/")
def create_issue(issue_data: IssueCreate, db: Session = Depends(get_db)):
    """
    ## Create Issue 

    Create a new issue in the database from the data provided in the request.
    """
    if not issue_data:
        raise HTTPException(status_code=404, detail="Issue data not provided")
    response_object = []

    # Creates the database row and stores it in the table

    new_issue_success = crud.create_issue(db, issue_data)

    if new_issue_success:
        return {
            "code": "success",
            "message": "Row Created",
        }
    else:
        return {"code": "error", "message": "Row Not Created"}


@router.delete("/{issueTitle}")
def delete_issue(
    issueTitle: str = Path(..., title="The ID of the Issue"),
    db: Session = Depends(get_db),
):
    """
    ## Delete an issue 

    Pass a issueTitle value and the issue will be deleted from the database.
    """
    if not issueTitle:
        raise HTTPException(status_code=404, detail="issueTitle not provided")
        response_object = []

    response = crud.delete_issue(db, issueTitle)

    if response:
        return {"code": "success", "message": "Issue {} Deleted".format(issueTitle)}
    else:
        return {
            "code": "error",
            "message": "Issue not Deleted or Multiple issues with same issueTitle existed.",
        }

@router.get("/test")
def crud_test(db: Session = Depends(get_db)):
    response = crud.group_cost(db)
    # print(response)
    return json.dumps(response)