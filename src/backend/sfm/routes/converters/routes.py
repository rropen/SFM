import json
import logging
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
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings
from .github_functions import (
    deployment_processor,
    pull_request_processor,
    populate_past_github,
)

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
    logger.info('method="POST" path="converters/github_webhooks"')
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

    else:
        # TODO: pull in push event information
        pass

    project_name = repository.get("name")
    project_db = db.exec(select(Project).where(Project.name == project_name)).first()
    if not project_db:
        logger.warning(
            'method=POST path="converters/github_webhooks" warning="Matching project not found"'
        )
        raise HTTPException(status_code=404, detail="Matching project not found")

    project_auth_token = request.headers.get("project-auth-key")  # workaround for now

    if event_type == "deployment":
        deployment = payload.get("deployment")
        deployment_processor(db, deployment, project_db, project_auth_token)

    elif event_type == "pull_request":
        pull_request = payload.get("pull_request")
        pull_request_processor(db, pull_request, project_db, project_auth_token)

    else:
        logger.warning(
            'method=POST path="converters/github_webhooks" warning="Event type not handled."'
        )
        raise HTTPException(status_code=404, detail="Event type not handled.")

    return project_name, pull_request


@router.get("/github_populate")
def populate_past_data(org: str, db: Session = Depends(get_db)):
    populate_past_github(db, org)
    return {"code": "success"}
