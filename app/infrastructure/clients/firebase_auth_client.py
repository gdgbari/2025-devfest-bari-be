import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin.auth import ListUsersPage, UserRecord

from core.settings import settings


class FirebaseAuthClient:
    """
    Client for interacting with Firebase Authentication using the firebase_admin SDK.

    This class provides methods to create, read, update, and delete users in Firebase Authentication.
    It ensures that the Firebase app is initialized before performing any operations.

    Note: Use as a singleton through FastAPI's dependency injection with lru_cache.
    """

    def __init__(self) -> None:
        """
        Initialize the Firebase client and Firebase app if not already initialized.
        
        In local development: uses service account key file if specified and exists.
        On Cloud Run: uses Application Default Credentials (ADC) automatically provided by GCP.
        """
        if not firebase_admin._apps:
            # Check if service account path is provided and file exists (local development)
            if (
                settings.firebase_service_account_path
                and os.path.exists(settings.firebase_service_account_path)
            ):
                cred: credentials.Certificate = credentials.Certificate(
                    settings.firebase_service_account_path
                )
                firebase_admin.initialize_app(cred)
            else:
                # Use Application Default Credentials (Cloud Run or local with gcloud auth)
                firebase_admin.initialize_app()
        self._initialized: bool = True

    def create_user(
        self, email: str, password: str, display_name: Optional[str] = None
    ) -> str:
        """
        Create a new user in Firebase Authentication.

        Args:
            email (str): The user's email address.
            password (str): The user's password.
            display_name (str, optional): The user's display name.

        Returns:
            str: The UID of the created user.
        """
        user_record: UserRecord = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=True
        )
        return user_record.uid

    def read_user(self, uid: str) -> Dict[str, Any]:
        """
        Retrieve a user by their UID.

        Args:
            uid (str): The UID of the user to retrieve.

        Returns:
            dict: The user record data as a dictionary.
        """
        user_record: UserRecord = auth.get_user(uid)
        return user_record._data

    def read_all_users(self) -> List[Dict[str, Any]]:
        """
        Retrieve all users from Firebase Authentication.

        Returns:
            list: A list of dictionaries representing all user records.
        """
        users: List[Dict[str, Any]] = []
        page: Optional[ListUsersPage] = auth.list_users()
        while page:
            for user in page.users:
                users.append(user._data)
            page = page.get_next_page()
        return users

    def update_user(
        self,
        uid: str,
        email: Optional[str] = None,
        password: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update a user's information.

        Args:
            uid (str): The UID of the user to update.
            email (str, optional): The new email address.
            password (str, optional): The new password.
            display_name (str, optional): The new display name.

        Returns:
            dict: The updated user record data as a dictionary.
        """
        params: Dict[str, Any] = {}
        if email is not None:
            params["email"] = email
        if password is not None:
            params["password"] = password
        if display_name is not None:
            params["display_name"] = display_name
        user_record = auth.update_user(uid, **params)
        return user_record._data

    def delete_user(self, uid: str) -> None:
        """
        Delete a user by their UID.

        Args:
            uid (str): The UID of the user to delete.
        """
        auth.delete_user(uid)

    def delete_all_users(self) -> None:
        """
        Delete all users from Firebase Authentication.

        WARNING: This operation is irreversible and will remove all users.
        """
        page: Optional[ListUsersPage] = auth.list_users()
        while page:
            for user in page.users:
                auth.delete_user(user.uid)
            page = page.get_next_page()

    def update_custom_claims(self, uid: str, claims: Dict[str, Any]) -> None:
        """ "
        Update customer claims for a jwt token
        """
        # Retrieve current custom claims
        user_record = auth.get_user(uid)
        existing_claims = user_record.custom_claims or {}
        # Update existing claims with new claims (merge)
        updated_claims = {**existing_claims, **claims}
        auth.set_custom_user_claims(uid=uid, custom_claims=updated_claims)
