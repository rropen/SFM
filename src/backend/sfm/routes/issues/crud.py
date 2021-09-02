from fastapi.exceptions import HTTPException
from sfm.models import Issue, IssueRead, IssueCreate, IssueUpdate 
from sqlmodel import Session, select

def get_all(db: Session, skip: int = 0, limit: int = 25):
    """Get all the issues and return them."""

    return db.exec(select(Issue).offset(skip).limit(limit).all())

def create_issue(db: Session, issue_data):
    """Take data from request and create a new issue in the database."""
    issue_db = Issue.from_orm(issue_data) 
    db.add(issue_db)
    db.commit()

    # Check the new record
    new_issue = db.get(Issue, issue_data.id).first()
    if new_issue.issueTitle == issue_data.issueTitle:
        return True  # successfully created record
    else:
        return False  # didn't store correctly


def delete_issue(db: Session, issueTitle):
    """Take a issueTitle and remove the row from the database."""
    issue = db.exec(select(Issue).where(Issue.issueTitle == issueTitle))
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    db.delete(issue)
    db.commit()

    # Check our work
    row = db.exec(select(Issue).where(issueTitle == issueTitle).where(Issue.issueTitle == issueTitle).first())
    if row:
        return False  # Row didn't successfully delete or another one exists
    else:
        return True  # We were successful
