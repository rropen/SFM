from sfm.routes.work_items import crud as item_crud
from sfm.routes.projects import crud as project_crud
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
        schemas.WorkItemOutput,
        skip=graphene.Int(),
        limit=graphene.Int(),
        project_id=graphene.Int(),
        project_name=graphene.String(),
        description="List all Work Items",
    )

    @staticmethod
    def resolve_work_items(
        self, info, skip=None, limit=None, project_id=None, project_name=None
    ):
        work_items_retrieved = item_crud.get_all(
            db=Session(engine),
            skip=skip,
            limit=limit,
            project_id=project_id,
            project_name=project_name,
        )
        json_serialized_list = [jsonable_encoder(item) for item in work_items_retrieved]
        return json_serialized_list

    get_single_work_item = graphene.Field(
        schemas.WorkItemOutput,
        id=graphene.NonNull(graphene.Int),
        description="Retrieve a single Work Item",
    )

    @staticmethod
    def resolve_get_single_work_item(self, info, id):
        retrieved_item = item_crud.get_by_id(Session(engine), id)
        return jsonable_encoder(retrieved_item)

    projects = graphene.List(
        schemas.ProjectOutput,
        skip=graphene.Int(),
        limit=graphene.Int(),
        description="List all Projects",
    )

    @staticmethod
    def resolve_projects(self, info, skip=None, limit=None):
        projects_retrieved = project_crud.get_all(Session(engine), skip, limit)
        json_serialized_list = [jsonable_encoder(item) for item in projects_retrieved]
        return json_serialized_list

    get_single_project = graphene.Field(
        schemas.ProjectOutput,
        id=graphene.NonNull(graphene.Int),
        description="Retrieve a single Project",
    )

    @staticmethod
    def resolve_get_single_project(self, info, id):
        retrieved_item = project_crud.get_by_id(Session(engine), id)
        return jsonable_encoder(retrieved_item)


@router.post("/")
def get_work_items_graph(query_str: str = Body(default=None)):
    query = graphene.Schema(query=Query)
    results = query.execute(query_str)
    return results.data
