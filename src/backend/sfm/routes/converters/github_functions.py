import json
import logging

from sfm.routes.work_items import crud as work_item_crud
from sfm.routes.commits import crud as commit_crud
from sfm.routes.projects import crud as project_crud
from sfm.models import (
    WorkItem,
    WorkItemUpdate,
    WorkItemCreate,
    ProjectCreate,
    CommitCreate,
    Project,
    ProjectUpdate,
)
from sfm.database import engine
import requests
from fastapi import HTTPException
from sqlmodel import select, and_
from datetime import datetime
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings
from sfm.logger import create_logger

logger = create_logger(__name__)

app_settings = get_settings()
headers = {"Authorization": f"token {app_settings.GITHUB_API_TOKEN}"}


def webhook_project_processor(db, repo_data, action):
    if action == "created":
        project_create_data = {
            "name": repo_data["name"],
            "repo_url": repo_data["html_url"],
            "description": repo_data["description"],
            "github_id": repo_data["id"],
        }
        project_db = ProjectCreate(**project_create_data)
        [project, _] = project_crud.create_project(
            db, project_db, app_settings.ADMIN_KEY
        )

    elif action == "deleted":
        project = db.exec(
            select(Project).where(Project.name == repo_data["name"])
        ).first()
        if not project:
            logger.debug(
                "Project to be deleted does not have matching entry in database"
            )
        else:
            project_crud.delete_project(db, project.id, app_settings.ADMIN_KEY)

    elif action == "renamed":
        renamed_project = db.exec(
            select(Project).where(Project.github_id == repo_data["id"])
        ).first()
        update_dict = {"name": repo_data["name"]}
        project_update_data = ProjectUpdate(**update_dict)
        project_crud.update_project(
            db, renamed_project.id, project_update_data, app_settings.ADMIN_KEY
        )

    return


def deployment_processor(
    db, deployment, project_db, project_auth_token
):  # pragma: no cover
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
        logger.debug("pull request is not merged, not stored")
        return  # do not store un-merged pull requests
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
    if app_settings.ENV != "test":
        json_data = requests.get(pull_request["commits_url"], headers=headers).json()
    else:
        json_data = json.load(open("./test_converters/testing_files/commits.json"))
        logger.warning("using testing commit data file")

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


def project_processor(db, project, include_list):
    logger.info('func="project_processor" info="entered"')
    if project["name"][0] == ".":
        logger.debug(
            "Project starts with a . or is not in the include list and will not be tracked"
        )
        project_db = "unset"
        proj_auth_token = "unset"
        return project_db, proj_auth_token
    elif include_list is not None and project["name"] not in include_list:
        logger.debug("Project not in the include list and will not be tracked")
        project_db = "unset"
        proj_auth_token = "unset"
        return project_db, proj_auth_token

    project_dict = {
        "name": project["name"],
        "lead_name": project["owner"]["login"],
        "repo_url": project["html_url"],
        "github_id": project["id"],
    }
    project_data = ProjectCreate(**project_dict)
    try:
        [project_db, proj_auth_token] = project_crud.create_project(
            db, project_data, admin_key=app_settings.ADMIN_KEY
        )

    except HTTPException:  # pragma: no cover
        raise Exception(
            "Issue with repeated projects. Clear database and try population again"
        )

    return project_db, proj_auth_token


def deployment_flagger(db, defect_id, proj_auth_token):
    defect = db.get(WorkItem, defect_id)
    deployment = db.exec(
        select(WorkItem)
        .where(
            and_(
                WorkItem.project_id == defect.project_id,
                WorkItem.category == "Pull Request",
                WorkItem.end_time <= defect.start_time,
            )
        )
        .order_by(WorkItem.end_time.desc())
    ).first()

    if deployment is None:
        pass

    # How to handle when there are defects but no pull request before

    update_dict = {"failed": True}
    work_item_update = WorkItemUpdate(**update_dict)
    work_item_crud.update_work_item(
        db, deployment.id, work_item_update, proj_auth_token
    )


