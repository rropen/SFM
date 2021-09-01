from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """
    ## Route Notes

    Only a helpful note to move to the docs page.
    """
    return {"Message": "Try /docs or /redoc"}


@router.get("/ping")
async def pong():
    """
    ## Route Notes

    Nothing really to say here...
    """
    return {"ping": "pong!"}
