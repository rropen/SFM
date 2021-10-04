# CD to backend > source env/Scripts/activate > pip install -r requirements.txt  > uvicron main:app --reload
# UI http://127.0.0.1:8000/docs http://127.0.0.1:8000/openapi.json
from fastapi import FastAPI, Depends
from sqlmodel import Session
from starlette.middleware.cors import CORSMiddleware
from sfm.database import create_db_and_tables, engine
import os
from sfm.routes.work_items import routes as work_items
from sfm.routes.projects import routes as projects
from sfm.routes.converters import routes as converters
from sfm.routes.metrics import routes as metrics
from sfm.routes.utilities import routes as utilities
from sfm.routes import root
from .config import get_settings


# This is how you can get access to environment configuration values throughout the application
# Then app_settings.ENV or app_settings.CONN_STR.  See config.py for possible values.
app_settings = get_settings()

# this file will always be called with __name__ == "sfm.main" (even in docker container)
create_db_and_tables()

description = "<h2>Software Factory Metrics</h2><br><blockquote>A custom app built by the Software Factory to generate DORA metrics which are a key concept in the move towards DevSecOps.</blockquote>"
app = FastAPI(
    debug=app_settings.DEBUG, title="SFM API", description=description, version="0.0.1"
)

assert app_settings.ENV != "unset"  # mandate ENV value
assert app_settings.ENV in ("test", "local", "development", "production")
assert app_settings.DEBUG != "unset"  # mandate DEBUG value
assert app_settings.SECRET_KEY != "unset"  # mandate SECRET_KEY value
assert app_settings.ADMIN_KEY != "unset"  # mandate SECRET_KEY value
assert app_settings.FRONTEND_URL != "unset"  # mandate FRONTEND_URL value
if app_settings.ENV in ["development", "production"]:
    assert app_settings.DBHOST != "unset"  # mandate DBHOST value
    assert app_settings.DBNAME != "unset"  # mandate DBNAME value
    assert app_settings.DBUSER != "unset"  # mandate DBUSER value
    assert app_settings.DBPASS != "unset"  # mandate DBPASS value

# CORS Stuff
origins = [app_settings.FRONTEND_URL]
print("Configured Origins: {}".format(origins))

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
