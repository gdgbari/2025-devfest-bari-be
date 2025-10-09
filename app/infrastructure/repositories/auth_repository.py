from firebase_admin import auth

from domain.entities.user import User
from infrastructure.clients.firebase_auth_client import FirebaseAuthClient
from infrastructure.errors.auth_errors import *


class AuthRepository:
    __auth_client = FirebaseAuthClient()

    @classmethod
    def create_user(cls, user_data: User) -> str:
        try:
            display_name = f"{user_data.name} {user_data.surname}".strip()
            uid = cls.__auth_client.create_user(
                email=user_data.email,
                password=user_data.password,
                display_name=display_name,
            )
            return uid
        except Exception as e:
            handle_firebase_auth_error(e)

    @classmethod
    def read_user(cls, uid: str):
        try:
            user_record = cls.__auth_client.read_user(uid)
            return user_record
        except Exception as e:
            handle_firebase_auth_error(e)

    @classmethod
    def read_all_users(cls):
        try:
            users = cls.__auth_client.read_all_users()
            return users
        except Exception as e:
            handle_firebase_auth_error(e)

    @classmethod
    def update_user(cls, uid: str, user_data: dict):
        try:
            user_record = cls.__auth_client.update_user(uid, email=user_data["email"])
            return user_record
        except Exception as e:
            handle_firebase_auth_error(e)

    @classmethod
    def delete_user(cls, uid: str):
        try:
            cls.__auth_client.delete_user(uid)
        except Exception as e:
            handle_firebase_auth_error(e)

    @classmethod
    def delete_all_users(cls):
        try:
            cls.__auth_client.delete_all_users()
        except Exception as e:
            handle_firebase_auth_error(e)
