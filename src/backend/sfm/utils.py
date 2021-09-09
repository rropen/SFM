import config
from datetime import datetime, timedelta
from typing import Optional

import jwt
import string
import random

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.ALGORITHM
ADMIN_KEY = config.ADMIN_KEY


def create_project_auth_token(expires_delta: Optional[timedelta] = None):
    letters = string.ascii_uppercase
    randString = "".join(random.choice(letters) for i in range(10))
    to_encode = {"string": randString}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=365)  # By default, expire in a year
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_project_auth_token(attempt: str, target: str):
    if attempt == target:
        return True
    else:
        return False


def verify_admin_key(attempt):
    if attempt == ADMIN_KEY:
        return True
    else:
        return False
