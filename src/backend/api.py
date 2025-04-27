import logging

from fastapi import APIRouter

from .auth import auth_router
from .email import email_router

logger = logging.getLogger(__name__)

api_router = APIRouter(tags=["api"])
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(email_router, prefix="/email")