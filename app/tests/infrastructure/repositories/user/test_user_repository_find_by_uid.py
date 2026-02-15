"""
Unit tests for UserRepository.find_by_uid
"""
import pytest
from unittest.mock import Mock

from infrastructure.repositories.user.user_repository import UserRepository
from infrastructure.errors.user_errors import ReadUserError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


@pytest.mark.unit
class TestUserRepositoryFindByUid:
    """Test suite for UserRepository.find_by_uid"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def user_repository(self, mock_firestore_client):
        """Create UserRepository with mocked client"""
        return UserRepository(firestore_client=mock_firestore_client)

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
