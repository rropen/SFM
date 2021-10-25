import json
import logging

from sfm.utils import validate_signature, calc_signature
from sfm.dependencies import get_db
from sfm.models import WorkItemCreate, Project, CommitCreate, WorkItem, WorkItemUpdate
from typing import List, Optional
from sqlmodel import Session, select, and_
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Request, Query
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings
from .github_functions import (
    webhook_project_processor,
    deployment_processor,
    pull_request_processor,
    project_processor,
    deployment_flagger,
    populate_past_github,
    defect_processor,
    reopened_processor,
    unlabeled_processor,
)

app_settings = get_settings()

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string="InstrumentationKey=" + app_settings.AZURE_LOGGING_CONN_STR
    )
)


router = APIRouter()


@router.post("/github_webhooks/")  # pragma: no cover
async def webhook_handler(
    request: Request, db: Session = Depends(get_db), test_int: Optional[int] = None
):
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

    logger.info('method="POST" path="converters/github_webhooks"')
    # handle events

    if app_settings.ENV == "test":
        file_list = [
            ["./test_converters/testing_files/wh_repo_created.json", "repository"],
            [
                "./test_converters/testing_files/wh_pull_request_dev.json",
                "pull_request",
            ],
            [
                "./test_converters/testing_files/wh_pull_request_main_not_merged.json",
                "pull_request",
            ],
            [
                "./test_converters/testing_files/wh_pull_request_main_merged.json",
                "pull_request",
            ],
            [
                "./test_converters/testing_files/wh_issue_opened.json",
                "issues",
            ],  # not currently important until flow metrics
            ["./test_converters/testing_files/wh_issue_labeled_prodDef.json", "issues"],
            ["./test_converters/testing_files/wh_issue_closed.json", "issues"],
            ["./test_converters/testing_files/wh_issue_reopened.json", "issues"],
            ["./test_converters/testing_files/wh_issue_unlabeled.json", "issues"],
            # ["./test_converters/testing_files/wh_deployment.json", "deployment"],
            ["./test_converters/testing_files/wh_repo_renamed.json", "repository"],
            ["./test_converters/testing_files/wh_repo_deleted.json", "repository"],
        ]
        payload = json.load(open(file_list[test_int][0]))
        proj_auth_token = app_settings.GITHUB_WEBHOOK_SECRET
        event_type = file_list[test_int][1]

    if app_settings.ENV != "test":
        raw = await request.body()
        signature = request.headers.get("X-Hub-Signature-256")
        proj_auth_token = validate_signature(signature, raw)

        payload = await request.json()

        event_type = request.headers.get("X-Github-Event")

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
            logger.warning(
                'method=POST path="converters/github_webhooks" warning="Matching project not found in db"'
            )
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
            logger.info(
                'method=POST path="converters/github_webhooks" info="Issues event type that is unhandled is passed"'
            )

    else:
        logger.warning(
            'method=POST path="converters/github_webhooks" warning="Event type not handled."'
        )
        return {"code": "event type not handled"}
        # raise HTTPException(status_code=404, detail="Event type not handled.")

    return {"code": "success"}


@router.get("/github_populate")
def populate_past_data(
    org: str,
    db: Session = Depends(get_db),
    include_only_list: Optional[List[str]] = Query(None),
):
    not_included_projects = populate_past_github(db, org, include_only_list)
    if not_included_projects != []:  # pragma: no cover
        included_projects = []
        for proj in include_only_list:
            if proj not in not_included_projects:
                included_projects.append(proj)
        return {
            "projects_included": included_projects,
            "projects_not_found": not_included_projects,
        }
    else:
        return {"code": "success"}
