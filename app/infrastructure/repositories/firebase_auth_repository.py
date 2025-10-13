from domain.entities.user import User
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.errors.auth_errors import *

class FirebaseAuthRepository:
    """
    Repository with db interaction realted with authentication operations
    """

    def __init__(
        self, 
        auth_client: FirebaseAuthClient,
    ):
        self.auth_client = auth_client

    def create(self, user_data: User) -> str:
        try:
            display_name = f"{user_data.name} {user_data.surname}".strip()
            uid = self.auth_client.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=display_name,
            )
            return uid
        except Exception as e:
            handle_firebase_auth_error(e)

    def update(self, uid: str, user_data: dict):
        try:
            user_record = self.auth_client.update_user(uid, email=user_data["email"])
            return user_record
        except Exception as e:
            handle_firebase_auth_error(e)

    def delete(self, uid: str):
        try:
            self.auth_client.delete_user(uid)
        except Exception as e:
            handle_firebase_auth_error(e)

    def delete_all(self):
        try:
            self.auth_client.delete_all_users()
        except Exception as e:
            handle_firebase_auth_error(e)
