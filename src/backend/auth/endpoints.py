import logging

from fastapi import APIRouter, Response, Request, HTTPException, status

from .service import AuthService
from .shemas import UserBaseSchema, UserRegisterSchema, UserLoginSchema, UserTokensSchema
from ..database import DatabaseSession

logger = logging.getLogger(__name__)
auth_router = APIRouter(tags=["auth"])


@auth_router.post("/register", response_model=UserBaseSchema)
async def register(user: UserRegisterSchema, database: DatabaseSession):
    auth_service = AuthService(database)
    return await auth_service.register(user)


@auth_router.post("/login", response_model=UserTokensSchema)
async def login(
    response: Response,
    credentials: UserLoginSchema,
    database: DatabaseSession
):
    auth_service = AuthService(database)
    result = await auth_service.login(credentials)
    response.set_cookie(
        key="Authorization",
        value=result.access_token,
        httponly=True,
        max_age=40 * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60
    )

    return result


@auth_router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Logout user by removing the Authorization cookie"""
    response.delete_cookie(key="Authorization")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@auth_router.post("/refresh", response_model=UserTokensSchema)
async def refresh(request: Request, response: Response, database: DatabaseSession):
    """Refresh access and refresh tokens"""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token"
        )

    auth_service = AuthService(database)
    tokens = await auth_service.refresh_access_token(refresh_token)

    response.set_cookie(
        key="Authorization",
        value=tokens.access_token,
        httponly=True,
        max_age=40 * 60
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=7 * 24 * 60 * 60
    )

    return tokens


@auth_router.get("/reset-password")
async def reset_password():
    ...


@auth_router.post("/reset-password")
async def request_reset_password():
    ...
