class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists in the system."""

    ...


class UserNotFoundException(Exception):
    """Exception raised when a user is not found in the system."""

    ...
