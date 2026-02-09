"""
Unit tests for AuthRepository
"""
import pytest
from unittest.mock import Mock

from domain.entities.user import User
from domain.entities.role import Role
from firebase_admin.auth import EmailAlreadyExistsError
from infrastructure.repositories.auth.auth_repository import AuthRepository
from infrastructure.errors.auth_errors import (
    AuthenticateUserError,
    DeleteUserAuthError,
)


@pytest.mark.unit
class TestAuthRepository:
    """Test suite for AuthRepository"""

    @pytest.fixture
    def mock_auth_client(self):
        """Mock FirebaseAuthClient"""
        return Mock()

    @pytest.fixture
    def auth_repository(self, mock_auth_client):
        """Create AuthRepository with mocked client"""
        return AuthRepository(auth_client=mock_auth_client)

    @pytest.fixture
    def input_user(self):
        """Sample user for testing"""
        return User(
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            password="securepassword123",
            role=Role.ATTENDEE,
        )

    def test_save_success(self, auth_repository, mock_auth_client, input_user):
        """Test successful user save in Firebase Auth sets uid and returns user"""
        mock_auth_client.create_user.return_value = "firebase-uid-123"

        expected_user = User(
            uid="firebase-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            password="securepassword123",
            role=Role.ATTENDEE,
        )

        result = auth_repository.save(input_user)

        assert result == expected_user
        mock_auth_client.create_user.assert_called_once_with(
            email="test@example.com",
            password="securepassword123", display_name="Test User",
        )

    def test_save_email_already_exists(self, auth_repository, mock_auth_client, input_user):
        """Test save raises AuthenticateUserError with 409 when email already exists"""
        mock_auth_client.create_user.side_effect = EmailAlreadyExistsError(
            message="Email already exists",
            cause="test",
            http_response=None,
        )

        with pytest.raises(AuthenticateUserError) as exc_info:
            auth_repository.save(input_user)

        assert exc_info.value.status_code == 409
        assert "Email already exsiting" in exc_info.value.message

    def test_save_generic_failure(self, auth_repository, mock_auth_client, input_user):
        """Test save raises AuthenticateUserError with 400 on generic failure"""
        mock_auth_client.create_user.side_effect = Exception("Firebase unavailable")

        with pytest.raises(AuthenticateUserError) as exc_info:
            auth_repository.save(input_user)

        assert exc_info.value.status_code == 400
        assert "Failed to authenticate the user" in exc_info.value.message

    def test_delete_success(self, auth_repository, mock_auth_client):
        """Test successful user deletion from Firebase Auth"""
        auth_repository.delete("uid-to-delete")

        mock_auth_client.delete_user.assert_called_once_with("uid-to-delete")

    def test_delete_failure(self, auth_repository, mock_auth_client):
        """Test delete raises DeleteUserAuthError on failure"""
        mock_auth_client.delete_user.side_effect = Exception("Firebase unavailable")

        with pytest.raises(DeleteUserAuthError) as exc_info:
            auth_repository.delete("uid-to-delete")

        assert exc_info.value.status_code == 400
        assert "Failed to delete user" in exc_info.value.message
