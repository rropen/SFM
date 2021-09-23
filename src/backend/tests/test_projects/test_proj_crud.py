from fastapi.exceptions import HTTPException
import pytest
from sqlmodel import select
from sqlmodel.main import SQLModel
from sfm.routes.projects import crud
from tests.conftest import hashed_token, engine

from sfm.models import Project, ProjectCreate, ProjectUpdate


# get_all
def test_get_all(init_database):
    """test that the crud function works as expected"""
    response = crud.get_all(init_database)
    assert response is not None
    assert response[0].name == "Test Project 1"
    assert response[0].leadName == "Peter Parker"
    assert response[0].leadEmail == "spider-person@stark.com"
    assert response[0].description == "A test project for testing"
    assert response[0].location == "Strangeville"
    assert response[0].repoUrl == "github.com/starkEnterprises"
    assert response[0].onPrem is False
    assert response[0].projectAuthTokenHashed == hashed_token

    """
    Test that the function raises an error when there are
    no projects in the table
    """
    SQLModel.metadata.drop_all(engine)
    with pytest.raises(Exception) as ex:
        crud.get_all(init_database)
        assert ex.value.message == "Projects not found"


# get_by_id
def test_get_by_id(init_database):
    """test that the crud function works as expected"""
    response = crud.get_by_id(init_database, project_id=1)
    assert response is not None
    assert response.name == "Test Project 1"
    assert response.leadName == "Peter Parker"
    assert response.leadEmail == "spider-person@stark.com"
    assert response.description == "A test project for testing"
    assert response.location == "Strangeville"
    assert response.repoUrl == "github.com/starkEnterprises"
    assert response.onPrem is False
    assert response.projectAuthTokenHashed == hashed_token

    """
    Testing that the crud function raises exception when the project
    does with matching id does not exist in DB
    """
    with pytest.raises(Exception) as ex:
        crud.get_by_id(init_database, project_id=15)
        assert ex.value.message == "Project not found"


# create_project
def test_create(init_database):
    """Testing that the project works as expected"""
    project_data = ProjectCreate(
        **{
            "name": "Test Project 2",
            "leadName": "Patrick Stark",
            "leadEmail": "starfish-person@stark.com",
            "description": "A test project for testing creation",
            "location": "Bikini Gotham",
            "repoUrl": "github.com/crustyEnterprises",
            "onPrem": True,
        }
    )

    response = crud.create_project(init_database, project_data, admin_key="admin_key")

    assert len(response) == 2
    assert response[0].name == "Test Project 2"
    assert response[0].name == "Test Project 2"
    assert response[0].leadName == "Patrick Stark"
    assert response[0].leadEmail == "starfish-person@stark.com"
    assert response[0].description == "A test project for testing creation"
    assert response[0].location == "Bikini Gotham"
    assert response[0].repoUrl == "github.com/crustyEnterprises"
    assert response[0].onPrem is True
    assert response[0].projectAuthTokenHashed is not None

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.create_project(init_database, project_data, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# delete_project
def test_delete_project(init_database):
    """Testing that the crud function works as expected"""
    response = crud.delete_project(init_database, project_id=1, admin_key="admin_key")
    assert response is True
    projects = init_database.exec(select(Project)).all()
    for project in projects:
        assert project.id != 1

    """
    Testing that the crud function raises an exception when the project
    with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.delete_project(init_database, project_id=15, admin_key="admin_key")
        assert ex.value.message == "Project not found"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.delete_project(init_database, project_id=1, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# refresh_project_key
def test_refresh_project_key(init_database):
    """Testing that the crud function works as expected"""
    response = crud.refresh_project_key(
        init_database, project_id=1, admin_key="admin_key"
    )
    assert response is not False
    assert response != "Catalyst"

    # testing that refreshing key did not change project details
    project_test = init_database.get(Project, 1)
    assert project_test.name == "Test Project 1"
    assert project_test.leadName == "Peter Parker"
    assert project_test.leadEmail == "spider-person@stark.com"
    assert project_test.description == "A test project for testing"
    assert project_test.location == "Strangeville"
    assert project_test.repoUrl == "github.com/starkEnterprises"
    assert project_test.onPrem is False

    """
    Testing that the crud function raises an exception when the project
    with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.refresh_project_key(init_database, project_id=15, admin_key="admin_key")
        assert ex.value.message == "Project not found"

    """
    Testing that the project raises an exception when the admin_key
    is incorrect
    """
    with pytest.raises(Exception) as ex:
        crud.refresh_project_key(init_database, project_id=1, admin_key="Shmadmin_key")
        assert ex.value.message == "Credentials are incorrect"


# update_project
def test_update_project(init_database):
    """Testing that the project works as expected"""
    update_dict = {
        "name": "New Test Project 1",
        "leadName": "Strong Squid",
        "repoUrl": "github.com/SquidEnterprises",
    }
    # vvv causes unset params to become default (exclude_unset didnt help)
    updated_project = ProjectUpdate(**update_dict)
    response = crud.update_project(
        init_database, project_id=1, project_data=updated_project, admin_key="admin_key"
    )

    assert response is not None
    assert response.name == "New Test Project 1"
    assert response.leadName == "Strong Squid"
    assert response.leadEmail == "spider-person@stark.com"
    assert response.description == "A test project for testing"
    assert response.location == "Strangeville"
    assert response.repoUrl == "github.com/SquidEnterprises"
    assert response.onPrem is False
    assert response.projectAuthTokenHashed == hashed_token

    """
    Testing that the crud function raises an exception when the
    project with matching id does not exist in the database
    """
    with pytest.raises(Exception) as ex:
        crud.update_project(
            init_database,
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
            init_database,
            project_id=1,
            project_data="placeholder",
            admin_key="Shmadmin_key",
        )
        assert ex.value.message == "Credentials are incorrect"
