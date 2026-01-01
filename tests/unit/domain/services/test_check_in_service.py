"""
Unit tests for CheckInService
"""
import pytest
from unittest.mock import Mock, call
from domain.services.check_in_service import CheckInService
from domain.entities.user import User
from domain.entities.role import Role
from infrastructure.errors.config_errors import CheckInNotOpenError
from infrastructure.errors.auth_errors import ForbiddenError


@pytest.mark.unit
class TestCheckInService:
    """Test suite for CheckInService"""

    @pytest.fixture
    def check_in_service(
        self,
        mock_user_service,
        mock_group_service,
        mock_config_service,
        mock_leaderboard_repository
    ):
        """Create CheckInService instance with mocked dependencies"""
        return CheckInService(
            user_service=mock_user_service,
            group_service=mock_group_service,
            config_service=mock_config_service,
            leaderboard_repository=mock_leaderboard_repository
        )

    def test_check_in_user_already_has_group_and_checked_in(
        self,
        check_in_service,
        mock_user_service
    ):
        """Test check-in when user already has group and is checked_in"""
        # Arrange
        user_with_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-1", "name": "Team A", "color": "#FF0000"},
            checked_in=True
        )
        mock_user_service.read_user.return_value = user_with_group

        # Act
        result = check_in_service.check_in("user-123")

        # Assert
        assert result == user_with_group
        mock_user_service.read_user.assert_called_once_with("user-123")
        # Should NOT call update_user since already checked_in
        mock_user_service.update_user.assert_not_called()

    def test_check_in_user_already_has_group_but_not_checked_in(
        self,
        check_in_service,
        mock_user_service
    ):
        """Test check-in when user has group but checked_in is False"""
        # Arrange
        user_with_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-1", "name": "Team A", "color": "#FF0000"},
            checked_in=False
        )
        mock_user_service.read_user.return_value = user_with_group

        # Act
        result = check_in_service.check_in("user-123")

        # Assert
        assert result.checked_in is True
        mock_user_service.read_user.assert_called_once_with("user-123")
        # Should call update_user to set checked_in to True
        mock_user_service.update_user.assert_called_once_with("user-123", {"checked_in": True})

    def test_check_in_raises_error_when_check_in_not_open(
        self,
        check_in_service,
        mock_user_service,
        mock_config_service
    ):
        """Test that check-in raises CheckInNotOpenError when check-in is closed"""
        # Arrange
        user_without_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            checked_in=False
        )
        mock_user_service.read_user.return_value = user_without_group
        mock_config_service.is_check_in_open.return_value = False

        # Act & Assert
        with pytest.raises(CheckInNotOpenError):
            check_in_service.check_in("user-123")

        # Verify check was performed
        mock_config_service.is_check_in_open.assert_called_once()

    def test_check_in_success_assigns_group_to_new_user(
        self,
        check_in_service,
        mock_user_service,
        mock_group_service,
        mock_config_service,
        mock_leaderboard_repository
    ):
        """Test successful check-in for user without group"""
        # Arrange
        user_without_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            checked_in=False
        )

        user_with_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-2", "name": "Team B", "color": "#00FF00"},
            checked_in=True
        )

        mock_user_service.read_user.return_value = user_without_group
        mock_config_service.is_check_in_open.return_value = True
        mock_group_service.increment_group_counter.return_value = "group-2"
        mock_user_service.assign_group_to_user.return_value = user_with_group

        # Act
        result = check_in_service.check_in("user-123")

        # Assert
        assert result == user_with_group
        assert result.group is not None
        assert result.group["gid"] == "group-2"

        # Verify flow
        mock_user_service.read_user.assert_called_once_with("user-123")
        mock_config_service.is_check_in_open.assert_called_once()
        mock_group_service.increment_group_counter.assert_called_once()
        mock_user_service.assign_group_to_user.assert_called_once_with("user-123", "group-2")

    def test_check_in_creates_leaderboard_entries(
        self,
        check_in_service,
        mock_user_service,
        mock_group_service,
        mock_config_service,
        mock_leaderboard_repository
    ):
        """Test that check-in creates leaderboard entries with correct data"""
        # Arrange
        user_without_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            checked_in=False
        )

        user_with_group = User(
            uid="user-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-3", "name": "Team C", "color": "#0000FF"},
            checked_in=True
        )

        mock_user_service.read_user.return_value = user_without_group
        mock_config_service.is_check_in_open.return_value = True
        mock_group_service.increment_group_counter.return_value = "group-3"
        mock_user_service.assign_group_to_user.return_value = user_with_group

        # Act
        result = check_in_service.check_in("user-123")

        # Assert
        # Verify leaderboard entries were created
        mock_leaderboard_repository.create_group_entry.assert_called_once_with(
            group_id="group-3",
            group_name="Team C",
            group_color="#0000FF"
        )
        mock_leaderboard_repository.update_user_group_color.assert_called_once_with(
            "user-123",
            "#0000FF"
        )

    def test_create_leaderboard_entries_with_complete_group_data(
        self,
        check_in_service,
        mock_leaderboard_repository
    ):
        """Test _create_leaderboard_entries with complete group data"""
        # Arrange
        user = User(
            uid="user-456",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-4", "name": "Team D", "color": "#FFFF00"},
            checked_in=True
        )

        # Act
        check_in_service._create_leaderboard_entries(user, "group-4")

        # Assert
        mock_leaderboard_repository.create_group_entry.assert_called_once_with(
            group_id="group-4",
            group_name="Team D",
            group_color="#FFFF00"
        )
        mock_leaderboard_repository.update_user_group_color.assert_called_once_with(
            "user-456",
            "#FFFF00"
        )

    def test_create_leaderboard_entries_without_group(
        self,
        check_in_service,
        mock_leaderboard_repository
    ):
        """Test _create_leaderboard_entries when user has no group"""
        # Arrange
        user = User(
            uid="user-789",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            checked_in=False
        )

        # Act
        check_in_service._create_leaderboard_entries(user, "group-5")

        # Assert
        # Should not create any leaderboard entries
        mock_leaderboard_repository.create_group_entry.assert_not_called()
        mock_leaderboard_repository.update_user_group_color.assert_not_called()

    def test_create_leaderboard_entries_missing_group_name(
        self,
        check_in_service,
        mock_leaderboard_repository
    ):
        """Test _create_leaderboard_entries when group data is incomplete (missing name)"""
        # Arrange
        user = User(
            uid="user-999",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-6", "color": "#FF00FF"},  # Missing 'name'
            checked_in=True
        )

        # Act
        check_in_service._create_leaderboard_entries(user, "group-6")

        # Assert
        # Should not create leaderboard entries if data is incomplete
        mock_leaderboard_repository.create_group_entry.assert_not_called()
        mock_leaderboard_repository.update_user_group_color.assert_not_called()

    def test_create_leaderboard_entries_missing_group_color(
        self,
        check_in_service,
        mock_leaderboard_repository
    ):
        """Test _create_leaderboard_entries when group data is incomplete (missing color)"""
        # Arrange
        user = User(
            uid="user-888",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-7", "name": "Team G"},  # Missing 'color'
            checked_in=True
        )

        # Act
        check_in_service._create_leaderboard_entries(user, "group-7")

        # Assert
        # Should not create leaderboard entries if data is incomplete
        mock_leaderboard_repository.create_group_entry.assert_not_called()
        mock_leaderboard_repository.update_user_group_color.assert_not_called()

    def test_check_in_flow_order(
        self,
        check_in_service,
        mock_user_service,
        mock_group_service,
        mock_config_service,
        mock_leaderboard_repository
    ):
        """Test that check-in operations happen in correct order"""
        # Arrange
        user_without_group = User(
            uid="user-order",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            checked_in=False
        )

        user_with_group = User(
            uid="user-order",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group={"gid": "group-order", "name": "Team Order", "color": "#123456"},
            checked_in=True
        )

        mock_user_service.read_user.return_value = user_without_group
        mock_config_service.is_check_in_open.return_value = True
        mock_group_service.increment_group_counter.return_value = "group-order"
        mock_user_service.assign_group_to_user.return_value = user_with_group

        # Create a manager to track call order
        manager = Mock()
        manager.attach_mock(mock_user_service.read_user, 'read_user')
        manager.attach_mock(mock_config_service.is_check_in_open, 'is_check_in_open')
        manager.attach_mock(mock_group_service.increment_group_counter, 'increment_group_counter')
        manager.attach_mock(mock_user_service.assign_group_to_user, 'assign_group_to_user')
        manager.attach_mock(mock_leaderboard_repository.create_group_entry, 'create_group_entry')

        # Act
        check_in_service.check_in("user-order")

        # Assert - verify order of calls
        expected_calls = [
            call.read_user("user-order"),
            call.is_check_in_open(),
            call.increment_group_counter(),
            call.assign_group_to_user("user-order", "group-order"),
            call.create_group_entry(
                group_id="group-order",
                group_name="Team Order",
                group_color="#123456"
            )
        ]

        assert manager.mock_calls == expected_calls

