# CD to backend > source env/Scripts/activate > pip install -r requirements.txt  > uvicron main:app --reload
# UI http://127.0.0.1:8000/docs http://127.0.0.1:8000/openapi.json
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sfm.database import create_db_and_tables, engine
import os
from sfm.routes.work_items import routes as work_items
from sfm.routes.projects import routes as projects
from sfm.routes.converters import routes as converters
from sfm.routes.metrics import routes as metrics
from sfm.routes.utilities import routes as utilities
from sfm.routes import root

# this file will always be called with __name__ == "sfm.main" (even in docker container)
create_db_and_tables()

description = "<h2>Software Factory Metrics</h2><br><blockquote>A custom app built by the Software Factory to generate DORA metrics which are a key concept in the move towards DevSecOps.</blockquote>"
app = FastAPI(title="SFM API", description=description, version="0.0.1")

# CORS Stuff
if os.environ.get("ENV") == "Local":
    ui_url = "http://localhost:3000"

# allow override
if os.environ.get("UI_URL", "http://localhost:3000"):
    ui_url = os.environ.get("UI_URL", "http://localhost:3000")

# throw an error if URL is unset.
assert ui_url != ""
origins = [ui_url]
print("origins: {}".format(origins))
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
