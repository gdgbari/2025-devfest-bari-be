"""
Unit tests for read_user router endpoints
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.users.read_user import router
from core.authorization import verify_id_token
from core.dependencies import get_read_user_service
from core.exception_handler import register_exception_handlers
from domain.entities.user import User
from domain.entities.role import Role
from domain.entities.group import Group
from domain.entities.tag import Tag
from infrastructure.errors.auth_errors import UnauthorizedError, ForbiddenError
from infrastructure.errors.user_errors import ReadUserError


def _build_user(uid="uid-123", role=Role.ATTENDEE):
    return User(
        uid=uid,
        email="test@example.com",
        name="Test",
        surname="User",
        nickname="testuser",
        role=role,
        checked_in=True,
        group=Group(
            gid="group-1",
            name="Test Group",
            color="#FF5733",
            image_url="https://example.com/group.png",
            user_count=5,
        ),
        tags=[
            Tag(tag_id="tag-1", points=10, secret="s3cret"),
            Tag(tag_id="tag-2", points=20, secret="anoth3r"),
        ],
    )


def _build_expected_user_json(uid="uid-123", role="attendee"):
    return {
        "uid": uid,
        "email": "test@example.com",
        "name": "Test",
        "surname": "User",
        "nickname": "testuser",
        "role": role,
        "checked_in": True,
        "group": {
            "gid": "group-1",
            "name": "Test Group",
            "color": "#FF5733",
            "image_url": "https://example.com/group.png",
            "user_count": 5,
        },
        "tags": [
            {"tag_id": "tag-1", "points": 10, "secret": "s3cret"},
            {"tag_id": "tag-2", "points": 20, "secret": "anoth3r"},
        ],
    }


@pytest.mark.unit
class TestReadUser:
    """Test suite for GET /users/{uid} endpoint"""

    @pytest.fixture
    def mock_service(self):
        return Mock()

    @pytest.fixture
    def client(self, mock_service):
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: _build_user(uid="admin-1", role=Role.ADMIN)
        return TestClient(app)

    @patch("api.routers.users.read_user.check_user_role")
    def test_success_as_admin(self, mock_check_role, client, mock_service):
        user = _build_user()
        mock_service.read_user.return_value = user

        response = client.get("/users/uid-123")

        assert response.status_code == 200
        assert response.json() == _build_expected_user_json()
        mock_check_role.assert_called_once()
        mock_service.read_user.assert_called_once_with("uid-123")

    @patch("api.routers.users.read_user.check_user_role")
    def test_success_as_owner(self, mock_check_role, mock_service):
        owner = _build_user(uid="owner-1")
        mock_service.read_user.return_value = owner

        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: owner
        client = TestClient(app)

        response = client.get("/users/owner-1")

        assert response.status_code == 200
        assert response.json() == _build_expected_user_json(uid="owner-1")

    def test_unauthorized(self, mock_service):
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service

        def raise_unauthorized():
            raise UnauthorizedError()

        app.dependency_overrides[verify_id_token] = raise_unauthorized
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/users/any-uid")

        assert response.status_code == 401
        mock_service.read_user.assert_not_called()

    @patch("api.routers.users.read_user.check_user_role", side_effect=ForbiddenError())
    def test_forbidden_not_owner(self, mock_check_role, client, mock_service):
        response = client.get("/users/not-mine")

        assert response.status_code == 403
        mock_service.read_user.assert_not_called()

    @patch("api.routers.users.read_user.check_user_role")
    def test_service_exception(self, mock_check_role, mock_service):
        mock_service.read_user.side_effect = ReadUserError("read failed", http_status=400)

        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: _build_user(uid="admin-1", role=Role.ADMIN)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/users/target-1")

        assert response.status_code == 400


@pytest.mark.unit
class TestReadCurrentUser:
    """Test suite for GET /users/me endpoint"""

    @pytest.fixture
    def mock_service(self):
        return Mock()

    @pytest.fixture
    def client(self, mock_service):
        user = _build_user(uid="me-1")
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: user
        return TestClient(app)

    def test_success(self, client, mock_service):
        user = _build_user(uid="me-1")
        mock_service.read_user.return_value = user

        response = client.get("/users/me")

        assert response.status_code == 200
        assert response.json() == _build_expected_user_json(uid="me-1")
        mock_service.read_user.assert_called_once_with("me-1")

    def test_unauthorized(self, mock_service):
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service

        def raise_unauthorized():
            raise UnauthorizedError()

        app.dependency_overrides[verify_id_token] = raise_unauthorized
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/users/me")

        assert response.status_code == 401

    def test_service_exception(self, mock_service):
        mock_service.read_user.side_effect = ReadUserError("read failed", http_status=400)

        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: _build_user(uid="me-1")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/users/me")

        assert response.status_code == 400


@pytest.mark.unit
class TestReadAllUsers:
    """Test suite for GET /users endpoint"""

    @pytest.fixture
    def mock_service(self):
        return Mock()

    @pytest.fixture
    def client(self, mock_service):
        admin = _build_user(uid="admin-1", role=Role.ADMIN)
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service
        app.dependency_overrides[verify_id_token] = lambda: admin
        return TestClient(app)

    @patch("api.routers.users.read_user.check_user_role")
    def test_success(self, mock_check_role, client, mock_service):
        admin = _build_user(uid="admin-1", role=Role.ADMIN)
        user2 = _build_user(uid="user-2")
        mock_service.read_all_users.return_value = [admin, user2]

        response = client.get("/users")

        assert response.status_code == 200
        assert response.json() == {
            "users": [
                _build_expected_user_json(uid="admin-1", role="admin"),
                _build_expected_user_json(uid="user-2"),
            ],
            "total": 2,
        }
        mock_check_role.assert_called_once()
        mock_service.read_all_users.assert_called_once()

    def test_unauthorized(self, mock_service):
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_read_user_service] = lambda: mock_service

        def raise_unauthorized():
            raise UnauthorizedError()

        app.dependency_overrides[verify_id_token] = raise_unauthorized
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/users")

        assert response.status_code == 401

    @patch("api.routers.users.read_user.check_user_role", side_effect=ForbiddenError())
    def test_forbidden(self, mock_check_role, client, mock_service):
        response = client.get("/users")

        assert response.status_code == 403
        mock_service.read_all_users.assert_not_called()
