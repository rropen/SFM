from sqlmodel import Session
from sfm.database import engine


def get_db():  # pragma: no cover
    with Session(engine) as db:
        yield db
