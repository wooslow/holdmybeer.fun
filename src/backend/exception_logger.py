from fastapi.responses import JSONResponse
from fastapi.requests import Request

from .auth import UserAlreadyExistsException, UserNotFoundException


async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, UserAlreadyExistsException):
        return JSONResponse(
            status_code=401,
            content={"message": "User already exists"},
        )
    elif isinstance(exc, UserNotFoundException):
        return JSONResponse(
            status_code=401,
            content={"message": "Incorrect email or password"},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )
