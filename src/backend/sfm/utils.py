import config
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

import string
import random

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ADMIN_KEY = config.ADMIN_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_project_auth_token():
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
    for i in range(10):
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
    if attempt == ADMIN_KEY:
        return True
    else:
        return False
