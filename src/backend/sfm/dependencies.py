from sqlmodel import Session
from sfm.database import engine


def get_db():
    with Session(engine) as db:
        yield db