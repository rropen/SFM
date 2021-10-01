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
from functools import lru_cache
from .config import Settings


# this file will always be called with __name__ == "sfm.main" (even in docker container)
create_db_and_tables()

description = "<h2>Software Factory Metrics</h2><br><blockquote>A custom app built by the Software Factory to generate DORA metrics which are a key concept in the move towards DevSecOps.</blockquote>"
app = FastAPI(title="SFM API", description=description, version="0.0.1")

# Environment Config Settings
@lru_cache()
def get_settings():
    return Settings()


assert get_settings().ENV != "unset"  # mandate ENV value
assert get_settings().DEBUG != "unset"  # mandate DEBUG value
assert get_settings().SECRET_KEY != "unset"  # mandate SECRET_KEY value
assert get_settings().FRONTEND_URL != "unset"  # mandate FRONTEND_URL value
assert get_settings().DBHOST != "unset"  # mandate DBHOST value
assert get_settings().DBNAME != "unset"  # mandate DBNAME value
assert get_settings().DBUSER != "unset"  # mandate DBUSER value
assert get_settings().DBPASS != "unset"  # mandate DBPASS value

# CORS Stuff

# if os.environ.get("ENV") == "Local":
#     ui_url = "http://localhost:3000"

# allow override
# if os.environ.get("UI_URL", "http://localhost:3000"):
#     ui_url = os.environ.get("UI_URL", "http://localhost:3000")


# throw an error if URL is unset.
# assert ui_url != ""
origins = [get_settings().FRONTEND_URL]
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
