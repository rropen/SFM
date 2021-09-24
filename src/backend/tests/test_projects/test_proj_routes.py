import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

# get at "/"
def test_get_all_endpoint(client: TestClient, db: Session):
    response = client.get("/projects/")
    assert response is not None
    assert response.json() == [
        {
            "name": "Test Project 1",
            "lead_name": "Peter Parker",
            "lead_email": "spider-person@stark.com",
            "description": "A test project for testing",
            "location": "Strangeville",
            "repo_url": "github.com/starkEnterprises",
            "on_prem": False,
            "id": 1,
        }
    ]


# get at "/{project_id}"


# post at "/"


# delete at "/{project_id}"


# post at "/{project_id}"


# patch at "/{project_id}"
