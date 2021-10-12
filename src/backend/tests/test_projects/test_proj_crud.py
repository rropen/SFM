from fastapi.exceptions import HTTPException
import pytest
from sqlmodel import select, Session
from sqlmodel.main import SQLModel
from sfm.routes.projects import crud
from tests.conftest import hashed_token1, hashed_token2

from sfm.models import Project, ProjectCreate, ProjectUpdate


# get_all
def test_get_all(db, session: Session):
    """test that the crud function works as expected"""
    response = crud.get_all(db)
    assert response is not None
    assert response[0].name == "Test Project 1"
    assert response[0].lead_name == "Peter Parker"
    assert response[0].lead_email == "spider-person@stark.com"
    assert response[0].description == "A test project for testing"
    assert response[0].location == "Strangeville"
    assert response[0].repo_url == "github.com/starkEnterprises"
    assert response[0].on_prem is False
    assert response[0].project_auth_token_hashed == hashed_token1

    assert response[1].name == "Test Project 2"
    assert response[1].lead_name == "Sergio Garcia"
    assert response[1].lead_email == "team-europe@pga.com"
    assert response[1].description == "A second test project for testing"
    assert response[1].location == "Kohler"
    assert response[1].repo_url == "github.com/pgaGolf"
    assert response[1].on_prem is False
    assert response[1].project_auth_token_hashed == hashed_token2

    """
    Test that the function raises an error when there are
    no projects in the table
    """
    session.delete(session.get(Project, 1))
    session.delete(session.get(Project, 2))
    session.commit()
    # SQLModel.metadata.drop_all(engine)
    with pytest.raises(Exception) as ex:
        crud.get_all(db)
        assert ex.value.message == "Projects not found"


# get_by_id
def test_get_by_id(db):
    """test that the crud function works as expected"""
    response = crud.get_by_id(db, project_id=1)
    assert response is not None
    assert response.name == "Test Project 1"
    assert response.lead_name == "Peter Parker"
    assert response.lead_email == "spider-person@stark.com"
    assert response.description == "A test project for testing"
    assert response.location == "Strangeville"
    assert response.repo_url == "github.com/starkEnterprises"
    assert response.on_prem is False
    assert response.project_auth_token_hashed == hashed_token1

    """
    Testing that the crud function raises exception when the project
    does with matching id does not exist in DB
    """
    with pytest.raises(Exception) as ex:
        crud.get_by_id(db, project_id=15)
        assert ex.value.message == "Project not found"


# create_project
def test_create(db):
    """Testing that the project works as expected"""
    project_data = ProjectCreate(
        **{
            "name": "Test Project 2",
            "lead_name": "Patrick Stark",
            "lead_email": "starfish-person@stark.com",
            "description": "A test project for testing creation",
            "location": "Bikini Gotham",
            "repo_url": "github.com/crustyEnterprises",
            "on_prem": True,
        }
    )

    response = crud.create_project(db, project_data, admin_key="admin_key")

    assert len(response) == 2
    assert response[0].name == "Test Project 2"
    assert response[0].lead_name == "Patrick Stark"
    assert response[0].lead_email == "starfish-person@stark.com"
    assert response[0].description == "A test project for testing creation"
    assert response[0].location == "Bikini Gotham"
    assert response[0].repo_url == "github.com/crustyEnterprises"
    assert response[0].on_prem is True
    assert response[0].project_auth_token_hashed is not None

    """
    Testing that the function raises an error if the project name already
    exists in the database
    """
    with pytest.raises(Exception) as ex:
        crud.delete_project(db, project_id=1, admin_key="admin_key")
        assert ex.value.message == "Database entry already exists"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.create_project(db, project_data, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# delete_project
def test_delete_project(db):
    """Testing that the crud function works as expected"""
    response = crud.delete_project(db, project_id=1, admin_key="admin_key")
    assert response is True
    projects = db.exec(select(Project)).all()
    for project in projects:
        assert project.id != 1

    """
    Testing that the crud function raises an exception when the project
    with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.delete_project(db, project_id=15, admin_key="admin_key")
        assert ex.value.message == "Project not found"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.delete_project(db, project_id=1, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# refresh_project_key
def test_refresh_project_key(db):
    """Testing that the crud function works as expected"""
    response = crud.refresh_project_key(db, project_id=1, admin_key="admin_key")
    assert response is not False
    assert response != "Catalyst"

    # testing that refreshing key did not change project details
    project_test = db.get(Project, 1)
    assert project_test.name == "Test Project 1"
    assert project_test.lead_name == "Peter Parker"
    assert project_test.lead_email == "spider-person@stark.com"
    assert project_test.description == "A test project for testing"
    assert project_test.location == "Strangeville"
    assert project_test.repo_url == "github.com/starkEnterprises"
    assert project_test.on_prem is False

    """
    Testing that the crud function raises an exception when the project
    with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.refresh_project_key(db, project_id=15, admin_key="admin_key")
        assert ex.value.message == "Project not found"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.refresh_project_key(db, project_id=1, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# update_project
def test_update_project(db):
    """Testing that the project works as expected"""
    update_dict = {
        "name": "New Test Project 1",
        "lead_name": "Strong Squid",
        "repo_url": "github.com/SquidEnterprises",
    }
    # vvv causes unset params to become default (exclude_unset didnt help)
    updated_project = ProjectUpdate(**update_dict)
    response = crud.update_project(
        db, project_id=1, project_data=updated_project, admin_key="admin_key"
    )

    assert response is not None
    assert response.name == "New Test Project 1"
    assert response.lead_name == "Strong Squid"
    assert response.lead_email == "spider-person@stark.com"
    assert response.description == "A test project for testing"
    assert response.location == "Strangeville"
    assert response.repo_url == "github.com/SquidEnterprises"
    assert response.on_prem is False
    assert response.project_auth_token_hashed == hashed_token1

    """
    Testing that the crud function raises an exception when the
    project with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.update_project(
            db,
            project_id=15,
            project_data="placeholder",
            admin_key="admin_key",
        )
        assert ex.value.message == "Project not found"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.update_project(
            db,
            project_id=1,
            project_data="placeholder",
            admin_key="Shmadmin_key",
        )
        assert ex.value.message == "Credentials are incorrect"
