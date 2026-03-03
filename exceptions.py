class UserExistsException(Exception):
    """Exception raised when trying to create a user that already exists."""
    pass

class UserDoesntExistException(Exception):
    """Exception raised when trying to retrieve a user that does not exist."""
    pass