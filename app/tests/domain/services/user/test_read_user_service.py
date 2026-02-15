"""
Unit tests for ReadUserService
"""
import pytest
from unittest.mock import Mock

from domain.entities.user import User
from domain.entities.group import Group
from domain.entities.tag import Tag
from domain.entities.role import Role
from domain.services.user.read_user_service import ReadUserService
from infrastructure.errors.user_errors import ReadUserError
from infrastructure.errors.group_errors import ReadGroupError
from infrastructure.errors.tag_errors import ReadTagError


@pytest.mark.unit
class TestReadUserService:
    """Test suite for ReadUserService"""

    @pytest.fixture
    def mock_user_repository(self):
        """Mock UserRepository"""
        return Mock()

    @pytest.fixture
    def mock_group_repository(self):
        """Mock GroupRepository"""
        return Mock()

    @pytest.fixture
    def mock_tag_repository(self):
        """Mock TagRepository"""
        return Mock()

    @pytest.fixture
    def read_user_service(
        self,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Create ReadUserService with mocked dependencies"""
        return ReadUserService(
            user_repository=mock_user_repository,
            group_repository=mock_group_repository,
            tag_repository=mock_tag_repository,
        )

    @pytest.fixture
    def group_ref_mock(self):
        """Mock Firestore document reference for group"""
        ref = Mock()
        ref.id = "group-123"
        return ref

    @pytest.fixture
    def sample_group(self):
        """Sample Group entity"""
        return Group(
            gid="group-123",
            name="Alpha",
            color="#FF0000",
            image_url="https://example.com/alpha.png",
            user_count=10,
        )

    @pytest.fixture
    def sample_tags(self):
        """Sample list of Tag entities"""
        return [
            Tag(tag_id="tag-1", points=10, secret="secret1"),
            Tag(tag_id="tag-2", points=20, secret="secret2"),
        ]

    def test_read_user_success_with_group_and_tags(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        group_ref_mock,
        sample_group,
        sample_tags,
    ):
        """Test successful read returns User with group and tags loaded"""
        mock_user_repository.find_by_uid.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group_ref": group_ref_mock,
            "tags": ["tag-1", "tag-2"],
            "checked_in": False,
        }
        mock_group_repository.find_by_gid.return_value = sample_group
        mock_tag_repository.find_by_tag_ids.return_value = sample_tags

        expected_user = User(
            uid="test-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=sample_group,
            tags=sample_tags,
            checked_in=False,
        )

        result = read_user_service.read_user("test-uid-123")

        assert result == expected_user
        mock_user_repository.find_by_uid.assert_called_once_with("test-uid-123")
        mock_group_repository.find_by_gid.assert_called_once_with("group-123")
        mock_tag_repository.find_by_tag_ids.assert_called_once_with(["tag-1", "tag-2"])

    def test_read_user_success_without_group(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        sample_tags,
    ):
        """Test successful read when user has no group assigned"""
        mock_user_repository.find_by_uid.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group_ref": None,
            "tags": ["tag-1", "tag-2"],
            "checked_in": False,
        }
        mock_tag_repository.find_by_tag_ids.return_value = sample_tags

        expected_user = User(
            uid="test-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            tags=sample_tags,
            checked_in=False,
        )

        result = read_user_service.read_user("test-uid-123")

        assert result == expected_user
        mock_group_repository.find_by_gid.assert_not_called()

    def test_read_user_success_without_tags(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        group_ref_mock,
        sample_group,
    ):
        """Test successful read when user has no tags"""
        mock_user_repository.find_by_uid.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group_ref": group_ref_mock,
            "tags": [],
            "checked_in": False,
        }
        mock_group_repository.find_by_gid.return_value = sample_group
        mock_tag_repository.find_by_tag_ids.return_value = None

        expected_user = User(
            uid="test-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=sample_group,
            tags=None,
            checked_in=False,
        )

        result = read_user_service.read_user("test-uid-123")

        assert result == expected_user

    def test_read_user_success_without_group_and_tags(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Test successful read when user has neither group nor tags"""
        mock_user_repository.find_by_uid.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group_ref": None,
            "tags": None,
            "checked_in": False,
        }
        mock_tag_repository.find_by_tag_ids.return_value = None

        expected_user = User(
            uid="test-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
            group=None,
            tags=None,
            checked_in=False,
        )

        result = read_user_service.read_user("test-uid-123")

        assert result == expected_user
        mock_group_repository.find_by_gid.assert_not_called()

    def test_read_user_repository_raises_read_user_error(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Test that ReadUserError from user_repository propagates"""
        mock_user_repository.find_by_uid.side_effect = ReadUserError(
            message="User was not found", http_status=404
        )

        with pytest.raises(ReadUserError) as exc_info:
            read_user_service.read_user("nonexistent-uid")

        assert exc_info.value.status_code == 404
        mock_group_repository.find_by_gid.assert_not_called()
        mock_tag_repository.find_by_tag_ids.assert_not_called()

    def test_read_user_group_repository_raises_read_group_error(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        group_ref_mock,
    ):
        """Test that ReadGroupError from group_repository propagates"""
        mock_user_repository.find_by_uid.return_value = {
            "uid": "test-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
            "group_ref": group_ref_mock,
            "tags": ["tag-1"],
            "checked_in": False,
        }
        mock_group_repository.find_by_gid.side_effect = ReadGroupError(
            message="Group not found", http_status=404
        )

        with pytest.raises(ReadGroupError) as exc_info:
            read_user_service.read_user("test-uid-123")

        assert exc_info.value.status_code == 404

    def test_read_all_users_success_with_group_and_tags(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        sample_group,
        sample_tags,
    ):
        """Test successful read_all returns list of Users with group and tags loaded"""
        group_ref_1 = Mock()
        group_ref_1.id = "group-123"
        group_ref_2 = Mock()
        group_ref_2.id = "group-123"

        mock_user_repository.find_all.return_value = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
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
                "group_ref": group_ref_2,
                "tags": ["tag-1", "tag-2"],
                "checked_in": True,
            },
        ]
        mock_group_repository.find_by_gid.return_value = sample_group
        mock_tag_repository.find_by_tag_ids.return_value = sample_tags

        result = read_user_service.read_all_users()

        assert len(result) == 2
        assert result[0] == User(
            uid="uid-1",
            email="alice@example.com",
            name="Alice",
            surname="Smith",
            nickname="alice",
            role=Role.ATTENDEE,
            group=sample_group,
            tags=sample_tags,
            checked_in=False,
        )
        assert result[1] == User(
            uid="uid-2",
            email="bob@example.com",
            name="Bob",
            surname="Jones",
            nickname="bob",
            role=Role.ATTENDEE,
            group=sample_group,
            tags=sample_tags,
            checked_in=True,
        )
        mock_user_repository.find_all.assert_called_once()
        assert mock_group_repository.find_by_gid.call_count == 2
        assert mock_tag_repository.find_by_tag_ids.call_count == 2

    def test_read_all_users_success_without_group(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        sample_tags,
    ):
        """Test read_all_users when users have no group assigned"""
        mock_user_repository.find_all.return_value = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group_ref": None,
                "tags": ["tag-1", "tag-2"],
                "checked_in": False,
            },
        ]
        mock_tag_repository.find_by_tag_ids.return_value = sample_tags

        result = read_user_service.read_all_users()

        assert len(result) == 1
        assert result[0] == User(
            uid="uid-1",
            email="alice@example.com",
            name="Alice",
            surname="Smith",
            nickname="alice",
            role=Role.ATTENDEE,
            group=None,
            tags=sample_tags,
            checked_in=False,
        )
        mock_group_repository.find_by_gid.assert_not_called()

    def test_read_all_users_success_without_tags(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
        sample_group,
    ):
        """Test read_all_users when users have no tags"""
        group_ref = Mock()
        group_ref.id = "group-123"

        mock_user_repository.find_all.return_value = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group_ref": group_ref,
                "tags": [],
                "checked_in": False,
            },
        ]
        mock_group_repository.find_by_gid.return_value = sample_group
        mock_tag_repository.find_by_tag_ids.return_value = None

        result = read_user_service.read_all_users()

        assert len(result) == 1
        assert result[0] == User(
            uid="uid-1",
            email="alice@example.com",
            name="Alice",
            surname="Smith",
            nickname="alice",
            role=Role.ATTENDEE,
            group=sample_group,
            tags=None,
            checked_in=False,
        )

    def test_read_all_users_empty_list(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Test read_all_users returns empty list when no users exist"""
        mock_user_repository.find_all.return_value = []

        result = read_user_service.read_all_users()

        assert result == []
        mock_group_repository.find_by_gid.assert_not_called()
        mock_tag_repository.find_by_tag_ids.assert_not_called()

    def test_read_all_users_repository_raises_read_user_error(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Test that ReadUserError from user_repository.find_all propagates"""
        mock_user_repository.find_all.side_effect = ReadUserError(
            message="Failed to read all users", http_status=400
        )

        with pytest.raises(ReadUserError) as exc_info:
            read_user_service.read_all_users()

        assert exc_info.value.status_code == 400
        mock_group_repository.find_by_gid.assert_not_called()
        mock_tag_repository.find_by_tag_ids.assert_not_called()

    def test_read_all_users_group_repository_raises_read_group_error(
        self,
        read_user_service,
        mock_user_repository,
        mock_group_repository,
        mock_tag_repository,
    ):
        """Test that ReadGroupError from group_repository propagates during read_all_users"""
        group_ref = Mock()
        group_ref.id = "group-123"

        mock_user_repository.find_all.return_value = [
            {
                "uid": "uid-1",
                "email": "alice@example.com",
                "name": "Alice",
                "surname": "Smith",
                "nickname": "alice",
                "role": "attendee",
                "group_ref": group_ref,
                "tags": ["tag-1"],
                "checked_in": False,
            },
        ]
        mock_group_repository.find_by_gid.side_effect = ReadGroupError(
            message="Group not found", http_status=404
        )

        with pytest.raises(ReadGroupError) as exc_info:
            read_user_service.read_all_users()

        assert exc_info.value.status_code == 404
