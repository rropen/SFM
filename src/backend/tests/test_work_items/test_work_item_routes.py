import pytest
from typing import List
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime, timedelta

# get at "/"
def test_get_all_endpoint(client: TestClient, db: Session):
    response = client.get("/workItems/")
    assert response is not None
    assert response.status_code == 200

    work_item = response.json()[0]

    assert work_item["category"] == "Deployment"
    assert work_item["start_time"] == datetime(2021, 8, 23, 9, 37, 17, 94309).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )
    assert work_item["end_time"] == datetime(2021, 9, 23, 9, 37, 17, 94309).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )
    assert work_item["duration_open"] == timedelta(days=31).total_seconds()
    assert (
        work_item["comments"] == "Test description for test work item in the database"
    )
    assert work_item["project_id"] == 1
    assert work_item["id"] == 1

    work_item = response.json()[1]

    assert work_item["category"] == "Pull Request"
    assert work_item["start_time"] == datetime(2021, 7, 23, 9, 37, 17, 94309).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )
    assert work_item["end_time"] == datetime(2021, 8, 23, 9, 37, 17, 94309).strftime(
        "%Y-%m-%dT%H:%M:%S.%f"
    )
    assert work_item["duration_open"] == timedelta(days=31).total_seconds()
    assert (
        work_item["comments"]
        == "new Test description for test work item in the database"
    )
    assert work_item["project_id"] == 2
    assert work_item["id"] == 2

    # Testing giving project id returns only data in that project
    response = client.get("/workItems/?project_id=1")
    print(response.json())
    assert len(response.json()) == 1
    work_item = response.json()[0]
    assert work_item["category"] == "Deployment"

    # Test giving project name returns only data in that project
    response = client.get("/workItems/?project_name=Test%20Project%202")
    assert len(response.json()) == 1
    work_item = response.json()[0]
    assert work_item["category"] == "Pull Request"

    # Test mismatching project name and ID returns no items
    with pytest.raises(Exception) as ex:
        response = client.get(
            "/workItems/?project_name=Test%20Project%202&project_id=1"
        )
        assert ex.value.message == "WorkItems not found"


# get at "/{work_item_id}"
def test_work_item_id_endpoint(client: TestClient, db: Session):
    # Test getting a valid work item returns desired response
    response = client.get("/workItems/1")
    assert response.status_code == 200

    # Test getting a non-existant work item throws exception
    with pytest.raises(Exception) as ex:
        response = client.get("/workItems/15")
        assert ex.value.message == "WorkItem not found"


# post at "/"
def test_work_item_post(client: TestClient, db: Session):
    # Test creating a new work item returns desired response
    input_obj = {
        "category": "Issue",
        "start_time": datetime(2021, 8, 23, 9, 37, 17, 94309).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        ),
        "end_time": datetime(2021, 9, 23, 9, 37, 17, 94309).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        ),
        "comments": "Here's some comments",
        "project_id": 2,
    }
    response = client.post(
        "/workItems/", json=input_obj, headers={"project-auth-token": "Catalyst2"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "id": 3,
    }

    # Test getting a non-existant work item throws exception
    with pytest.raises(Exception) as ex:
        response = client.get("/workItems/15")
        assert ex.value.message == "WorkItem not found"

    # ------------------------------------------------------------------
    ############################ STOPPED HERE #########################
    # ------------------------------------------------------------------


# delete at "/{project_id}"


# post at "/{project_id}"


# patch at "/{project_id}"
