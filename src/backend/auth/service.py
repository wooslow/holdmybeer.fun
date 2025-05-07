import os
import bcrypt
from passlib.context import CryptContext
from datetime import timedelta, datetime

from dotenv import load_dotenv
from fastapi.security import HTTPBearer
from jose import jwt

from .repository import AuthRepository
from .schemas import UserRegisterSchema, UserBaseSchema, UserLoginSchema, UserTokensSchema
from .exceptions import UserNotFoundException, EmailNotValidException

from ..database import DatabaseSession
from ..email import EmailService

load_dotenv()

security = HTTPBearer(scheme_name="Authorization")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bcrypt.__about__ = bcrypt  # Fix a AttributeError in passlib type: ignore


class AuthService:
    def __init__(self, database: DatabaseSession) -> None:
        self.auth_repository = AuthRepository(database)

    @staticmethod
    def _password_generator() -> str:
        """ Generate a random password """
        return bcrypt.gensalt().decode('utf-8')

    @staticmethod
    def _password_hasher(password: str) -> str:
        """ Hash a password using bcrypt """
        return pwd_context.hash(password)

    @staticmethod
    def _password_checker(plain_password: str, hashed_password: str) -> bool:
        """ Check a password against its hash """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def __encode_token(data: dict, expires_delta: timedelta) -> str:
        """ Encode a JWT token with an expiration time """
        payload = data.copy()
        payload.update({"exp": datetime.now() + expires_delta})

        return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")

    @staticmethod
    def _email_validator(email: str) -> bool:
        """ Validate email format """
        return isinstance(email, str) and "@" in email and "." in email

    @staticmethod
    def _create_tokens(data: dict) -> UserTokensSchema:
        """Generate access and refresh tokens"""
        access_token = AuthService.__encode_token(data, timedelta(minutes=40))
        refresh_token = AuthService.__encode_token(data, timedelta(days=7))

        return UserTokensSchema(access_token=access_token, refresh_token=refresh_token)

    async def register(self, user: UserRegisterSchema) -> UserBaseSchema:
        """ Function to register a new user """
        if not self._email_validator(user.email):
            raise EmailNotValidException()

        user.password = self._password_hasher(user.password)
        user_orm = await self.auth_repository.create(user)

        await EmailService().send_challenge(user.email, "register")

        return UserBaseSchema.from_orm(user_orm)

    async def after_email_verification(self, email: str) -> UserBaseSchema:
        """ Set email as verified """

        user = await self.auth_repository.set_email_verified(email)

        return UserBaseSchema.from_orm(user)

    async def update_last_login(self, email: str) -> None:
        """ Update the last login time for the user """
        await self.auth_repository.update_last_login(email)

    async def login(self, credentials: UserLoginSchema) -> UserTokensSchema:
        """ Authenticate user and return JWT tokens """
        if not self._email_validator(credentials.email):
            raise EmailNotValidException()

        found_user = await self.auth_repository.get(email=credentials.email)

        if not found_user or not self._password_checker(credentials.password, found_user.hash_password):
            raise UserNotFoundException()

        await self.update_last_login(found_user.email)

        tokens = self._create_tokens({"email": found_user.email})

        return tokens

    async def refresh_access_token(self, refresh_token: str) -> UserTokensSchema:
        """ Refresh access token using a refresh token """

        try:
            payload = jwt.decode(refresh_token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            email: str = payload.get("email")

            if email is None:
                raise UserNotFoundException()
        except jwt.JWTError:
            raise UserNotFoundException()

        tokens = self._create_tokens({"email": email})

        return tokens

    async def reset_password(self, email: str) -> None:
        """ Reset user password """
        if not self._email_validator(email):
            raise EmailNotValidException()

        found_user = await self.auth_repository.get(email=email)

        if not found_user:
            raise UserNotFoundException("If the email exists, a reset password link will be sent to it. Please check your inbox.")

        await EmailService().send_challenge(email, "reset_password")

    async def after_password_reset(self, email: str) -> None:
        """ Set password as reset """

        new_password = self._password_hasher(self._password_generator())

        await self.auth_repository.update(email, {"hash_password": new_password})
        await EmailService().send_mail(email, "new_password", new_password)
