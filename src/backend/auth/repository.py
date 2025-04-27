"""

Repository for user

All methods that interact with the database should be here
Only database models or nothing should be returned from this class

"""
import datetime
import json

from sqlalchemy.future import select

from .shemas import UserBaseSchema, UserRegisterSchema
from .models import UserBaseModel
from .exceptions import UserAlreadyExistsException
from .enums import UserPermissionRole, UserVerificationStatus

from ..database import DatabaseSession, redis


class UserRepository:
    def __init__(self, database: DatabaseSession) -> None:
        self.database: DatabaseSession = database

    def default_serializer(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        raise TypeError(f"Type {type(obj)} not serializable")

    async def get(self, email: str) -> UserBaseModel:
        """ Get user by email """

        user_data = await redis.get(f"user:{email}")

        if user_data:
            user_dict = json.loads(user_data)
            return UserBaseModel(**user_dict)

        query = select(UserBaseModel).where(UserBaseModel.email == email)
        async with self.database as session:  # Use self.database directly, no parentheses
            result = await session.execute(query)
            user = result.scalars().first()

            if user:
                await redis.set(f"user:{email}", json.dumps(user.model_dump(), default=self.default_serializer))

            return user

    async def create(self, user: UserRegisterSchema) -> UserBaseModel:
        """ Create user """

        existing_user = await self.get(user.email)

        if existing_user:
            raise UserAlreadyExistsException(f"User with email {user.email} already exists")

        db_user = UserBaseModel(
            email=user.email,
            hash_password=user.password,
            is_banned=False,
            permissions=UserPermissionRole.USER.value,
            verification_status=UserVerificationStatus.NOT_CONFIRMED.value,
            last_login=datetime.datetime.now(),
            created_at=datetime.datetime.now(),
        )

        async with self.database as session:
            session.add(db_user)
            await session.commit()

        await redis.set(f"user:{db_user.email}", json.dumps(db_user.model_dump(), default=self.default_serializer))

        return db_user
