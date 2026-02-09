"""
Unit tests for CreateUserService
"""
import pytest
from unittest.mock import Mock

from domain.entities.user import User
from domain.entities.role import Role
from domain.services.user.create_user_service import CreateUserService
from infrastructure.errors.auth_errors import AuthenticateUserError
from infrastructure.errors.user_errors import CreateUserError
from infrastructure.errors.leaderboard_errors import CreateLeaderboardUserEntryError


@pytest.mark.unit
class TestCreateUserService:
    """Test suite for CreateUserService"""

    @pytest.fixture
    def mock_auth_repository(self):
        """Mock AuthRepository"""
        mock = Mock()
        mock.save.return_value = None
        mock.delete.return_value = None
        return mock

    @pytest.fixture
    def mock_nickname_repository(self):
        """Mock NicknameRepository"""
        mock = Mock()
        mock.save.return_value = None
        mock.delete.return_value = None
        return mock

    @pytest.fixture
    def mock_user_repository(self):
        """Mock UserRepository"""
        mock = Mock()
        mock.save.return_value = None
        mock.delete.return_value = None
        return mock

    @pytest.fixture
    def mock_user_leaderboard_repository(self):
        """Mock UserLeaderboardRepository"""
        mock = Mock()
        mock.save.return_value = None
        return mock

    @pytest.fixture
    def create_user_service(
        self,
        mock_auth_repository,
        mock_nickname_repository,
        mock_user_repository,
        mock_user_leaderboard_repository,
    ):
        """Create CreateUserService with mocked dependencies"""
        return CreateUserService(
            auth_repository=mock_auth_repository,
            nickname_repository=mock_nickname_repository,
            user_repository=mock_user_repository,
            user_leaderboard_repository=mock_user_leaderboard_repository,
        )

    @pytest.fixture
    def input_user(self):
        """User entity as input for create"""
        return User(
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            password="securepassword123",
            role=Role.ATTENDEE,
        )

    def test_create_user_success(
        self,
        create_user_service,
        mock_auth_repository,
        mock_nickname_repository,
        mock_user_repository,
        mock_user_leaderboard_repository,
        input_user,
    ):
        """Test successful user creation calls all repositories in order"""
        def auth_save_side_effect(user):
            user.uid = "generated-uid-123"
            return user
        expected_user = User(
            uid="generated-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            password="securepassword123",
            nickname="testuser",
            role=Role.ATTENDEE,
        )

        mock_auth_repository.save.side_effect = auth_save_side_effect
        result = create_user_service.create(input_user)

        assert result == expected_user
        mock_nickname_repository.save.assert_called_once_with("testuser")
        mock_auth_repository.save.assert_called_once_with(input_user)
        mock_user_repository.save.assert_called_once_with(input_user)
        mock_user_leaderboard_repository.save.assert_called_once_with(input_user)

    def test_create_user_authenticate_user_error(
        self,
        create_user_service,
        mock_auth_repository,
        mock_nickname_repository,
        mock_user_repository,
        mock_user_leaderboard_repository,
        input_user,
    ):
        """Test that AuthenticateUserError triggers nickname rollback"""
        mock_auth_repository.save.side_effect = AuthenticateUserError(
            message="Email already exsiting", http_status=409
        )

        with pytest.raises(AuthenticateUserError):
            create_user_service.create(input_user)

        mock_nickname_repository.save.assert_called_once_with("testuser")
        mock_nickname_repository.delete.assert_called_once_with("testuser")
        mock_user_repository.save.assert_not_called()
        mock_user_leaderboard_repository.save.assert_not_called()

    def test_create_user_create_user_error(
        self,
        create_user_service,
        mock_auth_repository,
        mock_nickname_repository,
        mock_user_repository,
        mock_user_leaderboard_repository,
        input_user,
    ):
        """Test that CreateUserError triggers nickname + auth rollback"""
        def auth_save_side_effect(user):
            user.uid = "generated-uid-456"
            return user

        mock_auth_repository.save.side_effect = auth_save_side_effect
        mock_user_repository.save.side_effect = CreateUserError(
            message="User already existing", http_status=409
        )

        with pytest.raises(CreateUserError):
            create_user_service.create(input_user)

        mock_nickname_repository.save.assert_called_once_with("testuser")
        mock_nickname_repository.delete.assert_called_once_with("testuser")
        mock_auth_repository.delete.assert_called_once_with("generated-uid-456")
        mock_user_leaderboard_repository.save.assert_not_called()

    def test_create_user_create_leaderboard_user_entry_error(
        self,
        create_user_service,
        mock_auth_repository,
        mock_nickname_repository,
        mock_user_repository,
        mock_user_leaderboard_repository,
        input_user,
    ):
        """Test that CreateLeaderboardUserEntryError triggers full rollback"""
        def auth_save_side_effect(user):
            user.uid = "generated-uid-789"
            return user

        mock_auth_repository.save.side_effect = auth_save_side_effect
        mock_user_leaderboard_repository.save.side_effect = CreateLeaderboardUserEntryError(
            message="Failed to create leaderboard entry", http_status=400
        )

        with pytest.raises(CreateLeaderboardUserEntryError):
            create_user_service.create(input_user)

        mock_nickname_repository.save.assert_called_once_with("testuser")
        mock_nickname_repository.delete.assert_called_once_with("testuser")
        mock_auth_repository.delete.assert_called_once_with("generated-uid-789")
        mock_user_repository.delete.assert_called_once_with("generated-uid-789")
