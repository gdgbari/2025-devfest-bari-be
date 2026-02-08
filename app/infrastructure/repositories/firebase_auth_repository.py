from typing import Any, Dict

from domain.entities.user import User
from firebase_admin.auth import EmailAlreadyExistsError
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.errors.auth_errors import *


class FirebaseAuthRepository:
    """
    Repository with db interaction realted with authentication operations
    """

    # User field names
    USER_EMAIL: str = "email"

    def __init__(
        self,
        auth_client: FirebaseAuthClient,
    ):
        self.auth_client = auth_client


    def update_user_auth(self, uid: str, user_data: dict):
        """
        Updates authentication information for an existing user in Firebase Authentication.

        This method allows updating the email address associated with a user's Firebase Auth account.
        The method returns the updated user record from Firebase Authentication.

        Raises:
            UpdateUserAuthError: If user authentication update fails. Specific scenarios:
                - HTTP 400: Invalid UID, email format, or other Firebase Auth errors
        """
        try:
            user_record = self.auth_client.update_user(uid, email=user_data[self.USER_EMAIL])
            return user_record
        except Exception as e:
            raise UpdateUserAuthError(message=f"Failed to update user authentication", http_status=400)


    def delete_auth(self, uid: str):
        """
        Deletes a user account from Firebase Authentication.

        This method permanently removes the user's authentication account from Firebase Auth,
        including their email/password credentials and authentication tokens. This operation
        is irreversible. Note that this only deletes the Firebase Auth account and does NOT
        remove the user's profile data from Firestore.

        Raises:
            DeleteUserAuthError: If user authentication deletion fails. Specific scenarios:
                - HTTP 400: Invalid UID, user not found, or other Firebase Auth errors
        """
        try:
            self.auth_client.delete_user(uid)
        except Exception as e:
            raise DeleteUserAuthError(message=f"Failed to delete user", http_status=400)


    def update_custom_claims(self, uid: str, claims: Dict[str, Any]) -> None:
        """"
        Update custom claims for a user
        """
        try:
            self.auth_client.update_custom_claims(uid, claims)
        except Exception as e:
            raise UpdateUserAuthError(message=f"Failed to set custom claims", http_status=400)
