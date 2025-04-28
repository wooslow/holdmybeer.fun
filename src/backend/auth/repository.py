import datetime
import json

from sqlalchemy.future import select

from .shemas import UserRegisterSchema
from .models import UserBaseModel
from .exceptions import UserAlreadyExistsException, UserNotFoundException
from .enums import UserPermissionRole, UserVerificationStatus

from ..database import DatabaseSession, redis


class UserRepository:
    def __init__(self, database: DatabaseSession) -> None:
        self.database: DatabaseSession = database

    @staticmethod
    def _default_serializer(obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    @staticmethod
    def _datetime_decoder(dct):
        for key, value in dct.items():
            if key in ['created_at', 'last_login'] and isinstance(value, str):
                try:
                    dct[key] = datetime.datetime.fromisoformat(value)
                except ValueError:
                    pass
        return dct

    async def get(self, email: str) -> UserBaseModel:
        """ Get user by email """

        user_data = await redis.get(f"user:{email}")

        if user_data:
            user_dict = json.loads(user_data, object_hook=self._datetime_decoder)
            return UserBaseModel(**user_dict)

        query = select(UserBaseModel).where(UserBaseModel.email == email)
        async with self.database as session:
            result = await session.execute(query)
            user = result.scalars().first()

            if user:
                await redis.set(
                    f"user:{email}",
                    json.dumps(user.model_dump(), default=self._default_serializer)
                )

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
        )

        async with self.database as session:
            session.add(db_user)
            await session.commit()

        await redis.set(
            f"user:{db_user.email}",
            json.dumps(
                db_user.model_dump(),
                default=self._default_serializer
            ),
            ex=300
        )

        return db_user

    async def update(self, email: str, update_data: dict) -> UserBaseModel:  # TODO: Transfer to UserService
        """ Update user information """
        async with self.database as session:
            result = await session.execute(
                select(UserBaseModel).where(UserBaseModel.email == email)
            )
            user = result.scalars().first()

            if not user:
                raise UserNotFoundException()
            allowed_fields = {
                'hash_password',
                'is_banned',
                'permissions',
                'verification_status'
            }

            for field, value in update_data.items():
                if field in allowed_fields:
                    setattr(user, field, value)

            user.last_login = datetime.datetime.now(datetime.timezone.utc)

            try:
                await session.commit()
                await session.refresh(user)
            except Exception as e:
                await session.rollback()
                raise

            await redis.set(
                f"user:{user.email}",
                json.dumps(
                    user.model_dump(),
                    default=self._default_serializer
                ),
                ex=300
            )

            return user

    async def set_email_verified(self, email: str) -> UserBaseModel:  # TODO: Transfer to UserService
        """ Set email as verified """
        return await self.update(
            email=email,
            update_data={"verification_status": UserVerificationStatus.CONFIRMED.value}
        )
