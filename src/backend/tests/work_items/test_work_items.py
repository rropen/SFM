from fastapi.testclient import TestClient
from sqlmodel import Session
from sfm.routes.work_items import crud, routes
from sfm.routes.projects import crud as proj_crud
import pytest
import os
from sfm.models import WorkItemCreate


def test_get_all(init_database):
    response = crud.get_all(init_database, skip=0, limit=10)
    print(response)
    assert len(response) == 1


def test_create(init_database):
    work_item_data = WorkItemCreate(**{"category": "Deployment", "project_id": 1})
    response = crud.create_work_item(
        init_database, work_item_data, project_auth_token="Catalyst"
    )
    assert isinstance(response, int)


def test_work_item_in_DB(init_database):
    response = crud.get_by_id(init_database, 1)
    assert response is not None


def test_work_item_not_DB(init_database):
    response = crud.get_by_id(init_database, 2)
    print(response)
    assert response is None


def test_issues_not_in_file(init_database):
    files = os.listdir(".")
    assert "issues.db" not in files
