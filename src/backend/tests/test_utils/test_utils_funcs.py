import pytest
from typing import List
from fastapi.testclient import TestClient
from requests.sessions import HTTPAdapter
from sqlmodel import Session, select, and_
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sfm.models import WorkItem, Project, Commit
from sfm.utils import validate_signature, calc_signature
import requests
import json
import os


from sfm.config import get_settings

app_settings = get_settings()


def test_signatures(client: TestClient, db: Session):
    """Clearing database so that id's are easier to test"""
    json_obj = json.load(open("./test_utils/real_payload.json"))
    byte_obj = json.dumps(json_obj).encode("utf-8")
    signature = "jklhnvkljansdkjhvsauhefhoitpyqejknv"

    with pytest.raises(Exception) as ex:
        validate_signature(signature, byte_obj)
        assert ex.value.message == "Github Signature Incorrect"
