import json

from sfm.utils import validate_signature, calc_signature
from sfm.dependencies import get_db
from sfm.models import WorkItemCreate, Project, CommitCreate, WorkItem, WorkItemUpdate
from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request, Query
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings
from sfm.logger import create_logger
from .github_functions import (
    webhook_project_processor,
    deployment_processor,
    pull_request_processor,
    populate_past_github,
    defect_processor,
    reopened_processor,
    unlabeled_processor,
)

app_settings = get_settings()


logger = create_logger(__name__)


router = APIRouter()


def fetch_github_payload(request):
    raw = request.body()
    signature = request.headers.get("X-Hub-Signature-256")
    proj_auth_token = validate_signature(signature, raw)

    payload = request.json()

    event_type = request.headers.get("X-Github-Event")

    return payload, event_type, proj_auth_token


@router.post("/github_webhooks/")  # pragma: no cover
async def webhook_handler(request: Request, db: Session = Depends(get_db)):
    """
    ## Github Webhook Handler

    Awaits incoming payload from Github Webhooks and parses the data.
    Currently, endpoint processes two different event types: "Deployment" and "Pull Request".
    The payload data is parsed and data needed to calculate the DORA metrics is stored in the db tables.
    """

    if app_settings.GITHUB_WEBHOOK_SECRET in ["", "XXXXXXXXXXX"]:
        raise HTTPException(
            status_code=412,
            detail="Missing github webhook secret. Please specify GITHUB_WEBHOOK_SECRET and try again",
        )

    # if app_settings.ENV != "test":
    payload, event_type, proj_auth_token = fetch_github_payload(request)

    # gather common payload object properties
    if event_type != "push":  # push events are the exception to common properties
        repository = payload.get("repository")

    else:  # TODO: pull in push event information
        pass

    if event_type != "repository":
        project_name = repository.get("name")
        print("THE PROJECT NAME: ", project_name)
        project_db = db.exec(
            select(Project).where(Project.name == project_name)
        ).first()

        if not project_db:
            logger.debug("A matching project was not found in the database")
            raise HTTPException(
                status_code=404, detail="Matching project not found in db"
            )

    if event_type == "repository":
        action = payload.get("action")
        webhook_project_processor(db, repository, action)

    elif event_type == "deployment":
        deployment = payload.get("deployment")
        deployment_processor(db, deployment, project_db, proj_auth_token)

    elif event_type == "pull_request":
        pull_request = payload.get("pull_request")
        if (
            pull_request["head"]["repo"]["default_branch"] == "main"
        ):  # process only pull requests to main
            pull_request_processor(db, pull_request, project_db, proj_auth_token)

    elif event_type == "issues":
        action = payload.get("action")
        issue = payload.get("issue")
        if action == "closed":
            defect_processor(db, issue, project_db, proj_auth_token, closed=True)
        elif action == "labeled" and "production defect" in [
            lbl["name"] for lbl in issue["labels"]
        ]:
            defect_processor(db, issue, project_db, proj_auth_token, closed=False)
        elif action == "reopened":
            reopened_processor(db, issue, proj_auth_token)
        elif action == "unlabeled" and "production defect" not in [
            lbl["name"] for lbl in issue["labels"]
        ]:
            unlabeled_processor(db, issue, proj_auth_token)
        else:
            logger.debug("Issues event type passed that is unhandled")

    else:
        logger.warning("Event type not handled")
        return {"code": "event type not handled"}
        # raise HTTPException(status_code=404, detail="Event type not handled.")

    return {"code": "success"}


@router.get("/github_populate")
def populate_past_data(
    org: str,
    db: Session = Depends(get_db),
    include_only_list: Optional[List[str]] = Query(None),
):
    """
    ## Github Backpopulate

    Queries the GitHub API to populate projects and work items that already exist in specified repos.
    "include_only_list" is a list of repo names (as strings) that you wish use to populate the database.
    If "include_only_list" is populated, only projects in this list will be populated
    """
    proj_intended_not_found = populate_past_github(db, org, include_only_list)

    in_database = db.exec(select(Project)).all()
    proj_name_in_db = [proj.name for proj in in_database]

    not_found_projects = []
    if include_only_list is not None:
        for repo in include_only_list:
            if repo not in proj_name_in_db:
                not_found_projects.append(repo)

    if proj_intended_not_found != [] or not_found_projects != []:  # pragma: no cover
        included_projects = []
        for proj in include_only_list:
            if proj not in proj_intended_not_found and proj in proj_name_in_db:
                included_projects.append(proj)
        return {
            "projects_included": included_projects,
            "projects_not_included": proj_intended_not_found,
            "project_not_found": not_found_projects,
        }
    else:
        return {"code": "success"}
