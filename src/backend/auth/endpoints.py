import logging

from fastapi import APIRouter, Response

from .service import AuthService
from .shemas import UserBaseSchema, UserRegisterSchema, UserLoginResponseSchema
from ..database import DatabaseSession

logger = logging.getLogger(__name__)
auth_router = APIRouter(tags=["auth"])


@auth_router.post("/register", response_model=UserBaseSchema)
async def register(user: UserRegisterSchema, database: DatabaseSession):
    auth_service = AuthService(database)
    return await auth_service.register_user(user)


@auth_router.post("/login")
async def login():
    ...


@auth_router.post("/logout")
async def logout():
    ...


@auth_router.get("/me")
async def get_me():
    ...


@auth_router.post("/refresh")
async def refresh():
    ...


@auth_router.get("/reset-password")
async def reset_password():
    ...


@auth_router.post("/reset-password")
async def request_reset_password():
    ...
