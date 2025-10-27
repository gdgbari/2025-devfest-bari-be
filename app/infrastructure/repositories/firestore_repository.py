from domain.entities.group import Group
from domain.entities.user import User
from infrastructure.clients.firestore_client import FirestoreClient
from infrastructure.errors.firestore_errors import *
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
                collection_name="users", doc_id=user_data.uid, doc_data=user_data.to_firestore_data()
            )
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise CreateUserError(message=f"User already existing: {str(user_data.uid)}", http_status=409)
            raise CreateUserError(message=f"Failed to create user for uid {str(user_data.uid)}: {str(exception)}", http_status=400)


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
            self.firestore_client.create_doc("nicknames", doc_id=nickname)
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                raise ReserveNicknameError(message=f"Nickname already existing: {str(nickname)}", http_status=409)
            raise ReserveNicknameError(message=f"Failed to create nickname for nickname {str(nickname)}: {str(exception)}", http_status=400)


    def _resolve_group_reference(self, user_data: dict) -> None:
        """
        Resolves a Firestore DocumentReference in the 'group' field to extract the group name.

        This helper method checks if the user_data contains a 'group' field with a DocumentReference,
        fetches the referenced group document, and replaces the reference with just the group name.
        If the reference is invalid, missing, or the group doesn't exist, sets group to None.

        Args:
            user_data (dict): User data dictionary that may contain a 'group' DocumentReference.
                            This dict is modified in place.

        Returns:
            None: The user_data dict is modified in place.
        """
        if "group" in user_data and user_data["group"] is not None:
            group_ref = user_data["group"]
            # Check if it's a DocumentReference
            if hasattr(group_ref, 'get'):
                try:
                    group_doc = group_ref.get()
                    if group_doc.exists:
                        group_data = group_doc.to_dict()
                        # Extract only the name from the group
                        user_data["group"] = group_data.get("name") if group_data else None
                    else:
                        user_data["group"] = None
                except Exception:
                    # If fetching the group fails, set to None
                    user_data["group"] = None
            # If it's not a DocumentReference and not a string, set to None
            elif not isinstance(group_ref, str):
                user_data["group"] = None

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
            user_data_dict = self.firestore_client.read_doc(collection_name="users", doc_id=uid)
            self._resolve_group_reference(user_data_dict)
            return {"uid": uid, **user_data_dict}
        except DocumentNotFoundError as e:
            raise ReadUserError(message=f"Failed to read user {str(uid)}: User was not found", http_status=404)
        except Exception as e:
            raise ReadUserError(message=f"Failed to read user {str(uid)}: {str(e)}", http_status=400)


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
                collection_name="users",
                include_id=True,
                id_field_name="uid",
            )
            for user in users:
                self._resolve_group_reference(user)
            return users
        except Exception as e:
            raise ReadUserError(message=f"Failed to read all users: {str(e)}", http_status=400)


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
            self.firestore_client.delete_doc(collection_name="users",doc_id=uid)
        except DocumentNotFoundError as e:
            raise DeleteUserError(message=f"Failed to delete user {str(uid)} in firestore: User was not found", http_status=404)
        except Exception as e:
            raise DeleteUserError(message=f"Failed to delete user {str(uid)} in firestore: {str(e)}", http_status=400)


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
            self.firestore_client.delete_doc(collection_name="nicknames",doc_id=nickname)
        except DocumentNotFoundError as e:
            raise DeleteUserError(message=f"Failed to delete nickname {str(nickname)} in firestore: Nickname not found", http_status=404)
        except Exception as e:
            raise DeleteUserError(message=f"Failed to delete nickname {str(nickname)} in firestore: {str(e)}", http_status=400)


    def delete_all_users(self) -> None:
        """
        Deletes all user documents from the Firestore 'users' collection.

        This method performs a batch deletion of all user profile data from Firestore.
        WARNING: This is a destructive operation that cannot be undone. It should only be
        used for testing, data cleanup, or administrative purposes. This does NOT delete
        users from Firebase Authentication.

        Raises:
            DeleteUserError: If batch deletion fails. Specific scenarios:
                - HTTP 400: Firestore operation errors or collection access issues
        """
        try:
            self.firestore_client.delete_all_docs("users")
        except Exception as e:
            raise DeleteUserError(message=f"Failed to delete all users in firestore: {str(e)}", http_status=400)


    def delete_all_nicknames(self) -> None:
        """
        Deletes all nickname reservation documents from the Firestore 'nicknames' collection.

        This method performs a batch deletion of all nickname reservations from Firestore,
        making all nicknames available for future use. WARNING: This is a destructive operation
        that cannot be undone. It should only be used for testing, data cleanup, or
        administrative purposes.

        Raises:
            DeleteUserError: If batch deletion fails. Specific scenarios:
                - HTTP 400: Firestore operation errors or collection access issues
        """
        try:
            self.firestore_client.delete_all_docs("nicknames")
        except Exception as e:
            raise DeleteUserError(message=f"Failed to delete all nicknames in firestore: {str(e)}", http_status=400)


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
            if user_data["email"]:
                update_params["email"] = user_data["email"]
            if user_data["name"]:
                update_params["name"] = user_data["name"]
            if user_data["surname"]:
                update_params["surname"] = user_data["surname"]

            self.firestore_client.update_doc("users", doc_id=uid, doc_data=update_params)
        except DocumentNotFoundError as e:
            raise UpdateUserError(message=f"Failed to update user {str(uid)}: User was not found", http_status=404)
        except Exception as e:
            raise UpdateUserError(message=f"Failed to update user {str(uid)}: {str(e)}", http_status=400)


    def create_group(self, group_data) -> str:
        """
        Creates a new group document in the Firestore 'groups' collection.
        Returns the document ID.
        """
        try:
            doc_id = self.firestore_client.create_doc(
                collection_name="groups", doc_id=None, doc_data=group_data.to_firestore_data()
            )
            return doc_id
        except Exception as exception:
            if "ALREADY_EXISTS" in str(exception) or "already exists" in str(exception).lower():
                from infrastructure.errors.group_errors import CreateGroupError
                raise CreateGroupError(message=f"Failed to create group: {str(exception)}", http_status=409)
            from infrastructure.errors.group_errors import CreateGroupError
            raise CreateGroupError(message=f"Failed to create group: {str(exception)}", http_status=400)

    def read_group(self, gid: str) -> dict:
        """
        Retrieves a single group document from the Firestore 'groups' collection.
        """
        try:
            group_data_dict = self.firestore_client.read_doc(collection_name="groups", doc_id=gid)
            return {"gid": gid, **group_data_dict}
        except DocumentNotFoundError as e:
            from infrastructure.errors.group_errors import ReadGroupError
            raise ReadGroupError(message=f"Failed to read group {str(gid)}: Group was not found", http_status=404)
        except Exception as e:
            from infrastructure.errors.group_errors import ReadGroupError
            raise ReadGroupError(message=f"Failed to read group {str(gid)}: {str(e)}", http_status=400)

    def read_all_groups(self) -> list[dict]:
        """
        Retrieves all group documents from the Firestore 'groups' collection.
        """
        try:
            groups = self.firestore_client.read_all_docs(
                collection_name="groups",
                include_id=True,
                id_field_name="gid",
            )
            return groups
        except Exception as e:
            from infrastructure.errors.group_errors import ReadGroupError
            raise ReadGroupError(message=f"Failed to read all groups: {str(e)}", http_status=400)

    def delete_group(self, gid: str) -> None:
        """
        Deletes a group document from the Firestore 'groups' collection.
        """
        try:
            self.firestore_client.delete_doc(collection_name="groups", doc_id=gid)
        except DocumentNotFoundError as e:
            from infrastructure.errors.group_errors import DeleteGroupError
            raise DeleteGroupError(message=f"Failed to delete group {str(gid)} in firestore: Group was not found", http_status=404)
        except Exception as e:
            from infrastructure.errors.group_errors import DeleteGroupError
            raise DeleteGroupError(message=f"Failed to delete group {str(gid)} in firestore: {str(e)}", http_status=400)

    def delete_all_groups(self) -> None:
        """
        Deletes all group documents from the Firestore 'groups' collection.
        """
        try:
            self.firestore_client.delete_all_docs("groups")
        except Exception as e:
            from infrastructure.errors.group_errors import DeleteGroupError
            raise DeleteGroupError(message=f"Failed to delete all groups in firestore: {str(e)}", http_status=400)

    def update_group(self, gid: str, group_data: dict) -> None:
        """
        Updates an existing group document in the Firestore 'groups' collection.
        """
        try:
            update_params = {}
            if "name" in group_data and group_data["name"] is not None:
                update_params["name"] = group_data["name"]
            if "color" in group_data and group_data["color"] is not None:
                update_params["color"] = group_data["color"]
            if "image_url" in group_data and group_data["image_url"] is not None:
                update_params["image_url"] = group_data["image_url"]

            self.firestore_client.update_doc("groups", doc_id=gid, doc_data=update_params)
        except DocumentNotFoundError as e:
            from infrastructure.errors.group_errors import UpdateGroupError
            raise UpdateGroupError(message=f"Failed to update group {str(gid)}: Group was not found", http_status=404)
        except Exception as e:
            from infrastructure.errors.group_errors import UpdateGroupError
            raise UpdateGroupError(message=f"Failed to update group {str(gid)}: {str(e)}", http_status=400)
