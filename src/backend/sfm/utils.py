from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import string
import random
import logging
import hmac
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sqlalchemy.sql.operators import is_not_distinct_from
from sfm.config import get_settings
from fastapi import HTTPException, Depends
from sqlmodel import Session, select, and_
from sfm.models import Project
from sfm.logger import create_logger

logger = create_logger(__name__)

app_settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_project_auth_token():
    # creates 20 character string of random letters, numbers, symbols.
    logger.debug("A new project auth token has been created")
    low_letters = string.ascii_lowercase
    up_letters = string.ascii_uppercase
    digits = string.digits
    symbols = [
        "!",
        "#",
        "$",
        "%",
        "&",
        "*",
        "+",
        ":",
        ";",
        "?",
        "<",
        ">",
        "=",
        "_",
        "~",
    ]

    rand_arr = []
    for i in range(20):
        choice = random.randrange(4)
        if choice == 0:
            rand_char = random.choice(low_letters)
        elif choice == 1:
            rand_char = random.choice(up_letters)
        elif choice == 2:
            rand_char = random.choice(digits)
        elif choice == 3:
            rand_char = random.choice(symbols)

        rand_arr.append(rand_char)

    return "".join(rand_arr)


def hash_project_auth_token(token: str):
    return pwd_context.hash(token)


def calc_signature(payload):
    digest = hmac.new(
        key=app_settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload,
        digestmod="sha256",
    ).hexdigest()
    return f"sha256={digest}"


def validate_signature(signature, raw):
    if signature != calc_signature(raw):
        logger.warning(
            "Incorrect GitHub credentials included with incoming payload, access was denied"
        )
        raise HTTPException(status_code=401, detail="Github Credentials Incorrect")
    project_auth_token = app_settings.GITHUB_WEBHOOK_SECRET
    return project_auth_token


def verify_project_auth_token(attempt: str, target: str):
    if pwd_context.verify(attempt, target):
        return True
    elif pwd_context.verify(
        attempt, hash_project_auth_token(app_settings.GITHUB_WEBHOOK_SECRET)
    ):
        return True
    else:
        return False


def verify_admin_key(attempt):
    return attempt == app_settings.ADMIN_KEY


def verify_api_auth_token(attempt):
    return pwd_context.verify(attempt, pwd_context.hash(app_settings.API_AUTH_TOKEN))


epoch = datetime.utcfromtimestamp(0)


def unix_time_seconds(date):
    dt = datetime.combine(date, datetime.min.time())
    return (dt - epoch).total_seconds()


def project_selector(db, project_name=None, project_id=None):
    if project_name and not project_id:
        project = db.exec(select(Project).where(Project.name == project_name)).first()
        if not project:
            logger.debug("No Project found with the specified name")
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified name: {project_name}",
            )
    elif project_id and not project_name:
        project = db.get(Project, project_id)
        if not project:
            logger.debug("No project with the specified id")
            raise HTTPException(
                status_code=404,
                detail=f"No project found with the specified id: {project_id}",
            )
    elif project_id and project_name:
        project = db.exec(
            select(Project).where(
                and_(Project.id == project_id, Project.name == project_name)
            )
        ).first()
        if not project:
            logger.debug(
                "Either project_id and project_name do not match or no matching project"
            )
            raise HTTPException(
                status_code=404,
                detail="Either the project_name and project_id do not match, or there is not a project with the specified details. Try passing just one of the parameters instead of both.",
            )
    else:
        project = None

    return project
