from sfm.routes.work_items import crud
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate
from typing import List, Optional
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


router = APIRouter()


@router.post("/webhook_events/")
async def webhook_handler(
    request: Request,
    project_auth_token: str = Header(...),
    db: Session = Depends(get_db),
):
    # handle events
    payload = await request.json()
    event_type = request.headers.get("X-Github-Event")

    # gather common payload object properties
    if event_type != "push":  # push events are the exception to common properties
        action = payload.get("action")
        print(action)
        """
        sender = payload.get("sender")
        repository = payload.get("repository")
        organization = payload.get("organization")
        installation = payload.get("installation")
        """

    else:
        # TODO: pull in push event information
        pass

    # reviews requested or removed
    if event_type == "deployment":
        pass
        # deployment = payload.get("deployment")

    # ignore other events
    return "ok"
