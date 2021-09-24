import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime

# get at "/"
def test_get_all_endpoint(client: TestClient, db: Session):
    response = client.get("/workItems/")
    assert response is not None
    print(response.json())
    ob = [
        {
            "category": "Deployment",
            # "startTime": '2021-08-23 09:37:17.094309',
            "startTime": datetime(2021, 8, 23, 9, 37, 17, 94309),
            "endTime": "2021-09-23 09:37:17.094309",
            "durationOpen": "31 days, 0:00:00",
            "comments": "Test description for test work item in the database",
            "projectId": 1,
            "id": 1,
        }
    ]
    print(ob)
    assert response.json() == [
        {
            "category": "Deployment",
            # "startTime": '2021-08-23 09:37:17.094309',
            "startTime": datetime(2021, 8, 23, 9, 37, 17, 94309),
            "endTime": "2021-09-23 09:37:17.094309",
            "durationOpen": "31 days, 0:00:00",
            "comments": "Test description for test work item in the database",
            "projectId": 1,
            "id": 1,
        }
    ]


# get at "/{project_id}"


# post at "/"


# delete at "/{project_id}"


# post at "/{project_id}"


# patch at "/{project_id}"
