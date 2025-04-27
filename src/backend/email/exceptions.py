class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists in the system."""

    ...


class UserAlreadyPassedChallengeException(Exception):
    """Exception raised when a user has already passed a challenge."""

    ...
