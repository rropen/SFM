import pytest
from typing import List
from fastapi.testclient import TestClient
from requests.sessions import HTTPAdapter
from sqlmodel import Session
from datetime import datetime, timedelta
from fastapi import HTTPException

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
    assert len(response.json()) == 35
    work_item = response.json()[0]
    assert work_item["category"] == "Deployment"

    # Test giving project name returns only data in that project
    response = client.get("/workItems/?project_name=Test%20Project%202")
    assert len(response.json()) == 8
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
        response = client.get("/workItems/200")
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
        "id": 44,
    }


# delete at "/{work_item_id}"
def test_work_item_delete(client: TestClient, db: Session):
    # Test deleting an existing work item works
    response = client.delete(
        "/workItems/1", headers={"project-auth-token": "Catalyst1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "message": "WorkItem 1 Deleted",
    }

    # Test that trying to delete a non-existant work item returns correct response
    with pytest.raises(Exception) as ex:
        response = client.delete(
            "/workItems/200", headers={"project-auth-token": "Catalyst1"}
        )
        assert response.status_code == 404
        assert ex.value.message == "Item not found"


# patch at "/{work_item_id}"
def test_work_item_patch(client: TestClient, db: Session):
    # Test patching an existing work item works
    work_item_data = {
        "category": "Issue",
        "comments": "Here's some comments",
        "project_id": 1,
    }

    response = client.patch(
        "/workItems/1", work_item_data, headers={"project-auth-token": "Catalyst1"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "code": "success",
        "id": 1,
    }

    # Test that trying to patch a non-existant work item returns correct response
    with pytest.raises(Exception) as ex:
        response = client.patch(
            "/workItems/200", headers={"project-auth-token": "Catalyst1"}
        )
        assert response.status_code == 404
        assert ex.value.message == "Item not found"
