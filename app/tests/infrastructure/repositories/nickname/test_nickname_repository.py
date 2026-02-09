"""
Unit tests for NicknameRepository
"""
import pytest
from unittest.mock import Mock

from infrastructure.repositories.nickname.nickname_repository import NicknameRepository
from infrastructure.errors.user_errors import ReserveNicknameError, DeleteUserError
from infrastructure.errors.firestore_errors import DocumentNotFoundError


@pytest.mark.unit
class TestNicknameRepository:
    """Test suite for NicknameRepository"""

    @pytest.fixture
    def mock_firestore_client(self):
        """Mock FirestoreClient"""
        return Mock()

    @pytest.fixture
    def nickname_repository(self, mock_firestore_client):
        """Create NicknameRepository with mocked client"""
        return NicknameRepository(firestore_client=mock_firestore_client)

    def test_save_success(self, nickname_repository, mock_firestore_client):
        """Test successful nickname save normalizes and creates document"""
        nickname_repository.save("TestUser")

        mock_firestore_client.create_doc.assert_called_once_with(
            "nicknames", doc_id="testuser"
        )

    def test_save_nickname_already_exists(self, nickname_repository, mock_firestore_client):
        """Test save raises ReserveNicknameError with 409 when nickname already exists"""
        mock_firestore_client.create_doc.side_effect = Exception("ALREADY_EXISTS")

        with pytest.raises(ReserveNicknameError) as exc_info:
            nickname_repository.save("TestUser")

        assert exc_info.value.status_code == 409
        assert "Nickname already existing" in exc_info.value.message

    def test_save_generic_failure(self, nickname_repository, mock_firestore_client):
        """Test save raises ReserveNicknameError with 400 on generic failure"""
        mock_firestore_client.create_doc.side_effect = Exception("Connection error")

        with pytest.raises(ReserveNicknameError) as exc_info:
            nickname_repository.save("TestUser")

        assert exc_info.value.status_code == 400
        assert "Failed to create nickname" in exc_info.value.message

    def test_delete_success(self, nickname_repository, mock_firestore_client):
        """Test successful nickname deletion"""
        nickname_repository.delete("TestUser")

        mock_firestore_client.delete_doc.assert_called_once_with(
            collection_name="nicknames", doc_id="testuser"
        )

    def test_delete_not_found(self, nickname_repository, mock_firestore_client):
        """Test delete raises DeleteUserError with 404 when nickname not found"""
        mock_firestore_client.delete_doc.side_effect = DocumentNotFoundError()

        with pytest.raises(DeleteUserError) as exc_info:
            nickname_repository.delete("TestUser")

        assert exc_info.value.status_code == 404
        assert "Nickname not found" in exc_info.value.message

    def test_delete_generic_failure(self, nickname_repository, mock_firestore_client):
        """Test delete raises DeleteUserError with 400 on generic failure"""
        mock_firestore_client.delete_doc.side_effect = Exception("Connection error")

        with pytest.raises(DeleteUserError) as exc_info:
            nickname_repository.delete("TestUser")

        assert exc_info.value.status_code == 400
        assert "Failed to delete nickname" in exc_info.value.message

    def test_normalize_nickname_lowercases_and_strips_spaces(self, nickname_repository):
        """Test that nickname normalization converts to lowercase and removes spaces"""
        assert nickname_repository._normalize_nickname("Test User") == "testuser"
        assert nickname_repository._normalize_nickname("UPPER") == "upper"
        assert nickname_repository._normalize_nickname("no spaces here") == "nospaceshere"
