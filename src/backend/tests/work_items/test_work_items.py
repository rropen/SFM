from fastapi.testclient import TestClient
from sqlmodel import Session
from tests.conftest import engine
from sfm.routes.work_items import crud, routes


def test_get_all(test_app):
    response = crud.get_all(Session(engine), skip=0, limit=10)
    print(response)
    assert len(response) == 10
