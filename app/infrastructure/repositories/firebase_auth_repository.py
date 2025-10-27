from firebase_admin.auth import EmailAlreadyExistsError

from domain.entities.user import User
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


    def create_user_authentication(self, user_data: User) -> str:
        """
        Creates a new user in Firebase Authentication.

        This method creates a user account in Firebase Auth with email/password authentication.
        The display name is automatically generated from the user's name and surname.

        Raises:
            AuthenticateUserError: If user creation fails. Specific scenarios:
                - HTTP 409: Email already exists in Firebase Auth
                - HTTP 400: Invalid user data or other Firebase Auth errors
        """
        try:
            display_name = f"{user_data.name} {user_data.surname}".strip()
            uid = self.auth_client.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=display_name,
            )
            return uid
        except EmailAlreadyExistsError:
            raise AuthenticateUserError(message=f"Failed to authenticate the user: email already exsiting {str(user_data.email)}", http_status=409)
        except Exception as exception:
            raise AuthenticateUserError(message=f"Failed to authenticate the user with uid {str(user_data.uid)}: {str(exception)}", http_status=400)


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
            raise UpdateUserAuthError(message=f"Failed to update user authentication {str(uid)}: {str(e)}", http_status=400)


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
            raise DeleteUserAuthError(message=f"Failed to delete user {str(uid)} in firebase auth: {str(e)}", http_status=400)


    def delete_all(self):
        """
        Deletes all user accounts from Firebase Authentication.

        This method performs a batch deletion of all user authentication accounts from Firebase Auth.
        WARNING: This is a destructive operation that cannot be undone. All user credentials, tokens,
        and authentication records will be permanently removed. This should only be used for testing,
        data cleanup, or administrative purposes. This does NOT remove user profile data from Firestore.

        Raises:
            DeleteUserAuthError: If batch deletion fails. Specific scenarios:
                - HTTP 400: Firebase Auth operation errors or permission issues
        """
        try:
            self.auth_client.delete_all_users()
        except Exception as e:
            raise DeleteUserAuthError(message=f"Failed to delete all users in firebase auth: {str(e)}", http_status=400)
