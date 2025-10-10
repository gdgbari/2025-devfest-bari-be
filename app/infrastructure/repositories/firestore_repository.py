from domain.entities.user import User
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.user_errors import *


class FirestoreRepository:
    """
    Repository with db interaction related to user data operations in Firestore
    """

    def __init__(
        self,
        firestore_client: FirestoreClient,
    ):
        self.firestore_client = firestore_client

    def create(self, user_data: User) -> None:
        try:
            if not user_data.uid:
                raise UserIdNotSpecifiedError()

            self.firestore_client.create_user_doc(
                doc_id=user_data.uid, user_data=user_data.to_firestore_data()
            )
        except Exception as e:
            handle_firestore_user_error(e)

    def read(self, uid: str) -> dict:
        try:
            user_data_dict = self.firestore_client.read_user_doc(uid)
            return {"uid": uid, **user_data_dict}
        except Exception as e:
            handle_firestore_user_error(e)

    def read_all(self) -> list[dict]:
        try:
            return self.firestore_client.read_all_user_docs()
        except Exception as e:
            handle_firestore_user_error(e)

    def update(self, uid: str, user_data: dict) -> None:
        try:
            update_params = {}
            if user_data["name"]:
                update_params["name"] = user_data["name"]
            if user_data["surname"]:
                update_params["surname"] = user_data["surname"]

            self.firestore_client.update_user_doc(
                doc_id=uid, user_data=update_params
            )
        except Exception as e:
            handle_firestore_user_error(e)

    def delete(self, uid: str) -> None:
        try:
            self.firestore_client.delete_user_doc(doc_id=uid)
        except Exception as e:
            handle_firestore_user_error(e)

    def delete_all(self) -> None:
        try:
            self.firestore_client.delete_all_user_docs()
        except Exception as e:
            handle_firestore_user_error(e)
