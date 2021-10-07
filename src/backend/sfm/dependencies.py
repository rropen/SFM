from sqlmodel import Session
from sfm.database import engine


def get_db():  # pragma: no cover
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
