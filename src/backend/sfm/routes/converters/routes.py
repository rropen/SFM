from sfm.routes.work_items import crud
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate, Project
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine

# Create a database connection we can use
def get_db():
    with Session(engine) as db:
        yield db


def deployment_processor(db, deployment, project_db, project_auth_token):
    deployment_dict = {
        "category": "Deployment",
        "end_time": deployment.get("updated_at"),
        "project_id": project_db.id,
    }

    work_item_data = WorkItemCreate(**deployment_dict)
    crud.create_work_item(db, work_item_data, project_auth_token)

    print("this is a deployment")


router = APIRouter()


@router.post("/webhook_events/")
async def webhook_handler(
    request: Request,
    # project_auth_token: str = Header(...),
    db: Session = Depends(get_db),
):
    # handle events
    payload = await request.json()
    event_type = request.headers.get("X-Github-Event")
    # secret_auth_key = request.headers.get("X-Hub-Signature-256")

    print("THE EVENT TYPE:", event_type)

    # gather common payload object properties
    if event_type != "push":  # push events are the exception to common properties
        action = payload.get("action")
        # sender = payload.get("sender")
        repository = payload.get("repository")
        # organization = payload.get("organization")
        # installation = payload.get("installation")

    else:
        # TODO: pull in push event information
        pass

    project_name = repository.get("name")
    project_db = db.exec(select(Project).where(Project.name == project_name)).first()
    if not project_db:
        raise HTTPException(status_code=404, detail="Matching project not found")

    project_auth_token = request.headers.get("project-auth-key")  # workaround for now

    if event_type == "deployment":
        deployment = payload.get("deployment")
        deployment_processor(db, deployment, project_db, project_auth_token)

    ### issue processor psuedo-code
    # elif event_type == "issues":
    #     issue = payload.get("issue")
    #     if action == "created":
    #         issue_create(db, issue, project_db, project_auth_token)
    #     else:
    #         issue_close(db, issue, project_db, project_auth_token)

    # ignore other events for now, add as needed
    return action
