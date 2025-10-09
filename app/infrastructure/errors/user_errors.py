import logging

from fastapi import HTTPException


class UserDataNotFoundError(Exception):
    """Exception raised when user data is not found in Firestore."""

    pass


class UserDataAlreadyExistsError(Exception):
    """Exception raised when user data already exists in Firestore."""

    pass

class UserIdNotSpecifiedError(Exception):
    """Exception raised when a user ID is not specified."""

    pass


firestore_user_errors = {
    UserDataNotFoundError: (404, "User data not found"),
    UserDataAlreadyExistsError: (404, "User data already exists"),
    UserIdNotSpecifiedError: (400, "User id not specified"),
}


def handle_firestore_user_error(e: Exception):
    """
    Handles all Firestore exceptions related to users and converts them into HTTPException.
    """
    if type(e) in firestore_user_errors:
        status_code, detail = firestore_user_errors[type(e)]
        raise HTTPException(status_code=status_code, detail=detail)

    logging.error(f"User error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
