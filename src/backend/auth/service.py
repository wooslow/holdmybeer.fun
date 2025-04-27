import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError

from .repository import UserRepository
from .models import UserBaseModel
from .shemas import UserRegisterSchema, UserBaseSchema
from ..database import DatabaseSession

load_dotenv()
security = HTTPBearer(scheme_name="Authorization")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, database: DatabaseSession) -> None:
        self.user_repository = UserRepository(database)

    @staticmethod
    def _password_hasher(password: str) -> str:
        """ Hash a password using bcrypt """
        return pwd_context.hash(password)

    async def register_user(self, user: UserRegisterSchema) -> UserBaseSchema:
        """ Function to register a new user """

        user.password = self._password_hasher(user.password)
        user_orm = await self.user_repository.create(user)

        return UserBaseSchema.from_orm(user_orm)
