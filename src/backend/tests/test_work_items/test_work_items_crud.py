from typing import List
from fastapi.testclient import TestClient
from sqlmodel import Session
from sfm.routes.work_items import crud
from sfm.routes.projects import crud as proj_crud
import pytest
import os
from sfm.models import WorkItemCreate, WorkItem, WorkItemUpdate
import datetime
import sqlalchemy


def test_work_item_not_DB(db):
    with pytest.raises(Exception) as ex:
        crud.get_by_id(db, 2)
        assert ex.value.message == "Item not found"


def test_get_all(db):
    # Test no project specification returns all items
    response = crud.get_all(db, skip=0, limit=1000)
    assert len(response) == 43  # limited by limit
    assert type(response) == list
    workitem = response[0]
    assert workitem.category == "Deployment"
    assert workitem.issue_num is None
    assert workitem.start_time == datetime.datetime(2021, 8, 23, 9, 37, 17, 94309)
    assert workitem.end_time == datetime.datetime(2021, 9, 23, 9, 37, 17, 94309)
    assert workitem.duration_open == 2678400
    assert workitem.comments == "Test description for test work item in the database"
    assert workitem.project_id == 1
    assert workitem.project.name == "Test Project 1"
    assert workitem.id == 1

    # Test giving project id returns the correct project work items
    response = crud.get_all(db, skip=0, limit=1000, project_id=1)
    assert len(response) == 35
    assert type(response) == list
    workitem = response[0]
    assert workitem.project_id == 1

    # Test giving project name returns the correct project work items
    response = crud.get_all(db, skip=0, limit=1000, project_name="Test Project 1")
    assert len(response) == 35
    assert type(response) == list
    workitem = response[0]
    assert workitem.project_id == 1

    # Test giving project name AND project id returns the correct project work items
    response = crud.get_all(
        db, skip=0, limit=1000, project_name="Test Project 1", project_id=1
    )
    assert len(response) == 35
    assert type(response) == list
    workitem = response[0]
    assert workitem.project_id == 1

    # Test giving mismatching project name AND project id alerts user
    with pytest.raises(Exception) as ex:
        response = crud.get_all(
            db,
            skip=0,
            limit=10,
            project_name="Test Project 1",
            project_id=20,
        )
        assert ex.value.message == "Project not found"

    # Test giving non-existant project name alerts user
    with pytest.raises(Exception) as ex:
        response = crud.get_all(db, skip=0, limit=10, project_name="Wrong Project")
        assert ex.value.message == "Project not found"

    # Test giving non-existant project id alerts user
    with pytest.raises(Exception) as ex:
        response = crud.get_all(db, skip=0, limit=10, project_id=20)
        assert ex.value.message == "Project not found"


def test_get_by_id(db):
    # Test calling existing work item returns expected data
    response = crud.get_by_id(db, 1)
    assert response is not None
    assert type(response) is WorkItem
    workitem = response
    assert workitem.category == "Deployment"
    assert workitem.issue_num is None
    assert workitem.start_time == datetime.datetime(2021, 8, 23, 9, 37, 17, 94309)
    assert workitem.end_time == datetime.datetime(2021, 9, 23, 9, 37, 17, 94309)
    assert workitem.duration_open == 2678400
    assert workitem.comments == "Test description for test work item in the database"
    assert workitem.project_id == 1
    assert workitem.project.name == "Test Project 1"
    assert workitem.id == 1

    # Test calling non-existant work item
    with pytest.raises(Exception) as ex:
        response = crud.get_by_id(db, 2)
        assert ex.value.message == "Item not found"


