import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import datetime
from sfm.models import WorkItem, Project

from tests.test_converters.mock_converter_functions import (
    mock_fetch_github_payload,
    mock_get_commit_data,
)

# get at "/"
"""
# NOTE: using "session" fixture instead of "db" to use a blank database so we can avoid calling
#       delete database call which relies engine which is created in database.py which relies on
#       DATABASE_URL and doesnt correctly work in test which needs a memory sqlite database.
"""


def test_webhooks(client: TestClient, session: Session, mocker):
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

    mocker.patch(
        "sfm.routes.converters.github_functions.get_commit_data",
        return_value=mock_get_commit_data(),
    )

    # Testing respository created
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=0),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project = session.exec(select(Project).order_by(-Project.id)).first()
    assert project.name == "Webhook Testing Repo"

    # Testing pull_request to dev
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=1),
    )
    pre_work_item_length = len(session.exec(select(WorkItem)).all())
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(session.exec(select(WorkItem)).all()) == pre_work_item_length

    # Testing pull_request to main not merged.
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=2),
    )
    pre_work_item_length = len(session.exec(select(WorkItem)).all())
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(session.exec(select(WorkItem)).all()) == pre_work_item_length

    # Testing pull_request to main merged
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=3),
    )
    pre_work_item_length = len(session.exec(select(WorkItem)).all())
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    assert len(session.exec(select(WorkItem)).all()) == pre_work_item_length + 1
    pull_request = session.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert pull_request.category == "Pull Request"
    assert pull_request.start_time == datetime(2021, 9, 1, 12, 0, 0, 0)
    assert pull_request.end_time == datetime(2021, 9, 5, 12, 0, 0, 0)

    # Testing issue opened
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=4),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)

    # Testing issue labeled as production defect
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=5),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = session.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time is None
    recent_pull_request = session.exec(
        select(WorkItem)
        .where(WorkItem.category == "Pull Request")
        .order_by(-WorkItem.id)
    ).first()
    assert recent_pull_request.failed is True

    # Testing issue closed
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=6),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = session.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time == datetime(2021, 10, 5, 12, 0, 0, 0)

    # Testing issue reopened
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=7),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue = session.exec(select(WorkItem).order_by(-WorkItem.id)).first()
    assert issue.category == "Production Defect"
    assert issue.start_time == datetime(2021, 10, 1, 12, 0, 0, 0)
    assert issue.end_time is None

    # Testing issue unlabeled
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=8),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    issue_still_exists = session.get(WorkItem, issue.id)
    assert issue_still_exists is None
    recent_pull_request = session.exec(
        select(WorkItem)
        .where(WorkItem.category == "Pull Request")
        .order_by(-WorkItem.id)
    ).first()
    assert recent_pull_request.failed is None

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
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=9),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project = session.exec(select(Project).order_by(-Project.id)).first()
    assert project.name == "Webhook Testing Repo Renamed"
    assert project.repo_url == "https://github.com/WebhookTestingRepoURL"

    # Testing repository deleted
    mocker.patch(
        "sfm.routes.converters.routes.fetch_github_payload",
        return_value=mock_fetch_github_payload(test_int=10),
    )
    response = client.post("converters/github_webhooks/", json={"test": "test"})
    assert response.status_code == 200
    print("HERE'S THE RESPONSE: \n", response)
    project_still_exists = session.get(Project, project.id)
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
