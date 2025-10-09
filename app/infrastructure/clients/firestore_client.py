from typing import Any, Dict, List, Optional, Type

import firebase_admin
from firebase_admin import credentials, firestore

from core.settings import settings
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.user_errors import *


class FirestoreClient:
    """
    A singleton client for interacting with Google Firestore using the firebase_admin SDK.

    This class provides common methods for creating, reading, updating, and deleting documents
    in Firestore collections, as well as user-specific document operations.

    Usage:
        client = FirestoreClient()
        client.create_doc("collection", "doc_id", {"field": "value"})
    """

    _instance: Optional["FirestoreClient"] = None

    def __new__(
        cls: Type["FirestoreClient"], *args: Any, **kwargs: Any
    ) -> "FirestoreClient":
        """
        Ensures only one instance of FirestoreClient exists (singleton pattern).
        """
        if cls._instance is None:
            cls._instance = super(FirestoreClient, cls).__new__(cls)
            cls._instance._initialized: bool = False
        return cls._instance

    def __init__(self) -> None:
        """
        Initializes the Firestore client and Firebase app if not already initialized.
        """
        if getattr(self, "_initialized", False):
            return
        if not firebase_admin._apps:
            cred: credentials.Certificate = credentials.Certificate(
                settings.firebase_service_account_path
            )
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self._initialized: bool = True

    #########################################################################################################
    # Common functions                                                                                      #
    #########################################################################################################

    def create_doc(
        self,
        collection_name: str,
        doc_id: Optional[str],
        doc_data: Dict[str, Any],
    ) -> str:
        """
        Creates a document in the specified Firestore collection.

        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (Optional[str]): The document ID. If None, Firestore will auto-generate an ID.
            doc_data (dict): The data to store in the document.

        Returns:
            str: The ID of the created document.
        """
        try:
            _, doc_ref = self.db.collection(collection_name).add(
                document_data=doc_data,
                document_id=doc_id,
            )
            return doc_ref.id
        except Exception:
            raise DocumentNotFoundError()

    def read_doc(self, collection_name: str, doc_id: str) -> Dict[str, Any]:
        """
        Reads a document from a Firestore collection by its ID.

        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The document ID.

        Returns:
            dict: The document data.

        Raises:
            Exception: If the document does not exist.
        """
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_dict: Optional[Dict[str, Any]] = doc.to_dict()
            return doc_dict if doc_dict is not None else {}
        else:
            raise DocumentNotFoundError()

    def read_all_docs(
        self,
        collection_name: str,
        include_id: Optional[bool] = False,
        id_field_name: Optional[str] = "id",
    ) -> List[Dict[str, Any]]:
        """
        Reads all documents from a Firestore collection.

        Args:
            collection_name (str): The name of the Firestore collection.

        Returns:
            list[dict]: List of document data.
        """
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.get()
        if include_id:
            return [{id_field_name: doc.id, **doc.to_dict()} for doc in docs]
        else:
            return [doc.to_dict() for doc in docs]

    def update_doc(
        self,
        collection_name: str,
        doc_id: str,
        doc_data: Dict[str, Any],
    ) -> None:
        """
        Updates an existing document in a Firestore collection.

        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The document ID.
            doc_data (dict): The data to update in the document.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(doc_id)
            doc_ref.update(doc_data)
        except Exception:
            raise DocumentNotFoundError()

    def delete_doc(self, collection_name: str, doc_id: str) -> None:
        """
        Deletes a document from a Firestore collection.

        Args:
            collection_name (str): The name of the Firestore collection.
            doc_id (str): The document ID.
        """
        try:
            doc_ref = self.db.collection(collection_name).document(doc_id)
            doc_ref.delete()
        except Exception:
            raise DocumentNotFoundError()

    def delete_all_docs(self, collection_name: str) -> None:
        """
        Deletes all documents from a Firestore collection.

        Args:
            collection_name (str): The name of the Firestore collection.
        """
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.get()
        for doc in docs:
            doc.reference.delete()

    #########################################################################################################
    # Users related functions                                                                               #
    #########################################################################################################

    def create_user_doc(self, doc_id: str, user_data: Dict[str, Any]) -> None:
        """
        Creates a user document in the 'users' collection.

        Args:
            doc_id (str): The Firebase Auth uid to be used as document ID.
            user_data (dict): The user data to store.
        """
        try:
            self.create_doc("users", doc_id, user_data)
        except Exception:
            raise UserDataAlreadyExistsError()

    def read_user_doc(self, doc_id: str) -> Dict[str, Any]:
        """
        Reads a user document from the 'users' collection by its ID.

        Args:
            doc_id (str): The user document ID.

        Returns:
            dict: The user document data.
        """
        try:
            return self.read_doc("users", doc_id)
        except Exception:
            raise UserDataNotFoundError()

    def read_all_user_docs(self) -> List[Dict[str, Any]]:
        """
        Reads all user documents from the 'users' collection.

        Returns:
            List[dict]: A list of user document data.
        """
        return self.read_all_docs(
            collection_name="users",
            include_id=True,
            id_field_name="uid",
        )

    def update_user_doc(self, doc_id: str, user_data: Dict[str, Any]) -> None:
        """
        Updates a user document in the 'users' collection.

        Args:
            doc_id (str): The user document ID.
            user_data (dict): The user data to update.
        """
        try:
            self.update_doc("users", doc_id, user_data)
        except Exception:
            raise UserDataNotFoundError()

    def delete_user_doc(self, doc_id: str) -> None:
        """
        Deletes a user document from the 'users' collection.

        Args:
            doc_id (str): The user document ID.
        """
        try:
            self.delete_doc("users", doc_id)
        except Exception:
            raise UserDataNotFoundError()

    def delete_all_user_docs(self) -> None:
        """
        Deletes all user documents from the 'users' collection.
        """
        self.delete_all_docs("users")
