import json
from sfm.routes.work_items import crud
from sfm.routes.commits import crud as commit_crud
from sfm.dependencies import get_db
from sfm.models import WorkItemCreate, Project, CommitCreate
from typing import List, Optional
from sqlmodel import Session, select
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request
from sfm.database import engine
from urllib.request import urlopen
import requests
from datetime import datetime
from statistics import median


def deployment_processor(
    db, deployment, project_db, project_auth_token
):  # pragma: no cover
    deployment_dict = {
        "category": "Deployment",
        "end_time": deployment.get("updated_at"),
        "project_id": project_db.id,
    }

    work_item_data = WorkItemCreate(**deployment_dict)
    crud.create_work_item(db, work_item_data, project_auth_token)


def pull_request_processor(
    db, pull_request, project_db, project_auth_token
):  # pragma: no cover

    pull_request_dict = {
        "category": "Pull Request",
        "project_id": project_db.id,
        "start_time": pull_request.get("created_at"),
        "end_time": pull_request.get("merged_at"),
    }

    work_item_data = WorkItemCreate(**pull_request_dict)
    work_item_id = crud.create_work_item(db, work_item_data, project_auth_token)

    # commits_url = pull_request.get("commits_url")
    commits_url = "https://api.github.com/repos/Codertocat/Hello-World/commits"

    json_data = requests.get(commits_url).json()

    for i in range(0, len(json_data)):
        commit_data = json_data[i]
        date = datetime.strptime(
            commit_data["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
        )

        # pass work item id in dictionary to create commit
        commit_dict = {
            "work_item_id": work_item_id,
            "sha": commit_data["sha"],
            "date": date,
            "message": commit_data["commit"]["message"],
            "author": commit_data["commit"]["author"]["name"],
        }

        commit_obj = CommitCreate(**commit_dict)
        commit_crud.create_commit(db, commit_obj, project_auth_token)


router = APIRouter()


@router.post("/github_webhooks/")  # pragma: no cover
async def webhook_handler(
    request: Request,
    project_auth_token: str = Header(...),
    X_GitHub_Event: str = Header(...),  # DELETE ME WHEN DONE
    db: Session = Depends(get_db),
):
    """
    ## Github Webhook Handler

    Awaits incoming payload from Github Webhooks and parses the data.
    Currently, endpoint processes two different event types: "Deployment" and "Pull Request".
    The payload data is parsed and data needed to calculate the DORA metrics is stored in the db tables.
    """
    # handle events
    payload = await request.json()
    event_type = request.headers.get("X-Github-Event")

    # secret_auth_key = request.headers.get("X-Hub-Signature-256")
    event_type = X_GitHub_Event
    print("THE EVENT TYPE:", event_type)

    # gather common payload object properties
    if event_type != "push":  # push events are the exception to common properties
        # action = payload.get("action")
        # sender = payload.get("sender")
        repository = payload.get("repository")
        # organization = payload.get("organization")
        # installation = payload.get("installation")

        print(repository)
    else:
        # TODO: pull in push event information
        pass

    project_name = repository.get("name")
    print(project_name)
    project_db = db.exec(select(Project).where(Project.name == project_name)).first()
    if not project_db:
        raise HTTPException(status_code=404, detail="Matching project not found")

    project_auth_token = request.headers.get("project-auth-key")  # workaround for now

    if event_type == "deployment":
        deployment = payload.get("deployment")
        deployment_processor(db, deployment, project_db, project_auth_token)

    elif event_type == "pull_request":
        pull_request = payload.get("pull_request")
        print(pull_request)
        pull_request_processor(db, pull_request, project_db, project_auth_token)

    return project_name, pull_request
