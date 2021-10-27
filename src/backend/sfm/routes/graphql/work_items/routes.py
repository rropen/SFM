from sfm.routes.work_items import crud
import json
from sfm.database import engine
from sfm.dependencies import get_db
from sfm.models import WorkItemRead, WorkItemCreate, WorkItemUpdate
from typing import List, Optional
from sqlmodel import Session
from fastapi import APIRouter, HTTPException, Depends, Path, Header, Body
from fastapi.encoders import jsonable_encoder
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
import graphene
import sfm.routes.graphql.schemas as schemas
from sfm.config import get_settings

router = APIRouter()


class Query(graphene.ObjectType):
    work_items = graphene.List(
        schemas.WorkItemGraph,
        skip=graphene.Int(default_value=0),
        limit=graphene.Int(default_value=100),
        project_id=graphene.Int(default_value=None),
        project_name=graphene.String(default_value=None),
    )

    def resolve_work_items(self, info, skip, limit):
        work_items_retrieved = crud.get_all(
            db=Session(engine), skip=skip, limit=limit, project_id=1, project_name=None
        )
        json_serialized_list = [jsonable_encoder(item) for item in work_items_retrieved]
        return json_serialized_list


@router.post("/")
def get_work_items_graph(query_str: str = Body(default=None)):
    query = graphene.Schema(query=Query)
    results = query.execute(query_str)
    return results.data
