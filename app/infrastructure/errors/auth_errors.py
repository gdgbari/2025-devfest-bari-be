import logging

from fastapi import HTTPException
from firebase_admin import auth


class NoDataToUpdateError(Exception):
    """Exception raised when no data is provided for update in Auth operations."""
    pass


firebase_auth_errors: dict = {
    auth.EmailAlreadyExistsError: (409, "Email already exists"),
    auth.EmailNotFoundError: (404, "Email not found"),
    auth.UserNotFoundError: (404, "User not found"),
    NoDataToUpdateError: (400, "No data to update"),
}


def handle_firebase_auth_error(e: Exception):
    """
    Handles all Firebase Auth exceptions and converts them into HTTPException.
    """
    if type(e) in firebase_auth_errors:
        status_code, detail = firebase_auth_errors[type(e)]
        raise HTTPException(status_code=status_code, detail=detail)

    logging.error(f"Firebase Auth error: {str(e)}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
