from enum import Enum


class UserPermissionRole(Enum):
    """User permission roles for the application."""

    USER = 0
    ADMIN = 1


class UserVerificationStatus(Enum):
    """User verification status."""

    NOT_CONFIRMED = 0
    CONFIRMED = 1