def test_create_work_item(db):
    # Test creating a work item returns all data inputted
    work_item_data = WorkItemCreate(
        **{
            "category": "Issue",
            "issue_num": 1,
            "start_time": datetime.datetime(2021, 8, 11, 10, 15, 16, 94309),
            "end_time": datetime.datetime(2021, 8, 13, 10, 15, 16, 94309),
            "duration_open": int(
                (
                    datetime.datetime(2021, 8, 13, 10, 15, 16, 94309)
                    - datetime.datetime(2021, 8, 11, 10, 15, 16, 94309)
                ).total_seconds()
            ),
            "comments": "test comment here",
            "project_id": 1,
        }
    )
    response = crud.create_work_item(db, work_item_data, project_auth_token="Catalyst1")
    assert isinstance(response, int)
    assert response == 44
    workitem = db.get(WorkItem, response)
    assert workitem.category == "Issue"
    assert workitem.issue_num == 1
    assert workitem.start_time == datetime.datetime(2021, 8, 11, 10, 15, 16, 94309)
    assert workitem.end_time == datetime.datetime(2021, 8, 13, 10, 15, 16, 94309)
    assert workitem.duration_open == 172800
    assert workitem.comments == "test comment here"
    assert workitem.project_id == 1
    assert workitem.project.name == "Test Project 1"

    # Test that wrong project token throws exception
    with pytest.raises(Exception) as ex:
        response = crud.create_work_item(
            db, work_item_data, project_auth_token="WrongToken"
        )
        assert ex.value.message == "Credentials are incorrect"

    # Test that wrong project ID throws exception
    work_item_data = WorkItemCreate(**{"category": "Issue", "project_id": 15})

    with pytest.raises(Exception) as ex:
        response = crud.create_work_item(
            db, work_item_data, project_auth_token="Catalyst"
        )
        assert ex.value.message == "Credentials are incorrect"

    # Test that category not in the enum throws exception
    with pytest.raises(Exception) as ex:
        work_item_data = WorkItemCreate(
            **{"category": "WrongCategory", "project_id": 1}
        )
        response = crud.create_work_item(
            db, work_item_data, project_auth_token="Catalyst1"
        )
        assert "value is not a valid enumeration member" in ex.value.message


# Test delete_work_item
def test_delete_work_item(db):
    # Test exception thrown for non-existant work item
    with pytest.raises(Exception) as ex:
        response = crud.delete_work_item(db, 15, project_auth_token="Catalyst1")
        assert ex.value.message == "Item not found"

    # Test exception thrown when project auth token does not match work item's project
    with pytest.raises(Exception) as ex:
        response = crud.delete_work_item(db, 1, project_auth_token="WrongProject")
        assert ex.value.message == "Project not found"

    # Test item is properly deleted
    response = crud.delete_work_item(db, 1, project_auth_token="Catalyst1")
    assert response is True
    assert db.get(WorkItem, 1) is None


# Test update_work_item
def test_update_work_item(db):
    # Test updates get tracked in db
    work_item_data = WorkItemUpdate(
        **{
            "category": "Pull Request",
            "issue_num": 2,
            "start_time": datetime.datetime(2021, 7, 23, 9, 37, 17, 94309),
            "end_time": datetime.datetime(2021, 8, 23, 9, 37, 17, 94309),
            "comments": "different comment",
            "project_id": 1,
        }
    )
    response = crud.update_work_item(
        db, 1, work_item_data, project_auth_token="Catalyst1"
    )
    assert type(response) == WorkItem
    workitem = response
    assert workitem.category == "Pull Request"
    assert workitem.issue_num == 2
    assert workitem.start_time == datetime.datetime(2021, 7, 23, 9, 37, 17, 94309)
    assert workitem.end_time == datetime.datetime(2021, 8, 23, 9, 37, 17, 94309)
    assert workitem.comments == "different comment"
    assert workitem.project_id == 1
    assert workitem.project.name == "Test Project 1"

    # Test unset parameters do not get overwritten
    work_item_data = WorkItemUpdate(
        **{"category": "Issue", "comments": "new different comment"}
    )

    response = crud.update_work_item(
        db, 1, work_item_data, project_auth_token="Catalyst1"
    )

    assert type(response) == WorkItem
    workitem = response
    assert workitem.category == "Issue"
    assert workitem.issue_num == 2
    assert workitem.start_time == datetime.datetime(2021, 7, 23, 9, 37, 17, 94309)
    assert workitem.end_time == datetime.datetime(2021, 8, 23, 9, 37, 17, 94309)
    assert workitem.comments == "new different comment"
    assert workitem.project_id == 1
    assert workitem.project.name == "Test Project 1"

    response = crud.update_work_item(
        db, 1, work_item_data, project_auth_token="Catalyst1"
    )

    with pytest.raises(Exception) as ex:
        response = crud.update_work_item(
            db, 15, work_item_data, project_auth_token="Catalyst1"
        )
        assert ex.value.message == "Item not found"

    with pytest.raises(Exception) as ex:
        response = crud.update_work_item(
            db, 1, work_item_data, project_auth_token="WrongProject"
        )
        assert ex.value.message == "Credentials are incorrect"
