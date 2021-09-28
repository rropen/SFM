import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.conftest import hashed_token1

# get at "/"
def test_get_all_endpoint(client: TestClient, db: Session):
    """Testing the endpoint works as expected"""
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
        },
        {
            "name": "Test Project 2",
            "lead_name": "Sergio Garcia",
            "lead_email": "team-europe@pga.com",
            "description": "A second test project for testing",
            "location": "Kohler",
            "repo_url": "github.com/pgaGolf",
            "on_prem": False,
            "id": 2,
        },
        {
            "name": "Test Project with no WorkItems",
            "lead_name": "Sergio Manuel",
            "lead_email": "team-europe@pga.com",
            "description": "A third test project for testing",
            "location": "Kohler",
            "repo_url": "github.com/pgaGolf",
            "on_prem": False,
            "id": 3,
        },
    ]


# get at "/{project_id}"
def test_get_proj_id(client: TestClient, db: Session):
    """Testing the endpoint works as expected"""
    response = client.get("/projects/1")
    assert response is not None
    assert response.json() == {
        "name": "Test Project 1",
        "lead_name": "Peter Parker",
        "lead_email": "spider-person@stark.com",
        "description": "A test project for testing",
        "location": "Strangeville",
        "repo_url": "github.com/starkEnterprises",
        "on_prem": False,
        "id": 1,
    }

    """Testing that the endpoint raises exception when string passed"""
    response = client.get("projects/asddfda")
    assert response.status_code == 422


# post at "/"
def test_create_proj_endpoint(client: TestClient, db: Session):
    """Testing endpoint works as expected"""
    create_proj = {
        "name": "Test Project Create",
        "location": "Testingville",
        "repo_url": "github.com/testingHub",
        "on_prem": "True",
    }
    response = client.post(
        "/projects/", json=create_proj, headers={"admin-key": "admin_key"}
    )
    assert response.status_code == 200

    """Testing endpoint return if not input object not as expected"""
    incomp_proj = create_proj.pop("on_prem")
    response2 = client.post(
        "/projects/", json=incomp_proj, headers={"admin-key": "admin_key"}
    )
    assert response2.status_code == 422

    """Testing endpoint raises exception when no input data"""
    with pytest.raises(Exception) as ex:
        response = client.post("/projects/", headers={"admin-key": "admin_key"})
        assert ex.value.message == "Project data not provided"

    """Testing endpoint returns unsuccessful response code when no admin-key header"""
    response3 = client.post("/projects/", json=create_proj)
    assert response3.status_code == 422


# delete at "/{project_id}"
def test_delete_proj_endpoint(client: TestClient, db: Session):
    """Testing endpoint works as expected"""
    response = client.delete("/projects/1", headers={"admin-key": "admin_key"})
    assert response.status_code == 200

    """Testing endpoint raises exception when trying to delete non-existent project"""
    with pytest.raises(Exception) as ex:
        client.delete("projects/1", headers={"admin-key": "admin_key"})
        assert ex.value.message == "Project not found"


# post at "/{project_id}"
def test_refresh_proj_token(client: TestClient, db: Session):
    """Testing endpoint works as expected"""
    response = client.post("/projects/1", headers={"admin-key": "admin_key"})
    assert response.status_code == 200
    assert response.json()["code"] == "success"
    assert response.json()["token"] != hashed_token1


# patch at "/{project_id}"
def test_patch_proj_endpoint(client: TestClient, db: Session):
    update_body = {"location": "Wisconsin"}
    response = client.patch(
        "/projects/1", json=update_body, headers={"admin-key": "admin_key"}
    )
    assert response.status_code == 200
    assert response.json() == {"code": "success", "id": 1}
