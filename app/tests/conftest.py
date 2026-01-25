"""
Shared pytest fixtures for all tests
"""
import pytest
from unittest.mock import Mock, MagicMock

from domain.entities.user import User
from domain.entities.quiz import Quiz
from domain.entities.question import Question
from domain.entities.answer import Answer
from domain.entities.group import Group
from domain.entities.tag import Tag
from domain.entities.role import Role


# ========== Entity Fixtures ==========

@pytest.fixture
def sample_user() -> User:
    """Fixture that returns a sample User entity"""
    return User(
        uid="test-uid-123",
        email="test@example.com",
        name="Test",
        surname="User",
        nickname="testuser",
        role=Role.ATTENDEE,
        group=None,
        tags=None,
        checked_in=False
    )


@pytest.fixture
def sample_admin_user() -> User:
    """Fixture that returns an admin User entity"""
    return User(
        uid="admin-uid-123",
        email="admin@example.com",
        name="Admin",
        surname="User",
        nickname="adminuser",
        role=Role.ADMIN,
        group=None,
        tags=None,
        checked_in=True
    )


@pytest.fixture
def sample_user_with_group() -> User:
    """Fixture for user with group assigned"""
    return User(
        uid="test-uid-456",
        email="grouped@example.com",
        name="Grouped",
        surname="User",
        nickname="groupeduser",
        role=Role.ATTENDEE,
        group={"gid": "group-123", "name": "Team A"},
        tags=None,
        checked_in=True
    )


@pytest.fixture
def sample_answer() -> Answer:
    """Fixture that returns a sample Answer"""
    return Answer(
        id="answer-1",
        text="Sample Answer"
    )


@pytest.fixture
def sample_question() -> Question:
    """Fixture that returns a sample Question"""
    return Question(
        question_id="question-1",
        text="What is 2+2?",
        answer_list=[
            Answer(id="a1", text="3"),
            Answer(id="a2", text="4"),
            Answer(id="a3", text="5"),
            Answer(id="a4", text="6")
        ],
        correct_answer="a2",
        value=100
    )


@pytest.fixture
def sample_quiz(sample_question) -> Quiz:
    """Fixture that returns a sample Quiz"""
    return Quiz(
        quiz_id="quiz-123",
        title="Sample Quiz",
        question_list=[sample_question],
        is_open=True,
        session_id="session-1",
        timer_duration=60000,  # 1 minute in ms
        sessions=None
    )


@pytest.fixture
def sample_group() -> Group:
    """Fixture that returns a sample Group"""
    return Group(
        gid="group-123",
        name="Team A",
        color="#FF5733",
        image_url="https://example.com/team-a.png",
        user_count=5
    )


@pytest.fixture
def sample_tag() -> Tag:
    """Fixture that returns a sample Tag"""
    return Tag(
        tag_id="tag-1",
        points=10,
        secret="secret123"
    )


# ========== Mock Client Fixtures ==========

@pytest.fixture
def mock_firestore_client():
    """Mock FirestoreClient for repository tests"""
    mock = Mock()
    mock.get_collection.return_value = MagicMock()
    mock.db = MagicMock()
    return mock


@pytest.fixture
def mock_firebase_auth_client():
    """Mock FirebaseAuthClient for repository tests"""
    mock = Mock()
    mock.auth = MagicMock()
    return mock


@pytest.fixture
def mock_sessionize_client():
    """Mock SessionizeClient for session service tests"""
    mock = Mock()
    return mock


# ========== Mock Repository Fixtures ==========

@pytest.fixture
def mock_user_repository():
    """Mock UserRepository for service tests"""
    mock = Mock()
    mock.create.return_value = None
    mock.read.return_value = None
    mock.read_all.return_value = []
    mock.read_raw.return_value = {}
    mock.read_all_raw.return_value = []
    mock.update.return_value = None
    mock.delete.return_value = None
    mock.assign_group.return_value = None
    mock.add_tags.return_value = None
    mock.get_quiz_result.return_value = None
    mock.get_all_quiz_results.return_value = []
    mock.save_quiz_result.return_value = None
    mock.get_quiz_start_time.return_value = None
    mock.save_quiz_start_time.return_value = None
    return mock


@pytest.fixture
def mock_group_repository():
    """Mock GroupRepository for service tests"""
    mock = Mock()
    mock.create.return_value = None
    mock.read.return_value = None
    mock.read_all.return_value = []
    mock.update.return_value = None
    mock.delete.return_value = None
    mock.increment_user_count.return_value = None
    mock.decrement_user_count.return_value = None
    return mock


