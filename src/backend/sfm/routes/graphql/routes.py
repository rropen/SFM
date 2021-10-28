from sfm.config import get_settings
from sfm.routes.work_items import crud as item_crud
from sfm.routes.projects import crud as project_crud
from sfm.routes.commits import crud as commit_crud
from sfm.database import engine
from sqlmodel import Session
from fastapi.encoders import jsonable_encoder
import sfm.routes.graphql.schemas as schemas
from graphql import GraphQLError
import graphene
import json
import requests
from sfm.routes.metrics.routes import get_deployments

test_data = [
    {"first_name": "Tyler", "last_name": "BigShot"},
    {"first_name": "Gabe", "last_name": "Slicer"},
]
test_data_deployments = [
    {
        "project_name": "all",
        "deployment_dates": [
            [1625184000, 2],
            [1625270400, 0],
            [1625356800, 0],
            [1625443200, 0],
            [1625529600, 0],
            [1625616000, 0],
            [1625702400, 0],
            [1625788800, 2],
            [1625875200, 0],
            [1625961600, 0],
            [1626048000, 0],
            [1626134400, 0],
            [1626220800, 1],
            [1626307200, 0],
            [1626393600, 1],
            [1626480000, 0],
            [1626566400, 1],
            [1626652800, 0],
            [1626739200, 1],
            [1626825600, 0],
            [1626912000, 0],
            [1626998400, 1],
            [1627084800, 1],
            [1627171200, 0],
            [1627257600, 0],
            [1627344000, 1],
            [1627430400, 1],
            [1627516800, 0],
            [1627603200, 1],
            [1627689600, 1],
            [1627776000, 1],
            [1627862400, 0],
            [1627948800, 0],
            [1628035200, 0],
            [1628121600, 0],
            [1628208000, 1],
            [1628294400, 0],
            [1628380800, 0],
            [1628467200, 1],
            [1628553600, 0],
            [1628640000, 0],
            [1628726400, 0],
            [1628812800, 1],
            [1628899200, 0],
            [1628985600, 1],
            [1629072000, 0],
            [1629158400, 1],
            [1629244800, 0],
            [1629331200, 0],
            [1629417600, 1],
            [1629504000, 0],
            [1629590400, 1],
            [1629676800, 0],
            [1629763200, 0],
            [1629849600, 0],
            [1629936000, 0],
            [1630022400, 1],
            [1630108800, 1],
            [1630195200, 0],
            [1630281600, 1],
            [1630368000, 1],
            [1630454400, 0],
            [1630540800, 0],
            [1630627200, 1],
            [1630713600, 0],
            [1630800000, 1],
            [1630886400, 0],
            [1630972800, 0],
            [1631059200, 0],
            [1631145600, 0],
            [1631232000, 1],
            [1631318400, 1],
            [1631404800, 3],
            [1631491200, 1],
            [1631577600, 1],
            [1631664000, 0],
            [1631750400, 0],
            [1631836800, 2],
            [1631923200, 0],
            [1632009600, 1],
            [1632096000, 1],
            [1632182400, 0],
            [1632268800, 0],
            [1632355200, 0],
            [1632441600, 0],
            [1632528000, 0],
            [1632614400, 0],
            [1632700800, 0],
            [1632787200, 0],
            [1632873600, 0],
            [1632960000, 0],
            [1633046400, 0],
            [1633132800, 0],
            [1633219200, 0],
            [1633305600, 0],
            [1633392000, 0],
            [1633478400, 0],
            [1633564800, 0],
            [1633651200, 0],
            [1633737600, 0],
            [1633824000, 0],
            [1633910400, 0],
            [1633996800, 0],
            [1634083200, 0],
            [1634169600, 0],
            [1634256000, 0],
            [1634342400, 0],
            [1634428800, 0],
            [1634515200, 0],
            [1634601600, 0],
            [1634688000, 0],
            [1634774400, 0],
            [1634860800, 0],
            [1634947200, 0],
            [1635033600, 0],
            [1635120000, 0],
            [1635206400, 0],
            [1635292800, 0],
            [1635379200, 0],
        ],
        "performance": "Weekly",
        "deployment_dates_description": "List of lists, where each sublist consits of [unix date, number of deploys on that date]",
        "performance_description": "Elite: Multiple deploys per day, High: Between once per day and once per week, Medium: Between once per week and once per month, Low: More than once per month",
    }
]


class Person(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()


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
        # deployments_retrieved = get_deployments(
        #     project_id=project_id,
        #     project_name=project_name,
        #
        # )
        # json_serialized_list = [jsonable_encoder(item) for item in deployments_retrieved]
        # return json_serialized_lisaa
        return test_data_deployments

    person = graphene.List(Person)

    def resolve_person(self, info):
        return test_data


query = graphene.Schema(query=Query)
