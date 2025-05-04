import datetime
import json
import logging
from typing import Optional, Any

from sqlalchemy.future import select

from .schemas import UserRegisterSchema
from .models import UserBaseModel
from .exceptions import UserAlreadyExistsException, UserNotFoundException
from .enums import UserPermissionRole, UserVerificationStatus
from ..database import DatabaseSession, redis
from ..exceptions import ServerErrorException

logger = logging.getLogger(__name__)


class AuthRepository:
    def __init__(self, database: DatabaseSession) -> None:
        self.database = database

    @staticmethod
    def _default_serializer(obj):
        """Serialize datetime objects to ISO format"""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    @staticmethod
    def _datetime_decoder(dct: dict) -> dict:
        """Deserialize ISO format datetime strings to datetime objects"""
        for key in ['created_at', 'last_login']:
            if key in dct and isinstance(dct[key], str):
                try:
                    dct[key] = datetime.datetime.fromisoformat(dct[key])
                except ValueError:
                    pass
        return dct

    async def get(self, email: str) -> Optional[UserBaseModel]:
        """Retrieve a user by email with Redis caching"""
        logger.info(f"Fetching user by email: {email}")

        try:
            cached_data = await redis.get(f"user:{email}")
            if cached_data:
                logger.debug(f"User found in cache: {email}")
                data = json.loads(cached_data, object_hook=self._datetime_decoder)
                return UserBaseModel(**data)

            async with self.database as session:
                stmt = select(UserBaseModel).where(UserBaseModel.email == email)
                result = await session.execute(stmt)
                user = result.scalars().first()

                if user:
                    await redis.set(
                        f"user:{email}",
                        json.dumps(user.model_dump(), default=self._default_serializer),
                        ex=300
                    )
                    logger.debug(f"User loaded from DB and cached: {email}")

                return user

        except Exception as exc:
            logger.exception(f"Failed to retrieve user {email}: {exc}")
            raise ServerErrorException()

    async def create(self, user_data: UserRegisterSchema) -> UserBaseModel:
        """Create a new user"""
        logger.info(f"Creating user: {user_data.email}")

        if await self.get(user_data.email):
            logger.warning(f"User already exists: {user_data.email}")
            raise UserAlreadyExistsException(f"User with email {user_data.email} already exists")

        user = UserBaseModel(
            email=user_data.email,
            hash_password=user_data.password,
            is_banned=False,
            permissions=UserPermissionRole.USER.value,
            verification_status=UserVerificationStatus.NOT_CONFIRMED.value,
            last_login=datetime.datetime.now(datetime.timezone.utc),
        )

        try:
            async with self.database as session:
                session.add(user)
                await session.commit()
        except Exception as exc:
            logger.exception(f"Failed to create user {user_data.email}: {exc}")
            raise ServerErrorException()

        await redis.set(
            f"user:{user.email}",
            json.dumps(user.model_dump(), default=self._default_serializer),
            ex=300
        )

        logger.debug(f"User created and cached: {user.email}")
        return user

    async def update(self, email: str, update_data: dict[str, Any]) -> UserBaseModel:
        """Update user fields and refresh cache"""
        logger.info(f"Updating user: {email}")

        user = await self.get(email)
        if not user:
            logger.warning(f"User not found: {email}")
            raise UserNotFoundException()

        try:
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            user.last_login = datetime.datetime.now(datetime.timezone.utc)

            async with self.database as session:
                session.add(user)
                await session.commit()
                await session.refresh(user)

            await redis.set(
                f"user:{user.email}",
                json.dumps(user.model_dump(), default=self._default_serializer),
                ex=300
            )

            logger.debug(f"User updated and cache refreshed: {user.email}")
            return user

        except Exception as exc:
            logger.exception(f"Failed to update user {email}: {exc}")
            raise ServerErrorException()

    async def delete(self, email: str) -> None:
        """Delete a user by email"""
        logger.info(f"Deleting user: {email}")

        user = await self.get(email)
        if not user:
            logger.warning(f"User not found for deletion: {email}")
            raise UserNotFoundException()

        try:
            async with self.database as session:
                await session.delete(user)
                await session.commit()

            await redis.delete(f"user:{email}")
            logger.debug(f"User deleted and removed from cache: {email}")

        except Exception as exc:
            logger.exception(f"Failed to delete user {email}: {exc}")
            raise ServerErrorException()
