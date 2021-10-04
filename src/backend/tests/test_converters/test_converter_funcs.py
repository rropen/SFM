import pytest
from typing import List
from fastapi.testclient import TestClient
from requests.sessions import HTTPAdapter
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sfm.models import WorkItem, Project, Commit
import requests
import json
import os


# def test_github_backpopulate(client: TestClient,db: Session):
#     """Clearing database so that id's are easier to test"""
#     response = client.get("/converters/github_populate", params={"org": "rropen", "repo": "testing"})
#     assert response.status_code == 200

#     project = db.exec(select(Project).where(Project.name == "testing")).first()
#     assert project is not None

#     pull_requests = db.exec(select(WorkItem).where(WorkItem.project_id == project.id)).all()
#     assert len(pull_requests) == 1

#     commits = db.exec(select(Commit).where(Commit.work_item_id == pull_requests[0].id)).all()
#     assert len(commits) == 1
#     assert commits[0].sha == "6c25310a034145701775e620895c7b36d16fc1c4"
#     assert commits[0].work_item_id == 44
#     assert commits[0].time_to_pull == timedelta()
