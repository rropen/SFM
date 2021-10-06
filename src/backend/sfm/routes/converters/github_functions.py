import json
import logging
from sfm.routes.work_items import crud as work_item_crud
from sfm.routes.commits import crud as commit_crud
from sfm.routes.projects import crud as project_crud
from sfm.dependencies import get_db
from sfm.models import WorkItemCreate, ProjectCreate, CommitCreate
from sfm.database import engine
from urllib.request import urlopen
import requests
from datetime import datetime
from statistics import median
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings

app_settings = get_settings()
headers = {"Authorization": f"token {app_settings.GITHUB_API_TOKEN}"}

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=app_settings.AZURE_LOGGING_CONN_STR)
)


response = requests.get("https://api.github.com/rate_limit", headers=headers)
print("GitHub API RATE LIMIT INFO:", response.json()["rate"])


def deployment_processor(
    db, deployment, project_db, project_auth_token
):  # pragma: no cover
    logger.info("")
    deployment_dict = {
        "category": "Deployment",
        "end_time": deployment.get("updated_at"),
        "project_id": project_db.id,
    }

    work_item_data = WorkItemCreate(**deployment_dict)
    work_item_crud.create_work_item(db, work_item_data, project_auth_token)


def pull_request_processor(
    db, pull_request, project_db, project_auth_token
):  # pragma: no cover

    if pull_request["merged"] is False:
        return  # do not store un-merged pull requests
    print(pull_request["merged"])
    print(pull_request["created_at"])
    print(pull_request["merged_at"])
    pull_request_dict = {
        "category": "Pull Request",
        "project_id": project_db.id,
        "start_time": datetime.strptime(
            pull_request["created_at"], "%Y-%m-%dT%H:%M:%SZ"
        ),
        "end_time": datetime.strptime(pull_request["merged_at"], "%Y-%m-%dT%H:%M:%SZ"),
    }

    work_item_data = WorkItemCreate(**pull_request_dict)
    work_item_id = work_item_crud.create_work_item(
        db, work_item_data, project_auth_token
    )

    # commits_url = "https://api.github.com/repos/Codertocat/Hello-World/commits"

    json_data = requests.get(pull_request["commits_url"], headers=headers).json()

    for i in range(0, len(json_data)):
        commit_data = json_data[i]
        date = datetime.strptime(
            commit_data["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
        )

        # pass work item id in dictionary to create commit
        print(commit_data["sha"])
        commit_dict = {
            "work_item_id": work_item_id,
            "sha": commit_data["sha"],
            "date": date,
            "message": commit_data["commit"]["message"],
            "author": commit_data["commit"]["author"]["name"],
        }

        commit_obj = CommitCreate(**commit_dict)
        commit_crud.create_commit(db, commit_obj, project_auth_token)


def project_processor(db, project):
    project_dict = {
        "name": project["name"],
        "lead_name": project["owner"]["login"],
        "repo_url": project["html_url"],
    }

    project_data = ProjectCreate(**project_dict)
    [project_db, proj_auth_token] = project_crud.create_project(
        db, project_data, admin_key=app_settings.ADMIN_KEY
    )

    return project_db, proj_auth_token


def populate_past_github(db, org):
    """
    PSEUDOCODE:
        - 1. Query github api for org string that was passed
        - 2. Query repos(projects) in that organization via the repos_url
            - a. Create a Project for each repo via the project processor
        - 3. For each repo(project), query events url
        - 4. Loop through each event and pass to cooresponding processor by event type
            - a. For each pull_request, check merge with main through github endpoint call
                    1. If merged with main, query the commits_url
            - b. Create a commit workItem for each commit in the commits_url
        - 5. When an issue is LABELED with "production defect" start a timer for time to recover service
            - a. This timer stops when the issue is closed
                -i. (not easy and possible improvement) timer stops when verified issue is fixed
            - b. This marks the MOST RECENT deploy as a failure
    """

    org_data = requests.get(
        f"https://api.github.com/orgs/{org}", headers=headers
    ).json()
    repo_data = requests.get(org_data["repos_url"]).json()

    for repo in repo_data:
        project, proj_auth_token = project_processor(db, repo)

        events = requests.get(repo["events_url"], headers=headers).json()
        for event in events:
            if event["type"] == "PullRequestEvent":
                if (
                    event["payload"]["pull_request"]["head"]["repo"]["default_branch"]
                    == "main"
                ):  # only process pulls to main
                    pull_request_processor(
                        db, event["payload"]["pull_request"], project, proj_auth_token
                    )

            # elif event["type"] == "":
            #     deployment_processor(event["payload"]["deployment"])
