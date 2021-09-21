from fastapi.testclient import TestClient
from sqlmodel import Session
from tests.conftest import engine, test_db_session as db
from sfm.routes.work_items import crud, routes
from sfm.routes.projects import crud as proj_crud

from sfm.models import WorkItemCreate

"""
def test_get_all(test_app, db):
    response = crud.get_all(db, skip=0, limit=10)
    print(response)
    assert len(response) == 10


def test_create(test_app, db):
    work_item_data = WorkItemCreate(**{"category": "Deployment", "project_id": 1})
    response = crud.create_work_item(
        db, work_item_data, project_auth_token="l~$~Xv111j1O2H$_&0uo"
    )
    assert isinstance(response, int)
"""
