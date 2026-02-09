"""
Unit tests for create_user router endpoint
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.users.create_user import router
from core.dependencies import get_create_user_service
from core.exception_handler import register_exception_handlers
from domain.entities.user import User
from domain.entities.role import Role
from infrastructure.errors.auth_errors import AuthenticateUserError


@pytest.mark.unit
class TestCreateUserEndpoint:
    """Test suite for POST /users endpoint"""

    @pytest.fixture
    def mock_create_user_service(self):
        """Create a mock CreateUserService"""
        return Mock()

    @pytest.fixture
    def client(self, mock_create_user_service):
        """Create a FastAPI test client with mocked service dependency"""
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_create_user_service] = lambda: mock_create_user_service
        return TestClient(app)

    @pytest.fixture
    def valid_request_body(self):
        """Valid request payload for creating a user"""
        return {
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "password": "securepassword123",
            "role": "attendee",
        }

    def test_create_user_success(
        self,
        client,
        mock_create_user_service,
        valid_request_body,
    ):
        """Test successful user creation returns 201 with correct response"""
        created_user = User(
            uid="new-uid-123",
            email="test@example.com",
            name="Test",
            surname="User",
            nickname="testuser",
            role=Role.ATTENDEE,
        )
        mock_create_user_service.create.return_value = created_user

        response = client.post("/users", json=valid_request_body)

        assert response.status_code == 201
        assert response.json() == {
            "uid": "new-uid-123",
            "email": "test@example.com",
            "name": "Test",
            "surname": "User",
            "nickname": "testuser",
            "role": "attendee",
        }

    def test_create_user_invalid_request(
        self,
        client,
        mock_create_user_service,
    ):
        """Test that an invalid request body returns 422 Unprocessable Entity"""
        invalid_body = {
            "email": "not-an-email",
            "name": "Test",
        }

        response = client.post("/users", json=invalid_body)

        assert response.status_code == 422

    def test_create_user_service_raises_exception(
        self,
        mock_create_user_service,
        valid_request_body,
    ):
        """Test that an unhandled service exception results in a 500 error"""
        app = FastAPI()
        app.include_router(router)
        register_exception_handlers(app)
        app.dependency_overrides[get_create_user_service] = lambda: mock_create_user_service
        client = TestClient(app, raise_server_exceptions=False)

        mock_create_user_service.create.side_effect = Exception("Unexpected error")

        response = client.post("/users", json=valid_request_body)

        assert response.status_code == 500
