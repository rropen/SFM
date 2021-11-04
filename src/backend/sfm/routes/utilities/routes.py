from sfm.database import create_db_and_tables
from sfm.routes.utilities import crud as utility_crud
from sfm.dependencies import get_db
from sqlmodel import SQLModel
from fastapi import APIRouter, Depends
from sfm.database import engine
from sfm.config import get_settings
from opencensus.ext.azure.log_exporter import AzureLogHandler
import string
import random

import logging

app_settings = get_settings()

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(
        connection_string="InstrumentationKey=" + app_settings.AZURE_LOGGING_CONN_STR
    )
)


def random_sha(seed):  # pragma: no cover
    N = 20
    random.seed(a=seed)
    res = "".join(random.choices(string.ascii_uppercase + string.digits, k=N))
    return res


router = APIRouter()


@router.post("/populate_mock_data")  # pragma: no cover
def populate(db=Depends(get_db)):
    utility_crud.populate_db(db)


@router.delete("/clear_local_db")  # pragma: no cover
def clear(db=Depends(get_db)):
    utility_crud.clear_db(db)
