import pytest
from typing import List
from fastapi.testclient import TestClient
from requests.sessions import HTTPAdapter
from sqlmodel import Session, select
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from sfm.models import WorkItem
import json
import os
from tests.test_converters.pull_request_file import input_json


# get at "/"
# def test_webhooks(client: TestClient, db: Session):

#     input_obj = json.loads(input_json)
#     print("Input_obj type:\n", type(input_obj))
#     #response_body = Request(input_obj, headers={"project-auth-token": "Catalyst1", "X-GitHub-Event":"pull_request"})
#     #response = client.post("/github_webhooks/", response_body)
#     #response = client.post("/github_webhooks/", response_body)
#     response = client.post(webhook_handler.__name__, json=input_obj, headers={"project-auth-token": "Catalyst1", "X-GitHub-Event":"pull_request"})
#     print(response)
#     print("HERE'S THE RESPONSE: \n", response)

#     work_item = db.exec(select(WorkItem).order_by(-WorkItem.id)).first()
#     work_items = db.exec(select(WorkItem))
#     for item in work_items:
#         print(item.id, item.category, item.end_time)
#     print(work_item)
#     assert work_item.category == "Pull Request"
#     assert work_item.start_time == "2019-05-15T15:20:33Z"
#     assert work_item.end_time == "2019-05-15T15:24:33Z"
#     assert work_item.project_id == 1
#     assert len(work_item.commits) == 2
#     print(response)


# Projects: 2
# Work Items: 43
# Commits: 8