def unlabeled_processor(db, issue, proj_auth_token):
    unlabeled_prod_defect_item = db.exec(
        select(WorkItem).where(
            and_(WorkItem.issue_num == issue["number"]),
            (WorkItem.category == "Production Defect"),
        )
    ).first()
    failed_pull_request = db.exec(
        select(WorkItem)
        .where(
            and_(
                WorkItem.project_id == unlabeled_prod_defect_item.project_id,
                WorkItem.category == "Pull Request",
                WorkItem.end_time <= unlabeled_prod_defect_item.start_time,
                WorkItem.failed == True,  # noqa: E712
            )
        )
        .order_by(WorkItem.end_time.desc())
    ).first()
    update_dict = {"failed": None}
    work_item_update = WorkItemUpdate(**update_dict)
    work_item_crud.update_work_item(
        db, failed_pull_request.id, work_item_update, proj_auth_token
    )
    work_item_crud.delete_work_item(db, unlabeled_prod_defect_item.id, proj_auth_token)


def reopened_processor(db, issue, proj_auth_token):
    reopened_item = db.exec(
        select(WorkItem).where(WorkItem.issue_num == issue["number"])
    ).first()
    if not reopened_item:
        logger.warning("No matching WorkItem in db for reopened issue")
        raise HTTPException(  # pragma: no cover
            status_code=404, detail="No matching WorkItem in db for reopened issue"
        )
    comment_string = f'Issue reopened at {issue["updated_at"]},'
    if reopened_item.comments is not None:
        comment_string = comment_string + reopened_item.comments
    update_dict = {
        "end_time": None,
        "comments": comment_string,
    }
    work_item_update = WorkItemUpdate(**update_dict)
    work_item_crud.update_work_item(
        db, reopened_item.id, work_item_update, proj_auth_token
    )


def defect_processor(db, issue, project, proj_auth_token, closed=False):
    # closed=True signifies this was a "closed" event and not a "labeled" event

    issue_number = issue["number"]
    # if closed is true, set the existing defect end_time to the closed_at time and exit the function
    if closed is True:
        existing_issue = db.exec(
            select(WorkItem).where(
                and_(
                    WorkItem.category == "Production Defect",
                    WorkItem.issue_num == issue_number,
                )
            )
        ).first()

        if existing_issue is None:
            logger.debug("Defect with matching issue number does not exist")
            raise HTTPException(  # pragma: no cover
                status_code=404,
                detail="Defect with matching issue number does not exist",
            )

        update_defect_dict = {"end_time": issue["closed_at"]}
        work_item_update = WorkItemUpdate(**update_defect_dict)
        work_item_crud.update_work_item(
            db, existing_issue.id, work_item_update, proj_auth_token
        )
        logger.debug("Defect updated with new end_time")

        return

    # otherwise, go through the function and create a new workItem with the category of "Production Defect"
    state = issue["state"]
    open_time = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")

    # used for backpopulation purposes. Only happens if flagged event is already closed.
    if state == "closed":
        closed_time = datetime.strptime(issue["closed_at"], "%Y-%m-%dT%H:%M:%SZ")
    elif state == "open":
        closed_time = None
    else:
        pass

    create_defect_dict = {
        "category": "Production Defect",
        "issue_num": issue_number,
        "start_time": open_time,
        "end_time": closed_time,
        "project_id": project.id,
    }

    work_item_data = WorkItemCreate(**create_defect_dict)
    defect_id = work_item_crud.create_work_item(db, work_item_data, proj_auth_token)

    deployment_flagger(db, defect_id, proj_auth_token)


