from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer

# from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware
from starlette_graphene3 import GraphQLApp, make_graphiql_handler
import os
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

from sfm.dependencies import has_access
from sfm.models import *
from sfm.routes.work_items import routes as work_items
from sfm.routes.projects import routes as projects
from sfm.routes.converters import routes as converters
from sfm.routes.metrics import routes as metrics
from sfm.routes.utilities import routes as utilities
from sfm.routes.graphql.routes import query
from sfm.routes import root
from sfm.logger import create_logger
from .config import get_settings

# This is how you can get access to environment configuration values throughout the application
# Then app_settings.ENV or app_settings.CONN_STR.  See config.py for possible values.
app_settings = get_settings()

logger = create_logger(__name__)

# this file will always be called with __name__ == "sfm.main" (even in docker container)
# create_db_and_tables()

description = "<h2>Software Factory Metrics</h2><br><blockquote>A custom app built by the Software Factory to generate DORA metrics which are a key concept in the move towards DevSecOps.</blockquote>"
app = FastAPI(
    debug=os.environ.get("DEBUG"),
    title="SFM API",
    description=description,
    version="0.1.0",
    dependencies=[Depends(has_access)],
)


# assert app_settings.ENV != "unset"  # mandate ENV value
assert app_settings.ENV in ("test", "local", "development", "production")
assert app_settings.SECRET_KEY != "unset"  # mandate SECRET_KEY value
assert app_settings.ADMIN_KEY != "unset"  # mandate ADMIN_KEY value
assert app_settings.FRONTEND_URL != "unset"  # mandate FRONTEND_URL value
assert app_settings.GITHUB_API_TOKEN != "unset"  # mandate GITHUB_API_TOKEN value
if app_settings.ENV in ["development", "production"]:
    assert app_settings.DATABASE_URL != "unset"  # mandate DBNAME value

# CORS Stuff
origins = [app_settings.FRONTEND_URL]
# print("Configured Origins: {}".format(origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include api item submodules below
app.include_router(root.router, prefix="", tags=["root"])
app.include_router(work_items.router, prefix="/workItems", tags=["workItems"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(converters.router, prefix="/converters", tags=["converters"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(utilities.router, prefix="/utilities", tags=["utilities"])
app.mount("/graph", GraphQLApp(query, on_get=make_graphiql_handler()))
