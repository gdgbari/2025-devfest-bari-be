import time
from typing import Optional

from domain.entities.quiz import Quiz
from domain.entities.quiz_result import QuizResult
from domain.entities.quiz_start_time import QuizStartTime
from fastapi import status
from infrastructure.errors.quiz_errors import (InvalidAnswerListError,
                                               QuizAlreadySubmittedError,
                                               QuizStartTimeNotFoundError,
                                               QuizTimeUpError, ReadQuizError)
from infrastructure.repositories.config_repository import ConfigRepository
from infrastructure.repositories.leaderboard_repository import \
    LeaderboardRepository
from infrastructure.repositories.quiz_repository import QuizRepository
from infrastructure.repositories.user_repository import UserRepository

BACKOFF_TIME_MS = 30 * 1000  # 30 seconds grace period
DEFAULT_TIMER_DURATION_MS = 3 * 60 * 1000  # 3 minutes in milliseconds


class QuizService:
    """
    Service that manages all operations related to quizzes
    """

    def __init__(
        self,
        quiz_repository: QuizRepository,
        user_repository: UserRepository,
        leaderboard_repository: LeaderboardRepository,
        config_repository: ConfigRepository
    ):
        self.quiz_repository = quiz_repository
        self.user_repository = user_repository
        self.leaderboard_repository = leaderboard_repository
        self.config_repository = config_repository

    def create_quiz(self, quiz: Quiz) -> Quiz:
        """
        Creates a quiz in database.
        Timer duration is read from remote_config, defaulting to 3 minutes if not set.
        Generates unique question_id for each question.
        """
        # Get timer_duration from config or use default
        try:
            config = self.config_repository.read_config()
            timer_duration = config.timer_duration if config.timer_duration is not None else DEFAULT_TIMER_DURATION_MS
        except Exception:
            # If config read fails, use default
            timer_duration = DEFAULT_TIMER_DURATION_MS

        # Set timer_duration on quiz
        quiz.timer_duration = timer_duration

        # Generate unique question_id for each question
        for question in quiz.question_list:
            if question.question_id is None:
                question.question_id = str(uuid.uuid4())

        return self.quiz_repository.create(quiz)

    def _read_quiz(self, quiz_id: str, not_open_status: int = status.HTTP_403_FORBIDDEN) -> Quiz:
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

    def read_quiz(self, quiz_id: str, user_id: str) -> Quiz:
        """
        Read quiz and manage start time for the user.

        This method is SAFE against timer resets:
        - First access: creates start_time and begins the countdown, returns full timer_duration
        - Subsequent accesses: calculates remaining time and updates quiz.timer_duration

        If timer_duration is 0 (time expired), raises QuizTimeUpError.
        Users can only read the quiz while time is still available.

        Raises:
            ReadQuizError: if quiz is not open
            QuizTimeUpError: if timer has expired (timer_duration is 0)
        """
        # Read quiz (checks if open)
        quiz = self._read_quiz(quiz_id)

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

    def submit_quiz(self, quiz_id: str, answer_list: list[str], user_id: str) -> tuple[int, int]:
        """
        Checks the submitted answers and calculates score.
        Returns tuple of (score, max_score).

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

        # Calculate score
        score, max_score = self._calculate_score(quiz, answer_list)

        # Save quiz result
        result = QuizResult(
            score=score,
            max_score=max_score,
            quiz_title=quiz.title,
            submit_at=current_time
        )
        self.user_repository.save_quiz_result(user_id, quiz_id, result)

        # Update leaderboard scores atomically
        self._update_leaderboard_scores(user_id, score)

        return score, max_score

    def _update_leaderboard_scores(self, user_id: str, score: int) -> None:
        """
        Updates leaderboard scores for user and group atomically.

        Args:
            user_id (str): The user's UID
            score (int): The points to add
        """
        # Read user to get group information
        user = self.user_repository.read(user_id)

        # Increment user score atomically
        self.leaderboard_repository.increment_user_score(user_id, score)

        # Increment group score atomically if user has a group
        if user.group and user.group.get("gid"):
            group_id = user.group.get("gid")
            self.leaderboard_repository.increment_group_score(group_id, score)


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

            if index < len(answer_list) and answer_list[index] == question.correct_answer:
                score += question.value

        return score, max_score
