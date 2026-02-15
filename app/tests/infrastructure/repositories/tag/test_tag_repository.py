"""
Unit tests for TagRepository
"""
import pytest
from unittest.mock import Mock

from domain.entities.tag import Tag
from infrastructure.repositories.tag.tag_repository import TagRepository
from infrastructure.errors.tag_errors import ReadTagError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


@pytest.mark.unit
class TestTagRepository:
    """Test suite for TagRepository"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def tag_repository(self, mock_firestore_client):
        """Create TagRepository with mocked client"""
        return TagRepository(firestore_client=mock_firestore_client)

    @pytest.fixture
    def sample_tag_data(self):
        """Sample tag data as returned from Firestore"""
        return {
            "points": 10,
            "secret": "secret-value",
        }

    def test_find_by_tag_id_success(
        self, tag_repository, mock_firestore_client, sample_tag_data
    ):
        """Test successful find_by_tag_id returns a Tag entity"""
        mock_firestore_client.read_doc.return_value = sample_tag_data

        expected_tag = Tag(tag_id="tag-123", points=10, secret="secret-value")

        result = tag_repository.find_by_tag_id("tag-123")

        assert result == expected_tag
        mock_firestore_client.read_doc.assert_called_once_with(
            collection_name="tags", doc_id="tag-123"
        )

    def test_find_by_tag_id_not_found(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_id raises ReadTagError with 404 when tag not found"""
        mock_firestore_client.read_doc.side_effect = DocumentNotFoundError()

        with pytest.raises(ReadTagError) as exc_info:
            tag_repository.find_by_tag_id("nonexistent-tag")

        assert exc_info.value.status_code == 404
        assert "Tag not found" in exc_info.value.message

    def test_find_by_tag_id_generic_failure(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_id raises ReadTagError with 400 on generic failure"""
        mock_firestore_client.read_doc.side_effect = Exception("Connection error")

        with pytest.raises(ReadTagError) as exc_info:
            tag_repository.find_by_tag_id("tag-123")

        assert exc_info.value.status_code == 400
        assert "Failed to read tag" in exc_info.value.message

    def test_find_by_tag_ids_success(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_ids returns list of Tag entities"""
        mock_firestore_client.read_doc.side_effect = [
            {"points": 10, "secret": "s1"},
            {"points": 20, "secret": "s2"},
        ]

        expected_tags = [
            Tag(tag_id="tag-1", points=10, secret="s1"),
            Tag(tag_id="tag-2", points=20, secret="s2"),
        ]

        result = tag_repository.find_by_tag_ids(["tag-1", "tag-2"])

        assert result == expected_tags

    def test_find_by_tag_ids_empty_list(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_ids returns None for empty list"""
        result = tag_repository.find_by_tag_ids([])

        assert result is None
        mock_firestore_client.read_doc.assert_not_called()

    def test_find_by_tag_ids_none_input(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_ids returns None for None input"""
        result = tag_repository.find_by_tag_ids(None)

        assert result is None
        mock_firestore_client.read_doc.assert_not_called()

    def test_find_by_tag_ids_skips_missing_tags(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_ids skips tags that raise exceptions"""
        mock_firestore_client.read_doc.side_effect = [
            {"points": 10, "secret": "s1"},
            DocumentNotFoundError(),
            {"points": 30, "secret": "s3"},
        ]

        expected_tags = [
            Tag(tag_id="tag-1", points=10, secret="s1"),
            Tag(tag_id="tag-3", points=30, secret="s3"),
        ]

        result = tag_repository.find_by_tag_ids(["tag-1", "tag-2", "tag-3"])

        assert result == expected_tags

    def test_find_by_tag_ids_all_missing_returns_none(
        self, tag_repository, mock_firestore_client
    ):
        """Test find_by_tag_ids returns None when all tags fail"""
        mock_firestore_client.read_doc.side_effect = DocumentNotFoundError()

        result = tag_repository.find_by_tag_ids(["tag-1", "tag-2"])

        assert result is None
