import pytest
from typing import List
from fastapi.testclient import TestClient
from requests.sessions import HTTPAdapter
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sfm.models import WorkItem, Project
import json
import os


# get at "/"
def test_webhooks(client: TestClient, db: Session):
    client.delete("utilities/clear_local_db")
    """
        test_int = 0:  repository created,
        test_int = 1:  pull request to dev,
        test_int = 2:  pull request to main not merged,
        test_int = 3:  pull request to main merged,
        test_int = 4:  issue opened,
        test_int = 5:  issue labeled production defect,
        test_int = 6:  issue closed,
        test_int = 7:  issue reopened,
        test_int = 8:  issue unlabeled,
         -- test_int = 9:  deployment, UNUSED
        test_int = 9:  repository renamed,
        test_int = 10: repository deleted,
    """

    # Testing respository created
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 0}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project = db.exec(select(Project).order_by(-Project.id)).first()
    assert project.name == "Webhook Testing Repo"

    # Testing pull_request to dev
    pre_work_item_length = len(db.exec(select(WorkItem)).all())
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 1}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(db.exec(select(WorkItem)).all()) == pre_work_item_length

    # Testing pull_request to main not merged
    pre_work_item_length = len(db.exec(select(WorkItem)).all())
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 2}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(db.exec(select(WorkItem)).all()) == pre_work_item_length

    # Testing pull_request to main merged
    pre_work_item_length = len(db.exec(select(WorkItem)).all())
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 3}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(db.exec(select(WorkItem)).all()) == pre_work_item_length + 1
    pull_request = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert pull_request.category == "Pull Request"
    assert pull_request.start_time == datetime(2021, 9, 1, 12, 0, 0, 0)
    assert pull_request.end_time == datetime(2021, 9, 5, 12, 0, 0, 0)

    # Testing issue opened
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 4}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)

    # Testing issue labeled as production defect
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 5}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time is None
    # TODO: Add test to make sure most recent deployment is flagged as fail

    # Testing issue closed
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 6}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time == datetime(2021, 10, 5, 12, 0, 0, 0)

    # Testing issue reopened
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 7}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time is None

    # Testing issue unlabeled
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 8}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue_still_exists = db.get(WorkItem, issue.id)
    assert issue_still_exists is None
    # TODO: Add test to make sure that most recent deployment has failed flag removed

    # Testing deployment
    # response = client.post("converters/github_webhooks/", json={"test": "test"}, params={"test_int": 9})
    # assert response.status_code == 200
    # print("HERE'S THE RESPONSE: \n", response)
    # assert len(db.exec(select(WorkItem)).all()) == pre_work_item_length+1
    # pull_request = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    # assert pull_request.category == "Deployment"
    # assert pull_request.start_time == datetime(2021, 10, 1, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")
    # assert pull_request.end_time == datetime(2021, 10, 5, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Testing repository renamed
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 9}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project = db.exec(select(Project).order_by(-Project.id)).first()
    assert project.name == "Webhook Testing Repo Renamed"
    assert project.repo_url == "https://github.com/WebhookTestingRepoURL"

    # Testing repository deleted
    response = client.post(
        "converters/github_webhooks/", json={"test": "test"}, params={"test_int": 10}
    )
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project_still_exists = db.get(Project, project.id)
    assert project_still_exists is None

    # .start_time == datetime(2021, 10, 1, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%S.%f")
    # .end_time == datetime(2021, 10, 5, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%S.%f")
    # .start_time == datetime(2021, 10, 1, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")
    # .end_time == datetime(2021, 10, 5, 12, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ")

    # "created_at": "2021-10-01T12:00:00Z"
    # "closed_at": "2021-10-05T12:00:00Z"

    # work_item = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    # work_items = db.exec(select(WorkItem))

    # for item in work_items:
    #     print(item.id, item.category, item.end_time)
    # print(work_item)
    # assert work_item.category == "Pull Request"
    # assert work_item.start_time == "2019-05-15T15:20:33Z"
    # assert work_item.end_time == "2019-05-15T15:24:33Z"
    # assert work_item.project_id == 1
    # assert len(work_item.commits) == 2
    # print(response)


# Projects: 2
# Work Items: 43
# Commits: 8
