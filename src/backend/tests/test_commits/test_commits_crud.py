from typing import List
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from sfm.routes.commits import crud
import pytest
import os
from sfm.models import (
    WorkItemCreate,
    WorkItem,
    WorkItemUpdate,
    Commit,
    CommitCreate,
    CommitUpdate,
)
import datetime
import sqlalchemy


def test_commit_not_DB(db):
    with pytest.raises(Exception) as ex:
        crud.get_by_sha(db, 2)
        assert ex.value.message == "Item not found"


def test_get_all(db):
    # Test no project specification returns all items
    response = crud.get_all(db, skip=0, limit=10)
    assert len(response) == 9
    assert type(response) == list
    commit = response[0]
    assert commit.sha == "daffasdfsjfoie3039j33j882ji2jhsdaf"
    assert commit.date == datetime.datetime(2021, 9, 10, 9, 43, 8, 41351)
    assert commit.message == "feat(test): test commit message for testing commit"
    assert commit.author == "Spider-boy"
    assert commit.work_item_id == 1
    assert commit.time_to_pull == int(
        (datetime.timedelta(days=12, seconds=86049, microseconds=52958)).total_seconds()
    )

    # Test giving project id returns the correct project commits
    response = crud.get_all(db, skip=0, limit=10, project_id=1)
    assert len(response) == 5
    assert type(response) == list
    print(response)
    work_item_id = response[0].work_item_id
    work_item = db.get(WorkItem, work_item_id)
    assert work_item.project_id == 1

    # Test giving project name returns the correct project work items
    response = crud.get_all(db, skip=0, limit=10, project_name="Test Project 1")
    assert len(response) == 5
    assert type(response) == list
    print(response)
    work_item_id = response[0].work_item_id
    work_item = db.get(WorkItem, work_item_id)
    assert work_item.project_id == 1

    # Test giving project name AND project id returns the correct project work items
    response = crud.get_all(
        db, skip=0, limit=10, project_name="Test Project 1", project_id=1
    )
    assert len(response) == 5
    assert type(response) == list
    print(response)
    work_item_id = response[0].work_item_id
    work_item = db.get(WorkItem, work_item_id)
    assert work_item.project_id == 1

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


def test_get_by_sha(db):
    # Test calling existing commit returns expected data
    response = crud.get_by_sha(db, "daffasdfsjfoie3039j33j882ji2jhsdaf")
    assert response is not None
    assert type(response) is Commit
    commit = response
    assert commit.sha == "daffasdfsjfoie3039j33j882ji2jhsdaf"
    assert commit.date == datetime.datetime(2021, 9, 10, 9, 43, 8, 41351)
    assert commit.message == "feat(test): test commit message for testing commit"
    assert commit.author == "Spider-boy"
    assert commit.work_item_id == 1
    assert commit.time_to_pull == int(
        (datetime.timedelta(days=12, seconds=86049, microseconds=52958)).total_seconds()
    )

    # Test calling non-existant commit
    with pytest.raises(Exception) as ex:
        response = crud.get_by_id(db, "ladsjkflasjkdaldsfjl234lfdahfa")
        assert ex.value.message == "Item not found"


def test_create_commit(db):
    # Test creating a commit returns all data inputted
    commit_data = CommitCreate(
        **{
            "sha": "faslkuvczberwe2975jinvcui",
            "date": datetime.datetime(2021, 8, 11, 9, 43, 8, 41351),
            "message": "feat(test): a new commit message",
            "author": "Spider-girl",
            "work_item_id": 1,
        }
    )
    response = crud.create_commit(db, commit_data, project_auth_token="Catalyst1")
    assert isinstance(response, str)
    assert response == "faslkuvczberwe2975jinvcui"
    commit = db.exec(select(Commit).where(Commit.sha == response)).first()
    assert commit.sha == "faslkuvczberwe2975jinvcui"
    assert commit.date == datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
    assert commit.message == "feat(test): a new commit message"
    assert commit.author == "Spider-girl"
    assert commit.work_item_id == 1
    assert commit.time_to_pull == int(
        (
            datetime.datetime(2021, 9, 23, 9, 37, 17, 94309)
            - datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
        ).total_seconds()
    )

    # Test that wrong project token throws exception
    with pytest.raises(Exception) as ex:
        response = crud.create_commit(db, commit_data, project_auth_token="WrongToken")
        assert ex.value.message == "Credentials are incorrect"

    # Test that wrong project ID throws exception
    commit_data = WorkItemCreate(**{"category": "Issue", "project_id": 2})

    with pytest.raises(Exception) as ex:
        response = crud.create_commit(db, commit_data, project_auth_token="Catalyst1")
        assert ex.value.message == "Credentials are incorrect"

    # Test that category not in the enum throws exception
    with pytest.raises(Exception) as ex:
        commit_data = WorkItemCreate(**{"category": "WrongCategory", "project_id": 1})
        response = crud.create_commit(db, commit_data, project_auth_token="Catalyst1")
        assert "value is not a valid enumeration member" in ex.value.message


