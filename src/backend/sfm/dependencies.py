from sqlmodel import Session
from sfm.database import engine
from sfm.config import get_settings
from sfm.utils import verify_api_auth_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app_settings = get_settings()
security = HTTPBearer()


def get_db():  # pragma: no cover
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def has_access(credentials: HTTPBasicCredentials = Depends(security)):
    token = credentials.credentials
    verified = verify_api_auth_token(token)
    if verified:
        return True
    else:
        raise HTTPException(status_code=403, detail="Incorrect Credentials")
