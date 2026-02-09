"""
Unit tests for UserRepository
"""
import pytest
from unittest.mock import Mock

from domain.entities.user import User
from domain.entities.role import Role
from infrastructure.repositories.user.user_repository import UserRepository
from infrastructure.errors.user_errors import CreateUserError, DeleteUserError
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