# Test delete_commit
def test_delete_commit(db):
    # Test exception thrown for non-existant commit
    with pytest.raises(Exception) as ex:
        response = crud.delete_commit(
            db, "akdfjlaqeworuoifa123", project_auth_token="Catalyst1"
        )
        assert ex.value.message == "Item not found"

    # Test exception thrown when project auth token does not match commit's project
    with pytest.raises(Exception) as ex:
        response = crud.delete_commit(
            db,
            "daffasdfsjfoie3039j33j882ji2jhsdaf",
            project_auth_token="WrongProject",
        )
        assert ex.value.message == "Project not found"

    # Test item is properly deleted
    response = crud.delete_commit(
        db,
        "daffasdfsjfoie3039j33j882ji2jhsdaf",
        project_auth_token="Catalyst1",
    )
    assert response is True
    assert db.get(Commit, "daffasdfsjfoie3039j33j882ji2jhsdaf") is None


# Test update_commit
def test_update_commit(db):
    # Test updates get tracked in db
    commit_data = CommitUpdate(
        **{
            "date": datetime.datetime(2021, 8, 11, 9, 43, 8, 41351),
            "message": "feat(test): a new commit message",
            "author": "Spider-girl",
        }
    )
    response = crud.update_commit(
        db,
        "daffasdfsjfoie3039j33j882ji2jhsdaf",
        commit_data,
        project_auth_token="Catalyst1",
    )
    assert type(response) == Commit
    assert response.sha == "daffasdfsjfoie3039j33j882ji2jhsdaf"
    commit = db.exec(select(Commit).where(Commit.sha == response.sha)).first()
    assert commit.date == datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
    assert commit.message == "feat(test): a new commit message"
    assert commit.author == "Spider-girl"
    assert commit.work_item_id == 1
    assert commit.time_to_pull == int(
        (
            datetime.datetime(2021, 9, 23, 9, 37, 17, 94309)
            - datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
        ).total_seconds()
    )

    # Test unset parameters do not get overwritten
    commit_data = CommitUpdate(**{"message": "update message", "author": "new author"})

    response = crud.update_commit(
        db,
        "daffasdfsjfoie3039j33j882ji2jhsdaf",
        commit_data,
        project_auth_token="Catalyst1",
    )

    assert type(response) == Commit
    commit = db.exec(select(Commit).where(Commit.sha == response.sha)).first()
    assert commit.date == datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
    assert commit.message == "update message"
    assert commit.author == "new author"
    assert commit.work_item_id == 1
    assert commit.time_to_pull == int(
        (
            datetime.datetime(2021, 9, 23, 9, 37, 17, 94309)
            - datetime.datetime(2021, 8, 11, 9, 43, 8, 41351)
        ).total_seconds()
    )

    # test that updating a non-existant item alerts user
    with pytest.raises(Exception) as ex:
        response = crud.update_commit(
            db,
            "oiauydfebvauioeq",
            commit_data,
            project_auth_token="Catalyst1",
        )
        assert ex.value.message == "Item not found"

    # test that using wrong project auth token throws exception
    with pytest.raises(Exception) as ex:
        response = crud.update_commit(
            db,
            "daffasdfsjfoie3039j33j882ji2jhsdaf",
            commit_data,
            project_auth_token="WrongProject",
        )
        assert ex.value.message == "Credentials are incorrect"
