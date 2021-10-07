from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import string
import random
import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler
from sfm.config import get_settings

app_settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    format="%(asctime)s %(pathname)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)
logger.addHandler(
    AzureLogHandler(connection_string=app_settings.AZURE_LOGGING_CONN_STR)
)


def create_project_auth_token():
    # creates 20 character string of random letters, numbers, symbols.
    logger.info("Created new project auth token")
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


def hash_project_auth_token(token: str, expires_delta: Optional[timedelta] = None):
    return pwd_context.hash(token)


def verify_project_auth_token(attempt: str, target: str):
    return pwd_context.verify(attempt, target)


def verify_admin_key(attempt):
    return attempt == app_settings.ADMIN_KEY


epoch = datetime.utcfromtimestamp(0)


def unix_time_seconds(date):
    dt = datetime.combine(date, datetime.min.time())
    return (dt - epoch).total_seconds()
