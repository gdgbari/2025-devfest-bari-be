import os
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from core.settings import settings
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.user_errors import *


class FirestoreClient:
    """
    Client for interacting with Google Firestore using the firebase_admin SDK.

    This class provides common methods for creating, reading, updating, and deleting documents
    in Firestore collections, as well as user-specific document operations.

    Note: Use as a singleton through FastAPI's dependency injection with lru_cache.

    Usage:
        client = FirestoreClient()
        client.create_doc("collection", "doc_id", {"field": "value"})
    """


    def __init__(self) -> None:
        """
        Initializes the Firestore client and Firebase app if not already initialized.
        
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
        self.db = firestore.client()
        self._initialized: bool = True


    def create_doc(
        self,
        collection_name: str,
        doc_id: Optional[str],
        doc_data: Optional[Dict[str, Any]] = None,
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
        _, doc_ref = self.db.collection(collection_name).add(
            document_data=doc_data,
            document_id=doc_id,
        )
        return doc_ref.id


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
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
        else:
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
