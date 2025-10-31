from domain.entities.user import User
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import *
from infrastructure.errors.user_errors import *


class FirestoreRepository:
    """
    Repository with db interaction related to user data operations in Firestore
    """

    # Collection names
    USERS_COLLECTION: str = "users"
    NICKNAMES_COLLECTION: str = "nicknames"
    GROUP_COLLECTION: str = "groups"

    # User field names
    USER_ID: str = "uid"
    USER_EMAIL: str = "email"
    USER_NAME: str = "name"
    USER_SURNAME: str = "surname"
    USER_NICKNAME: str = "nickname"
    USER_GROUP: str = "group"

    def __init__(
        self,
        firestore_client: FirestoreClient
    ):
        self.firestore_client = firestore_client


    def create_user(self, user_data: User) -> None:
        """
        Creates a new user document in the Firestore 'users' collection.

        This method stores user profile data (email, name, surname, nickname) in Firestore
        using the Firebase Auth UID as the document ID. This should be called AFTER the user
        has been created in Firebase Auth and has a valid UID assigned.

        Raises:
            CreateUserError: If user document creation fails. Specific scenarios:
                - HTTP 409: A user document with this UID already exists in Firestore
                - HTTP 400: Invalid user data or other Firestore operation errors
        """
        try:
            self.firestore_client.create_doc(
                collection_name=self.USERS_COLLECTION, doc_id=user_data.uid, doc_data=user_data.to_firestore_data()
            )
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateUserError(message=f"User already existing", http_status=409)
            raise CreateUserError(message=f"Failed to create user", http_status=400)


    def reserve_nickname(self, nickname: str) -> None:
        """
        Reserves a nickname by creating a document in the Firestore 'nicknames' collection.

        This method ensures nickname uniqueness across the application by attempting to create
        a document with the nickname as both the document ID and a field value. Firestore's
        document ID uniqueness constraint guarantees that no two users can have the same nickname.

        This should be called BEFORE creating the user in Firebase Auth to fail fast if the
        nickname is already taken, preventing orphaned authentication records.

        Raises:
            ReserveNicknameError: If nickname reservation fails. Specific scenarios:
                - HTTP 409: Nickname is already taken by another user
                - HTTP 400: Invalid nickname format or other Firestore operation errors
        """
        try:
            self.firestore_client.create_doc(self.NICKNAMES_COLLECTION, doc_id=nickname)
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise ReserveNicknameError(message=f"Nickname already existing", http_status=409)
            raise ReserveNicknameError(message=f"Failed to create nickname", http_status=400)


    def _resolve_group_reference(self, user_data: dict) -> None:
        """
        Resolves a Firestore DocumentReference in the 'group' field to extract the complete group object.

        This helper method checks if the user_data contains a 'group' field with a DocumentReference,
        fetches the referenced group document, and replaces the reference with the complete group data.
        If the reference is invalid, missing, or the group doesn't exist, sets group to None.

        Args:
            user_data (dict): User data dictionary that may contain a 'group' DocumentReference.
                            This dict is modified in place.

        Returns:
            None: The user_data dict is modified in place.
        """
        if self.USER_GROUP in user_data and user_data[self.USER_GROUP] is not None:
            group_ref = user_data[self.USER_GROUP]
            # Check if it's a DocumentReference
            if hasattr(group_ref, 'get'):
                try:
                    group_doc = group_ref.get()
                    if group_doc.exists:
                        group_data = group_doc.to_dict()
                        # Include the complete group object with document ID
                        if group_data:
                            group_data['gid'] = group_doc.id
                            user_data[self.USER_GROUP] = group_data
                        else:
                            user_data[self.USER_GROUP] = None
                    else:
                        user_data[self.USER_GROUP] = None
                except Exception:
                    # If fetching the group fails, set to None
                    user_data[self.USER_GROUP] = None
            # If it's not a DocumentReference and not a dict, set to None
            elif not isinstance(group_ref, dict):
                user_data[self.USER_GROUP] = None

    def read_user(self, uid: str) -> dict:
        """
        Retrieves a single user document from the Firestore 'users' collection.

        This method fetches user profile data (email, name, surname, nickname) from Firestore
        using the Firebase Auth UID as the document ID. The UID is included in the returned
        dictionary for convenience.

        Raises:
            ReadUserError: If user retrieval fails. Specific scenarios:
                - HTTP 404: User document with this UID does not exist in Firestore
                - HTTP 400: Invalid UID format or other Firestore operation errors
        """
        try:
            user_data_dict = self.firestore_client.read_doc(collection_name=self.USERS_COLLECTION, doc_id=uid)
            self._resolve_group_reference(user_data_dict)
            return {self.USER_ID: uid, **user_data_dict}
        except DocumentNotFoundError:
            raise ReadUserError(message=f"User was not found", http_status=404)
        except Exception:
            raise ReadUserError(message=f"Failed to read user", http_status=400)


    def read_all_users(self) -> list[dict]:
        """
        Retrieves all user documents from the Firestore 'users' collection.

        This method fetches all user profile data stored in Firestore and returns them as a list
        of dictionaries. Each dictionary includes the UID as a field for convenient processing.

        Raises:
            ReadUserError: If retrieving users fails. Specific scenarios:
                - HTTP 400: Firestore operation errors or collection access issues
        """
        try:
            users = self.firestore_client.read_all_docs(
                collection_name=self.USERS_COLLECTION,
                include_id=True,
                id_field_name=self.USER_ID,
            )
            for user in users:
                self._resolve_group_reference(user)
            return users
        except Exception:
            raise ReadUserError(message=f"Failed to read all users", http_status=400)


    def delete_user(self, uid: str) -> None:
        """
        Deletes a user document from the Firestore 'users' collection.

        This method removes the user profile data from Firestore using the Firebase Auth UID
        as the document ID. Note that this only deletes the Firestore document and does NOT
        delete the user from Firebase Authentication.

        Raises:
            DeleteUserError: If user deletion fails. Specific scenarios:
                - HTTP 404: User document with this UID does not exist in Firestore
                - HTTP 400: Invalid UID format or other Firestore operation errors
        """
        try:
            self.firestore_client.delete_doc(collection_name=self.USERS_COLLECTION, doc_id=uid)
        except DocumentNotFoundError:
            raise DeleteUserError(message=f"User was not found", http_status=404)
        except Exception:
            raise DeleteUserError(message=f"Failed to delete user", http_status=400)


    def delete_nickname(self, nickname: str) -> None:
        """
        Deletes a nickname reservation from the Firestore 'nicknames' collection.

        This method removes a nickname document from Firestore, making the nickname available
        for future reservation. This is typically called when a user is deleted to free up
        their nickname for reuse.

        Raises:
            DeleteUserError: If nickname deletion fails. Specific scenarios:
                - HTTP 404: Nickname document does not exist in Firestore
                - HTTP 400: Invalid nickname format or other Firestore operation errors
        """
        try:
            self.firestore_client.delete_doc(collection_name=self.NICKNAMES_COLLECTION, doc_id=nickname)
        except DocumentNotFoundError as e:
            raise DeleteUserError(message=f"Nickname not found", http_status=404)
        except Exception:
            raise DeleteUserError(message=f"Failed to delete nickname", http_status=400)


    def update_user(self, uid: str, user_data: dict) -> None:
        """
        Updates an existing user document in the Firestore 'users' collection.

        This method allows partial updates to user profile data. Only the fields provided
        in the user_data dictionary (name and/or surname) will be updated. Fields not provided
        will remain unchanged. Email and nickname cannot be updated through this method.

        Raises:
            UpdateUserError: If user update fails. Specific scenarios:
                - HTTP 404: User document with this UID does not exist in Firestore
                - HTTP 400: Invalid data format or other Firestore operation errors
        """
        try:
            update_params = {}
            if user_data[self.USER_EMAIL]:
                update_params[self.USER_EMAIL] = user_data[self.USER_EMAIL]
            if user_data[self.USER_NAME]:
                update_params[self.USER_NAME] = user_data[self.USER_NAME]
            if user_data[self.USER_SURNAME]:
                update_params[self.USER_SURNAME] = user_data[self.USER_SURNAME]

            self.firestore_client.update_doc(self.USERS_COLLECTION, doc_id=uid, doc_data=update_params)
        except DocumentNotFoundError:
            raise UpdateUserError(message=f"User was not found", http_status=404)
        except Exception:
            raise UpdateUserError(message=f"Failed to update user", http_status=400)


    def assign_group_to_user(self, uid: str, gid: str) -> None:
        """
        Assigns a group to a user by storing a DocumentReference.
        """
        try:
            group_ref = self.firestore_client.db.collection(self.GROUP_COLLECTION).document(gid)

            self.firestore_client.update_doc(
                self.USERS_COLLECTION,
                doc_id=uid,
                doc_data={self.USER_GROUP: group_ref}
            )
        except DocumentNotFoundError:
            raise UpdateUserError(message=f"User not found", http_status=404)
        except Exception as e:
            raise UpdateUserError(message=f"Failed to assign group", http_status=400)
