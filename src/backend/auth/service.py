import bcrypt
from passlib.context import CryptContext

from dotenv import load_dotenv
from fastapi.security import HTTPBearer

from .repository import UserRepository
from .shemas import UserRegisterSchema, UserBaseSchema

from ..database import DatabaseSession
from ..email import EmailService

load_dotenv()
security = HTTPBearer(scheme_name="Authorization")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bcrypt.__about__ = bcrypt


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

        await EmailService().send_challenge(user.email, "register")

        return UserBaseSchema.from_orm(user_orm)

    async def after_email_verification(self, email: str) -> UserBaseSchema:
        """ Set email as verified """

        user = await self.user_repository.set_email_verified(email)

        return UserBaseSchema.from_orm(user)