def populate_past_github(db, org, include_list):  # noqa: C901
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

    if app_settings.GITHUB_API_TOKEN in ["", "XXXXXXXXXXX"]:  # pragma: no cover
        raise HTTPException(
            status_code=412,
            detail="Missing github api token.  Please specify GITHUB_API_TOKEN and try again",
        )

    assert app_settings.ENV != ""

    if app_settings.ENV != "test":  # pragma: no cover
        # response = requests.get("https://api.github.com/rate_limit", headers=headers)
        # logger.debug(f"{response}")
        # print("GitHub API RATE LIMIT INFO:", response.json()["rate"])
        # print(app_settings.ENV)
        org_data = requests.get(
            f"https://api.github.com/orgs/{org}", headers=headers
        ).json()
        org_data_string = str(org_data["repos_url"])
        repo_data = requests.get(org_data_string, headers=headers).json()

    else:
        org_data = json.load(open("./test_converters/testing_files/org_data.json"))
        repo_data = json.load(open("./test_converters/testing_files/testing_repo.json"))

    key_dict = {}
    repo_list = [repo["name"] for repo in repo_data]
    # proj_not_found_in_repo = [set(include_list) - set(repo_list)]
    if include_list is not None:
        for proj in include_list:
            if proj not in repo_list:
                raise HTTPException(
                    status_code=404, detail=f"{proj} does not exist in {org}"
                )

    for repo in repo_data:
        logger.debug(f'Entered repo loop with repo name = {repo["name"]}')
        project_exist = db.exec(
            select(Project).where(Project.name == repo["name"])
        ).first()

        if project_exist and repo["name"] in key_dict.keys():
            proj_auth_token = key_dict[repo["name"]]
            project = project_exist
        else:
            project, proj_auth_token = project_processor(db, repo, include_list)

        if project == "unset":
            continue

        if project is False:
            logger.error("Project was not properly created")
            continue

        key_dict[repo["name"]] = proj_auth_token

        if app_settings.ENV != "test":  # pragma: no cover
            event_request_str = str(repo["events_url"])
            max_pages = 10
            page_num = 0
            end_of_results = False
            events = []
            while end_of_results is False and page_num < max_pages:
                params = {"state": "all", "per_page": 100, "page": page_num}
                result = requests.get(
                    event_request_str, headers=headers, params=params
                ).json()
                for data in result:
                    events.append(data)
                end_of_results = len(result) < 100
                page_num += 1
        else:
            events = json.load(open("./test_converters/testing_files/events.json"))

        # event_types = [event["type"] for event in events]
        # logger.info(f'HERES THE EVENTS {event_types}')
        for event in reversed(events):
            logger.debug(f'"Entered event loop with event name = {event["type"]}"')
            if event["type"] == "PullRequestEvent":
                if (
                    event["payload"]["pull_request"]["head"]["repo"]["default_branch"]
                    == "main"
                ):  # only process pulls to main
                    pull_request_processor(
                        db, event["payload"]["pull_request"], project, proj_auth_token
                    )

        if app_settings.ENV != "test":  # pragma: no cover
            issue_events_str = str(repo["issue_events_url"])
            issue_events_str = issue_events_str.split("{")[0]
            issue_events = requests.get(issue_events_str, headers=headers).json()
        else:
            issue_events = json.load(
                open("./test_converters/testing_files/issue_events.json")
            )

        # Find the flagged events in the issue events and send them for processing and storage
        for i_event in reversed(issue_events):
            logger.debug(
                f'"Entered labeled event loop with event name = {i_event["event"]}"'
            )
            if (
                i_event["event"] == "labeled"
                and i_event["label"]["name"] == "production defect"
            ):
                defect_processor(
                    db, i_event["issue"], project, proj_auth_token, closed=False
                )

        # Second time through the issue events, this time looking for any closed events to set end times for
        # issues that were created with "labeled" events in the first loop through
        for i_event in reversed(issue_events):
            logger.debug(
                f'"Entered closed event loop with event name = {i_event["event"]}"'
            )
            label_names = [label["name"] for label in i_event["issue"]["labels"]]
            if i_event["event"] == "closed" and "production defect" in label_names:
                defect_processor(
                    db, i_event["issue"], project, proj_auth_token, closed=True
                )

    proj_intended_not_found = []
    # If a project is in the database already with a matching name,
    if include_list is not None:
        in_database = db.exec(select(Project)).all()
        project_names_in_db = [proj.name for proj in in_database]
        proj_intended_not_found = list(set(include_list) - set(project_names_in_db))

    return proj_intended_not_found
