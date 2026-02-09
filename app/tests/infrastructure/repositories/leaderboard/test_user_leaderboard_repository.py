"""
Unit tests for UserLeaderboardRepository
"""
import pytest
from unittest.mock import Mock, patch

from domain.entities.user import User
from domain.entities.role import Role
from infrastructure.repositories.leaderboard.user_leaderboard_repository import UserLeaderboardRepository
from infrastructure.errors.leaderboard_errors import CreateLeaderboardUserEntryError


@pytest.mark.unit
class TestUserLeaderboardRepository:
    """Test suite for UserLeaderboardRepository"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def leaderboard_repository(self, mock_firestore_client):
        """Create UserLeaderboardRepository with mocked client"""
        return UserLeaderboardRepository(firestore_client=mock_firestore_client)

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

    @patch.object(UserLeaderboardRepository, "_get_timestamp", return_value=1700000000000)
    def test_save_success(
        self, mock_timestamp, leaderboard_repository, mock_firestore_client, input_user
    ):
        """Test successful leaderboard entry creation with correct data"""
        leaderboard_repository.save(input_user)

        expected_data = {
            "group_color": "black",
            "nickname": "testuser",
            "score": 0,
            "updated_at": 1700000000000,
        }
        mock_firestore_client.create_doc.assert_called_once_with(
            collection_name="leaderboard_users",
            doc_id="test-uid-123",
            doc_data=expected_data,
        )

    def test_save_failure(self, leaderboard_repository, mock_firestore_client, input_user):
        """Test save raises CreateLeaderboardUserEntryError on failure"""
        mock_firestore_client.create_doc.side_effect = Exception("Firestore error")

        with pytest.raises(CreateLeaderboardUserEntryError) as exc_info:
            leaderboard_repository.save(input_user)

        assert exc_info.value.status_code == 400
        assert "Failed to create leaderboard entry" in exc_info.value.message
