from fastapi.responses import JSONResponse
from fastapi.requests import Request


from .auth import UserAlreadyExistsException


async def custom_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, UserAlreadyExistsException):
        return JSONResponse(
            status_code=409,
            content={"message": str(exc)},
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"},
        )
