"""
Unit tests for GroupRepository
"""
import pytest
from unittest.mock import Mock

from domain.entities.group import Group
from infrastructure.repositories.group.group_repository import GroupRepository
from infrastructure.errors.group_errors import ReadGroupError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


@pytest.mark.unit
class TestGroupRepository:
    """Test suite for GroupRepository"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def group_repository(self, mock_firestore_client):
        """Create GroupRepository with mocked client"""
        return GroupRepository(firestore_client=mock_firestore_client)

    @pytest.fixture
    def sample_group_data(self):
        """Sample group data as returned from Firestore"""
        return {
            "name": "Alpha",
            "color": "#FF0000",
            "image_url": "https://example.com/alpha.png",
            "user_count": 10,
        }

    def test_find_by_gid_success(
        self, group_repository, mock_firestore_client, sample_group_data
    ):
        """Test successful find_by_gid returns a Group entity"""
        mock_firestore_client.read_doc.return_value = sample_group_data

        expected_group = Group(
            gid="group-123",
            name="Alpha",
            color="#FF0000",
            image_url="https://example.com/alpha.png",
            user_count=10,
        )

        result = group_repository.find_by_gid("group-123")

        assert result == expected_group
        mock_firestore_client.read_doc.assert_called_once_with(
            collection_name="groups", doc_id="group-123"
        )

    def test_find_by_gid_not_found(
        self, group_repository, mock_firestore_client
    ):
        """Test find_by_gid raises ReadGroupError with 404 when group not found"""
        mock_firestore_client.read_doc.side_effect = DocumentNotFoundError()

        with pytest.raises(ReadGroupError) as exc_info:
            group_repository.find_by_gid("nonexistent-gid")

        assert exc_info.value.status_code == 404
        assert "Group not found" in exc_info.value.message

    def test_find_by_gid_generic_failure(
        self, group_repository, mock_firestore_client
    ):
        """Test find_by_gid raises ReadGroupError with 400 on generic failure"""
        mock_firestore_client.read_doc.side_effect = Exception("Connection error")

        with pytest.raises(ReadGroupError) as exc_info:
            group_repository.find_by_gid("group-123")

        assert exc_info.value.status_code == 400
        assert "Failed to read group" in exc_info.value.message