@pytest.fixture
def mock_tags_repository():
    """Mock TagsRepository for service tests"""
    mock = Mock()
    mock.create.return_value = None
    mock.read.return_value = None
    mock.read_all.return_value = []
    mock.update.return_value = None
    mock.delete.return_value = None
    return mock


@pytest.fixture
def mock_quiz_repository():
    """Mock QuizRepository for service tests"""
    mock = Mock()
    mock.create.return_value = None
    mock.read.return_value = None
    mock.read_all.return_value = []
    mock.update.return_value = None
    mock.delete.return_value = None
    return mock


@pytest.fixture
def mock_leaderboard_repository():
    """Mock LeaderboardRepository for service tests"""
    mock = Mock()
    mock.create_user_entry.return_value = None
    mock.create_group_entry.return_value = None
    mock.add_points_to_user.return_value = None
    mock.add_points_to_group.return_value = None
    mock.delete_user_entry.return_value = None
    mock.delete_group_entry.return_value = None
    return mock


@pytest.fixture
def mock_config_repository():
    """Mock ConfigRepository for service tests"""
    mock = Mock()
    mock.read_config.return_value = None
    mock.update_config.return_value = None
    return mock


@pytest.fixture
def mock_firestore_repository():
    """Mock FirestoreRepository for tests"""
    mock = Mock()
    mock.create_user.return_value = None
    mock.read_user.return_value = {}
    mock.read_all_users.return_value = []
    mock.update_user.return_value = None
    mock.delete_user.return_value = None
    mock.reserve_nickname.return_value = None
    mock.delete_nickname.return_value = None
    return mock


@pytest.fixture
def mock_auth_repository():
    """Mock FirebaseAuthRepository for tests"""
    mock = Mock()
    mock.create_user_authentication.return_value = "test-uid-123"
    mock.delete_auth.return_value = None
    mock.update_user_auth.return_value = None
    return mock


# ========== Mock Service Fixtures ==========

@pytest.fixture
def mock_user_service():
    """Mock UserService for endpoint tests"""
    mock = Mock()
    mock.create_user.return_value = None
    mock.read_user.return_value = None
    mock.read_all_users.return_value = []
    mock.update_user.return_value = None
    mock.delete_user.return_value = None
    mock.assign_group_to_user.return_value = None
    mock.add_tags.return_value = None
    return mock


@pytest.fixture
def mock_quiz_service():
    """Mock QuizService for endpoint tests"""
    mock = Mock()
    mock.create_quiz.return_value = None
    mock.read_quiz.return_value = None
    mock.read_all_quizzes.return_value = []
    mock.update_quiz.return_value = None
    mock.delete_quiz.return_value = None
    mock.submit_quiz.return_value = (0, 0)
    return mock


@pytest.fixture
def mock_group_service():
    """Mock GroupService for endpoint tests"""
    mock = Mock()
    mock.create_group.return_value = None
    mock.read_group.return_value = None
    mock.read_all_groups.return_value = []
    mock.update_group.return_value = None
    mock.delete_group.return_value = None
    mock.increment_user_count.return_value = None
    mock.decrement_user_count.return_value = None
    return mock


@pytest.fixture
def mock_tag_service():
    """Mock TagService for endpoint tests"""
    mock = Mock()
    mock.create_tag.return_value = None
    mock.read_tag.return_value = None
    mock.read_all_tags.return_value = []
    mock.update_tag.return_value = None
    mock.delete_tag.return_value = None
    mock.assign_tag_to_user.return_value = None
    return mock


@pytest.fixture
def mock_leaderboard_service():
    """Mock LeaderboardService for tests"""
    mock = Mock()
    mock.add_points.return_value = None
    mock.get_user_leaderboard.return_value = []
    mock.get_group_leaderboard.return_value = []
    return mock


@pytest.fixture
def mock_session_service():
    """Mock SessionService for tests"""
    mock = Mock()
    mock.ensure_sessions_synced.return_value = None
    mock.get_slots_for_session.return_value = []
    mock.sync_sessions.return_value = None
    return mock


@pytest.fixture
def mock_config_service():
    """Mock ConfigService for tests"""
    mock = Mock()
    mock.get_config.return_value = None
    mock.update_config.return_value = None
    return mock


@pytest.fixture
def mock_check_in_service():
    """Mock CheckInService for tests"""
    mock = Mock()
    mock.check_in_user.return_value = None
    return mock

