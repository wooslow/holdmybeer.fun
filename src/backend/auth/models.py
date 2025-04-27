from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped

from ..database import CustomBase
from .enums import UserPermissionRole, UserVerificationStatus


class UserBaseModel(CustomBase):
    __tablename__ = "users_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String)
    is_banned: Mapped[bool] = mapped_column(default=False)
    permissions: Mapped[UserPermissionRole] = mapped_column(
        Integer,
        default=UserPermissionRole.USER
    )
    verification_status: Mapped[UserVerificationStatus] = mapped_column(
        Integer,
        default=UserVerificationStatus.NOT_CONFIRMED
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
