import time
import uuid
from typing import Optional

from domain.entities.quiz import Quiz
from domain.entities.quiz_result import QuizResult
from domain.entities.quiz_start_time import QuizStartTime
from fastapi import status
from infrastructure.errors.quiz_errors import (
    InvalidAnswerListError,
    QuizAlreadySubmittedError,
    QuizStartTimeNotFoundError,
    QuizTimeUpError,
    ReadQuizError,
    QuizAllSessionsAlreadyCompletedError,
)
from infrastructure.repositories.config_repository import ConfigRepository
from infrastructure.repositories.quiz_repository import QuizRepository
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.tags_repository import TagsRepository
from domain.services.session_service import SessionService
from domain.services.leaderboard_service import LeaderboardService

BACKOFF_TIME_MS = 30 * 1000  # 30 seconds grace period
DEFAULT_TIME_PER_QUESTION_MS = 60 * 1000  # 1 minute in milliseconds
DEFAULT_QUIZ_POINTS: int = 300

class QuizService:
    """
    Service that manages all operations related to quizzes
    """

    def __init__(
        self,
        quiz_repository: QuizRepository,
        user_repository: UserRepository,
        leaderboard_service: LeaderboardService,
        config_repository: ConfigRepository,
        session_service: SessionService,
        tags_repository: TagsRepository,
    ):
        self.quiz_repository = quiz_repository
        self.user_repository = user_repository
        self.leaderboard_service = leaderboard_service
        self.config_repository = config_repository
        self.session_service = session_service
        self.tags_repository = tags_repository

    def create_quiz(self, quiz: Quiz) -> Quiz:
        """
        Creates a quiz in database.
        Timer duration is read from remote_config, defaulting to 3 minutes if not set.
        Generates unique question_id for each question.
        """
        time_per_question, question_value = self._get_config_values(quiz)
        quiz.timer_duration = len(quiz.question_list) * time_per_question

        # Generate unique question_id for each question
        # update question value
        for question in quiz.question_list:
            if question.question_id is None:
                question.question_id = str(uuid.uuid4())
            question.value = question_value

        return self.quiz_repository.create(quiz)

    def _get_config_values(self, quiz: Quiz) -> tuple[int, int]:
        """
        Calculates the time per question and the question value from the config.
        """
        try:
            config = self.config_repository.read_config()
            time_per_question = (
                config.time_per_question
                if config.time_per_question is not None
                else DEFAULT_TIME_PER_QUESTION_MS
            )
            quiz_points = config.quiz_points
        except Exception:
            # If config read fails, use default values
            time_per_question = DEFAULT_TIME_PER_QUESTION_MS
            quiz_points = DEFAULT_QUIZ_POINTS
        question_value = quiz_points // len(quiz.question_list)
        return time_per_question, question_value

    def _read_quiz(
        self, quiz_id: str, not_open_status: int = status.HTTP_403_FORBIDDEN
    ) -> Quiz:
        """
        Internal method to read a quiz from database.
        Raises ReadQuizError if quiz is not open.

        Args:
            quiz_id: The quiz ID to read
            not_open_status: HTTP status code to use when quiz is not open (default: 403)
        """

        quiz = self.quiz_repository.read(quiz_id)

        # Check if quiz is open
        if not quiz.is_open:
            raise ReadQuizError("Quiz is not open", http_status=not_open_status)

        return quiz

    def read_all_quizzes(self) -> list[Quiz]:
        """
        Reads all quizzes from database.
        """
        return self.quiz_repository.read_all()

    def update_quiz(self, quiz_id: str, quiz_update: dict) -> Quiz:
        """
        Updates a quiz in database.
        """
        return self.quiz_repository.update(quiz_id, quiz_update)

    def delete_quiz(self, quiz_id: str) -> None:
        """
        Deletes a quiz from database.
        """
        self.quiz_repository.delete(quiz_id)

    async def read_quiz(self, quiz_id: str, user_id: str) -> Quiz:
        """
        Read quiz and manage start time for the user.
        Also ensures sessions are synced before reading.

        This method is SAFE against timer resets:
        - First access: creates start_time and begins the countdown, returns full timer_duration
        - Subsequent accesses: calculates remaining time and updates quiz.timer_duration

        If timer_duration is 0 (time expired), raises QuizTimeUpError.
        Users can only read the quiz while time is still available.

        Raises:
            ReadQuizError: if quiz is not open
            QuizAlreadySubmittedError: if user has already submitted this quiz
            QuizTimeUpError: if timer has expired (timer_duration is 0)
            QuizAllSessionsAlreadyCompletedError: if user already has all quiz sessions
        """
        # Ensure sessions are synced (cached for TTL period)
        await self.session_service.ensure_sessions_synced()

        # Read quiz (checks if open)
        quiz = self._read_quiz(quiz_id)

        # Check if user has already submitted this quiz
        existing_result = self.user_repository.get_quiz_result(user_id, quiz_id)
        if existing_result:
            raise QuizAlreadySubmittedError("You have already submitted this quiz")

        # Check if user already has all quiz sessions
        self._validate_user_has_new_sessions(user_id, quiz.sessions)

        # Check if user already has a start time
        start_time = self.user_repository.get_quiz_start_time(user_id, quiz_id)
        current_time = int(time.time() * 1000)  # milliseconds

        if not start_time:
            # First time: create start time
            start_time = QuizStartTime(started_at=current_time)
            self.user_repository.save_quiz_start_time(user_id, quiz_id, start_time)
        else:
            # Calculate remaining time and update quiz timer_duration
            elapsed_time = current_time - start_time.started_at
            remaining_time = quiz.timer_duration - elapsed_time
            quiz.timer_duration = remaining_time if remaining_time > 0 else 0

            # Check if time has expired
            if quiz.timer_duration == 0:
                raise QuizTimeUpError("Quiz time has expired")

        print(quiz)

        return quiz

    def submit_quiz(
        self, quiz_id: str, answer_list: list[str], user_id: str
    ) -> tuple[int, int]:
        """
        Checks the submitted answers and calculates score.
        Returns tuple of (score, max_score).

        Score is multiplied by ratio of new sessions to total sessions.
        Example: quiz has session_1, session_2; user has session_1 -> score *= 1/2

        Validations:
        - Quiz must be open (returns 423 if not open)
        - User must not have already submitted
        - Answer list length must match question count
        - Timer must not have expired (with backoff grace period)
        """
        # Read quiz and run all validations (use 423 for not open during submit)
        quiz = self._read_quiz(quiz_id, not_open_status=status.HTTP_423_LOCKED)
        self._validate_submission(user_id, quiz_id)
        self._validate_answers(answer_list, quiz)
        current_time = self._validate_timer(user_id, quiz_id, quiz)

        # Calculate base score
        score, max_score = self._calculate_score(quiz, answer_list)

        # Apply session multiplier
        user_tag_ids = self._get_user_tag_ids(user_id)
        new_sessions = self._get_new_sessions(user_tag_ids, quiz.sessions)
        total_sessions = len(quiz.sessions)

        # Calculate multiplier: new_sessions / total_sessions
        multiplier = len(new_sessions) / total_sessions
        score = int(score * multiplier)

        # Save quiz result
        result = QuizResult(
            score=score,
            max_score=max_score,
            quiz_title=quiz.title,
            submitted_at=current_time,
        )
        self.user_repository.save_quiz_result(user_id, quiz_id, result)

        # Update leaderboard scores atomically
        self._update_leaderboard_scores(user_id, score)

        # Only add new sessions to user tags
        if new_sessions:
            self.user_repository.add_tags(user_id, new_sessions)

            # Process only new session tags for points
            tag_points = self._process_quiz_tags(new_sessions)
            if tag_points > 0:
                self._update_leaderboard_scores(user_id, tag_points)

        return score, max_score

    def _get_user_tag_ids(self, user_id: str) -> set[str]:
        """
        Gets user's tag IDs (documentIds) from Firestore.
        Returns empty set if user has no tags.
        """
        user_data = self.user_repository.read_raw(user_id)
        tag_ids = user_data.get("tags", [])
        return set(tag_ids) if tag_ids else set()

    def _get_new_sessions(self, user_tag_ids: set[str], quiz_sessions: list[str]) -> list[str]:
        """
        Returns list of quiz sessions that user doesn't already have.

        Args:
            user_tag_ids: Set of tag IDs user already has
            quiz_sessions: List of session tag IDs from quiz

        Returns:
            List of new session tag IDs
        """
        return [session for session in quiz_sessions if session not in user_tag_ids]

    def _validate_user_has_new_sessions(self, user_id: str, quiz_sessions: list[str]) -> None:
        """
        Validates that user has at least one new session from quiz.

        Raises:
            QuizAllSessionsAlreadyCompletedError: if user already has all quiz sessions
        """
        user_tag_ids = self._get_user_tag_ids(user_id)
        new_sessions = self._get_new_sessions(user_tag_ids, quiz_sessions)

        if not new_sessions:
            raise QuizAllSessionsAlreadyCompletedError(
                "You have already completed all sessions for this quiz"
            )

    def _process_quiz_tags(self, session_tags: list[str]) -> int:
        """
        Reads tags from tags collection using session_tags as documentIds,
        and returns the sum of all tag points.

        Args:
            session_tags: List of tag documentIds (e.g., ["session_1", "session_2"])

        Returns:
            Total points from all tags
        """
        total_points = 0
        for tag_id in session_tags:
            try:
                tag = self.tags_repository.read(tag_id)
                total_points += tag.points
            except Exception:
                # If tag doesn't exist, skip it
                continue
        return total_points

    def _update_leaderboard_scores(self, user_id: str, score: int) -> None:
        """
        Updates leaderboard scores for user and group atomically.

        Args:
            user_id (str): The user's UID
            score (int): The points to add
        """
        user = self.user_repository.read(user_id)
        self.leaderboard_service.add_points(user, score)

    def _validate_submission(self, user_id: str, quiz_id: str) -> None:
        """
        Validates that the user hasn't already submitted this quiz.

        Raises:
            QuizAlreadySubmittedError: if quiz was already submitted by this user
        """
        existing_result = self.user_repository.get_quiz_result(user_id, quiz_id)
        if existing_result:
            raise QuizAlreadySubmittedError("You have already submitted this quiz")

    def _validate_answers(self, answer_list: list[str], quiz: Quiz) -> None:
        """
        Validates that the answer list length matches the question count.

        Raises:
            InvalidAnswerListError: if answer list length doesn't match question count
        """
        if len(answer_list) != len(quiz.question_list):
            raise InvalidAnswerListError(
                f"Answer list length ({len(answer_list)}) must match "
                f"question count ({len(quiz.question_list)})"
            )

    def _validate_timer(self, user_id: str, quiz_id: str, quiz: Quiz) -> int:
        """
        Validates that the quiz timer hasn't expired (with backoff grace period).
        Returns the current time in milliseconds.

        Raises:
            QuizStartTimeNotFoundError: if user hasn't started the quiz yet
            QuizTimeUpError: if the timer has expired
        """
        # Check quiz start time exists
        start_time = self.user_repository.get_quiz_start_time(user_id, quiz_id)
        if not start_time:
            raise QuizStartTimeNotFoundError(
                "Quiz start time not found. Please access the quiz first."
            )

        # Validate timer hasn't expired (with backoff grace period)
        current_time = int(time.time() * 1000)  # milliseconds
        max_allowed_time = start_time.started_at + quiz.timer_duration + BACKOFF_TIME_MS

        if current_time > max_allowed_time:
            raise QuizTimeUpError("Quiz time has expired")

        return current_time

    def _calculate_score(self, quiz: Quiz, answer_list: list[str]) -> tuple[int, int]:
        """
        Calculates the score for a quiz, given a valid quiz and answer list.
        """
        score = 0
        max_score = 0

        for index, question in enumerate(quiz.question_list):
            max_score += question.value

            if (
                index < len(answer_list)
                and answer_list[index] == question.correct_answer
            ):
                score += question.value

        return score, max_score
