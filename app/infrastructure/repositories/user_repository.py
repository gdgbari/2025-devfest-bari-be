from domain.entities.user import User
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.user_errors import *


class UserRepository:
    __firestore_client: FirestoreClient = FirestoreClient()

    @classmethod
    def create_user(cls, user_data: User) -> None:
        try:
            if not user_data.uid:
                raise UserIdNotSpecifiedError()

            cls.__firestore_client.create_user_doc(
                doc_id=user_data.uid, user_data=user_data.to_firestore_data()
            )
        except Exception as e:
            handle_firestore_user_error(e)

    @classmethod
    def read_user(cls, uid: str) -> dict:
        try:
            user_data_dict = cls.__firestore_client.read_user_doc(uid)
            return {"uid": uid, **user_data_dict}
        except Exception as e:
            handle_firestore_user_error(e)

    @classmethod
    def read_all_users(cls) -> list[dict]:
        try:
            return cls.__firestore_client.read_all_user_docs()
        except Exception as e:
            handle_firestore_user_error(e)

    @classmethod
    def update_user(cls, uid: str, user_data: dict) -> None:
        try:
            update_params = {}
            if user_data["name"]:
                update_params["name"] = user_data["name"]
            if user_data["surname"]:
                update_params["surname"] = user_data["surname"]

            cls.__firestore_client.update_user_doc(
                doc_id=uid, user_data=update_params
            )
        except Exception as e:
            handle_firestore_user_error(e)

    @classmethod
    def delete_user(cls, uid: str) -> None:
        try:
            cls.__firestore_client.delete_user_doc(doc_id=uid)
        except Exception as e:
            handle_firestore_user_error(e)

    @classmethod
    def delete_all_users(cls) -> None:
        try:
            cls.__firestore_client.delete_all_user_docs()
        except Exception as e:
            handle_firestore_user_error(e)
