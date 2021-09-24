import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime

# get at "/"
# def test_get_all_endpoint(client: TestClient, db: Session):
#    response = client.get("/workItems/")
#    assert response is not None
#    print(response.json())
#    ob = [
#        {
#            "category": "Deployment",
#            # "start_time": '2021-08-23 09:37:17.094309',
#            "start_time": datetime(2021, 8, 23, 9, 37, 17, 94309),
#            "end_time": "2021-09-23 09:37:17.094309",
#            "duration_open": "31 days, 0:00:00",
#            "comments": "Test description for test work item in the database",
#            "project_id": 1,
#            "id": 1,
#        }
#    ]
#    print(ob)
#    assert response.json() == [
#        {
#            "category": "Deployment",
#            # "start_time": '2021-08-23 09:37:17.094309',
#            "start_time": datetime(2021, 8, 23, 9, 37, 17, 94309),
#            "end_time": "2021-09-23 09:37:17.094309",
#            "duration_open": "31 days, 0:00:00",
#            "comments": "Test description for test work item in the database",
#            "project_id": 1,
#            "id": 1,
#        }
#    ]


# get at "/{project_id}"


# post at "/"


# delete at "/{project_id}"


# post at "/{project_id}"


# patch at "/{project_id}"
