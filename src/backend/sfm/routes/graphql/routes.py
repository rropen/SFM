from sfm.config import get_settings
from sfm.routes.work_items import crud as item_crud
from sfm.routes.projects import crud as project_crud
from sfm.routes.commits import crud as commit_crud
from sfm.routes.metrics import crud as metrics_crud
from sfm.database import engine
from sqlmodel import Session
from fastapi.encoders import jsonable_encoder
import sfm.routes.graphql.schemas as schemas
from graphql import GraphQLError
import graphene
import json
import requests
from sfm.routes.metrics.routes import get_deployments


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

    commits = graphene.List(
        schemas.CommitOutput,
        skip=graphene.Int(),
        limit=graphene.Int(),
        project_id=graphene.Int(),
        project_name=graphene.String(),
        description="List all commits",
    )

    @staticmethod
    def resolve_commits(
        self, info, skip=None, limit=None, project_id=None, project_name=None
    ):
        commits_retrieved = commit_crud.get_all(
            db=Session(engine),
            skip=skip,
            limit=limit,
            project_id=project_id,
            project_name=project_name,
        )
        json_serialized_list = [jsonable_encoder(item) for item in commits_retrieved]
        return json_serialized_list

    get_single_commit = graphene.Field(
        schemas.CommitOutput,
        sha=graphene.String(),
        id=graphene.Int(),
        description="Retrieve a single commit",
    )

    @staticmethod
    def resolve_get_single_commit(self, info, sha=None, id=None):
        if sha is not None and id is None:
            commit_retrieved = commit_crud.get_by_sha(Session(engine), sha)
        elif id is not None and sha is None:
            commit_retrieved = commit_crud.get_by_id(Session(engine), id)
        else:
            raise GraphQLError("Please specify either an ID or a SHA, not both")
        return jsonable_encoder(commit_retrieved)

    deployments = graphene.List(
        schemas.DeploymentOutput,
        project_id=graphene.Int(),
        project_name=graphene.String(),
        description="List all deployments",
    )

    @staticmethod
    def resolve_deployments(self, info, project_id=None, project_name=None):
        deployments_retrieved = [
            metrics_crud.get_deployments_crud(
                Session(engine),
                project_id=project_id,
                project_name=project_name,
            )
        ]
        json_serialized_list = [
            jsonable_encoder(item) for item in deployments_retrieved
        ]
        return json_serialized_list


query = graphene.Schema(query=Query)
