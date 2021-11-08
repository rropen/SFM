import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select, and_
from datetime import datetime
from tests.test_converters.mock_converter_functions import (
    mock_parse_github_for_repo_data,
    mock_parse_github_for_issue_events,
    mock_parse_github_for_events,
    mock_get_commit_data,
)
from sfm.models import WorkItem, Project, Commit
from sfm.config import get_settings

app_settings = get_settings()


def test_github_backpopulate(client: TestClient, db: Session, mocker):
    mocker.patch(
        "sfm.routes.converters.github_functions.parse_github_for_repo_data",
        return_value=mock_parse_github_for_repo_data(),
    )
    mocker.patch(
        "sfm.routes.converters.github_functions.parse_github_for_issue_events",
        return_value=mock_parse_github_for_issue_events(),
    )
    mocker.patch(
        "sfm.routes.converters.github_functions.parse_github_for_events",
        return_value=mock_parse_github_for_events(),
    )
    mocker.patch(
        "sfm.routes.converters.github_functions.get_commit_data",
        return_value=mock_get_commit_data(),
    )

    """Clearing database so that id's are easier to test"""
    print(app_settings.ENV)
    response = client.get(
        "/converters/github_populate",
        params={"org": "rropen", "include_only_list": ["testing", ".nope"]},
    )

    print(response)
    assert response.status_code == 200

    project = db.exec(select(Project).where(Project.name == "testing")).first()
    assert project is not None

    pull_requests = db.exec(
        select(WorkItem).where(
            and_(WorkItem.project_id == project.id, WorkItem.category == "Pull Request")
        )
    ).all()
    assert len(pull_requests) == 3

    print(pull_requests[0].id)
    print(pull_requests[0].project.name)
    print(db.exec(select(Commit).where(Commit.work_item_id == 44)).all())
    commits = db.exec(
        select(Commit).where(Commit.work_item_id == pull_requests[0].id)
    ).all()
    assert len(commits) == 1
    assert commits[0].sha == "6c25310a034145701775e620895c7b36d16fc1c4"
    assert commits[0].work_item_id == 46
    assert commits[0].time_to_pull == 373

    defects = db.exec(
        select(WorkItem).where(WorkItem.category == "Production Defect")
    ).all()
    assert len(defects) == 3
    assert defects[1].issue_num == 5
    assert defects[1].start_time == datetime(2021, 10, 11, 15, 17, 35, 0)
    assert defects[1].end_time == datetime(2021, 10, 11, 15, 22, 33, 0)
    assert defects[1].duration_open == int(
        (
            datetime(2021, 10, 11, 15, 22, 33, 0)
            - datetime(2021, 10, 11, 15, 17, 35, 0)
        ).total_seconds()
    )

    failed_deploy1 = db.get(WorkItem, 47)
    failed_deploy2 = db.get(WorkItem, 48)

    assert failed_deploy1.failed is True
    assert failed_deploy2.failed is True

    response = client.get(
        "/converters/github_populate",
        params={"org": "rropen", "include_only_list": ["Nope"]},
    )
    assert response.status_code == 404
