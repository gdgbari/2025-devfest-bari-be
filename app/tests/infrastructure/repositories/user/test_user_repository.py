"""
Unit tests for UserRepository
"""
import pytest
from unittest.mock import Mock

from domain.entities.user import User
from domain.entities.role import Role
from infrastructure.repositories.user.user_repository import UserRepository
from infrastructure.errors.user_errors import CreateUserError, DeleteUserError, ReadUserError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


@pytest.mark.unit
class TestUserRepository:
    """Test suite for UserRepository"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def user_repository(self, mock_firestore_client):
        """Create UserRepository with mocked client"""
        return UserRepository(firestore_client=mock_firestore_client)

    @pytest.fixture
    def input_user(self):
        """Sample user for testing"""
        return User(
            uid="test-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
        )

    @pytest.fixture
    def sample_user_data(self):
        """Sample user data as returned from Firestore"""
        group_ref = Mock()
        group_ref.id = "group-123"
        return {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group": group_ref,
            "tags": ["tag-1", "tag-2"],
            "checked_in": False,
        }

    def test_save_success(self, user_repository, mock_firestore_client, input_user):
        """Test successful user save creates document and returns user"""
        result = user_repository.save(input_user)

        assert result == input_user
        mock_firestore_client.create_doc.assert_called_once_with(
            collection_name="users",
            doc_id="test-uid-123",
            doc_data=input_user.to_firestore_data(),
        )

    def test_save_user_already_exists(self, user_repository, mock_firestore_client, input_user):
        """Test save raises CreateUserError with 409 when user already exists"""
        mock_firestore_client.create_doc.side_effect = Exception("ALREADY_EXISTS")

        with pytest.raises(CreateUserError) as exc_info:
            user_repository.save(input_user)

        assert exc_info.value.status_code == 409
        assert "User already existing" in exc_info.value.message

    def test_save_generic_failure(self, user_repository, mock_firestore_client, input_user):
        """Test save raises CreateUserError with 400 on generic failure"""
        mock_firestore_client.create_doc.side_effect = Exception("Connection error")

        with pytest.raises(CreateUserError) as exc_info:
            user_repository.save(input_user)

        assert exc_info.value.status_code == 400
        assert "Failed to create user" in exc_info.value.message

    def test_delete_success(self, user_repository, mock_firestore_client):
        """Test successful user deletion"""
        user_repository.delete("uid-to-delete")

        mock_firestore_client.delete_doc.assert_called_once_with(
            collection_name="users", doc_id="uid-to-delete"
        )

    def test_delete_not_found(self, user_repository, mock_firestore_client):
        """Test delete raises DeleteUserError with 404 when user not found"""
        mock_firestore_client.delete_doc.side_effect = DocumentNotFoundError()

        with pytest.raises(DeleteUserError) as exc_info:
            user_repository.delete("uid-to-delete")

        assert exc_info.value.status_code == 404
        assert "User was not found" in exc_info.value.message

    def test_delete_generic_failure(self, user_repository, mock_firestore_client):
        """Test delete raises DeleteUserError with 400 on generic failure"""
        mock_firestore_client.delete_doc.side_effect = Exception("Connection error")

        with pytest.raises(DeleteUserError) as exc_info:
            user_repository.delete("uid-to-delete")

        assert exc_info.value.status_code == 400
        assert "Failed to delete user" in exc_info.value.message

    def test_find_by_uid_success(
        self, user_repository, mock_firestore_client, sample_user_data
    ):
        """Test successful find_by_uid returns user data dict with uid and group_ref"""
        group_ref = sample_user_data["group"]
        mock_firestore_client.read_doc.return_value = sample_user_data

        expected_result = {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group": None,
            "group_ref": group_ref,
            "tags": ["tag-1", "tag-2"],
            "checked_in": False,
            "uid": "test-uid-123",
        }

        result = user_repository.find_by_uid("test-uid-123")

        assert result == expected_result
        mock_firestore_client.read_doc.assert_called_once_with(
            collection_name="users", doc_id="test-uid-123"
        )

    def test_find_by_uid_success_no_group(
        self, user_repository, mock_firestore_client
    ):
        """Test find_by_uid when user has no group"""
        user_data = {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "tags": [],
            "checked_in": False,
        }
        mock_firestore_client.read_doc.return_value = user_data

        expected_result = {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group": None,
            "group_ref": None,
            "tags": [],
            "checked_in": False,
            "uid": "test-uid-123",
        }

        result = user_repository.find_by_uid("test-uid-123")

        assert result == expected_result

    def test_find_by_uid_not_found(
        self, user_repository, mock_firestore_client
    ):
        """Test find_by_uid raises ReadUserError with 404 when user not found"""
        mock_firestore_client.read_doc.side_effect = DocumentNotFoundError()

        with pytest.raises(ReadUserError) as exc_info:
            user_repository.find_by_uid("nonexistent-uid")

        assert exc_info.value.status_code == 404
        assert "User was not found" in exc_info.value.message

    def test_find_by_uid_generic_failure(
        self, user_repository, mock_firestore_client
    ):
        """Test find_by_uid raises ReadUserError with 400 on generic failure"""
        mock_firestore_client.read_doc.side_effect = Exception("Connection error")

        with pytest.raises(ReadUserError) as exc_info:
            user_repository.find_by_uid("test-uid-123")

        assert exc_info.value.status_code == 400
        assert "Failed to read user" in exc_info.value.message

    def test_find_all_success(
        self, user_repository, mock_firestore_client
    ):
        """Test successful find_all returns list of user dicts with group_ref remapped"""
        group_ref_1 = Mock()
        group_ref_1.id = "group-123"
        group_ref_2 = Mock()
        group_ref_2.id = "group-456"

        firestore_data = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group": group_ref_1,
                "tags": ["tag-1", "tag-2"],
                "checked_in": False,
            },
            {
                "uid": "uid-2",
                "email": "bob@example.com",
                "name": "Bob",
                "surname": "Jones",
                "nickname": "bob",
                "role": "attendee",
                "group": group_ref_2,
                "tags": ["tag-3"],
                "checked_in": True,
            },
        ]
        mock_firestore_client.read_all_docs.return_value = firestore_data

        expected_result = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group": None,
                "group_ref": group_ref_1,
                "tags": ["tag-1", "tag-2"],
                "checked_in": False,
            },
            {
                "uid": "uid-2",
                "email": "bob@example.com",
                "name": "Bob",
                "surname": "Jones",
                "nickname": "bob",
                "role": "attendee",
                "group": None,
                "group_ref": group_ref_2,
                "tags": ["tag-3"],
                "checked_in": True,
            },
        ]

        result = user_repository.find_all()

        assert result == expected_result
        mock_firestore_client.read_all_docs.assert_called_once_with(
            collection_name="users",
            include_id=True,
            id_field_name="uid",
        )

    def test_find_all_success_no_group(
        self, user_repository, mock_firestore_client
    ):
        """Test find_all when users have no group"""
        firestore_data = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "tags": [],
                "checked_in": False,
            },
        ]
        mock_firestore_client.read_all_docs.return_value = firestore_data

        expected_result = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group": None,
                "group_ref": None,
                "tags": [],
                "checked_in": False,
            },
        ]

        result = user_repository.find_all()

        assert result == expected_result

    def test_find_all_empty_collection(
        self, user_repository, mock_firestore_client
    ):
        """Test find_all returns empty list when no users exist"""
        mock_firestore_client.read_all_docs.return_value = []

        result = user_repository.find_all()

        assert result == []
        mock_firestore_client.read_all_docs.assert_called_once_with(
            collection_name="users",
            include_id=True,
            id_field_name="uid",
        )

    def test_find_all_generic_failure(
        self, user_repository, mock_firestore_client
    ):
        """Test find_all raises ReadUserError with 400 on generic failure"""
        mock_firestore_client.read_all_docs.side_effect = Exception("Connection error")

        with pytest.raises(ReadUserError) as exc_info:
            user_repository.find_all()

        assert exc_info.value.status_code == 400
        assert "Failed to read all users" in exc_info.value.message
