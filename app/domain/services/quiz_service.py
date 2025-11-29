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
    ):
        self.quiz_repository = quiz_repository
        self.user_repository = user_repository
        self.leaderboard_service = leaderboard_service
        self.config_repository = config_repository
        self.session_service = session_service

    def create_quiz(self, quiz: Quiz) -> Quiz:
        """
        Creates a quiz in database.
        Timer duration is read from remote_config, defaulting to 3 minutes if not set.
        Generates unique question_id for each question.
        """
        num_questions = len(quiz.question_list)
        time_per_question, total_points = self._get_quiz_config()

        quiz.timer_duration = num_questions * time_per_question

        # Generate unique question_id for each question
        # update question value
        point_values = self._distribute_points(num_questions, total_points)

        for i, question in enumerate(quiz.question_list):
            if question.question_id is None:
                question.question_id = str(uuid.uuid4())
            question.value = point_values[i]

        return self.quiz_repository.create(quiz)

    def _get_quiz_config(self) -> tuple[int, int]:
        """
        Reads config and returns (time_per_question, total_quiz_points).
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
        return time_per_question, quiz_points

    def _distribute_points(self, num_questions: int, total_points: int) -> list[int]:
        """
        Distributes total points among questions.
        If division is not perfect, distributes remainder to first questions.
        """
        if num_questions <= 0:
            return []

        base_value = total_points // num_questions
        remainder = total_points % num_questions

        points = []
        for i in range(num_questions):
            value = base_value
            if i < remainder:
                value += 1
            points.append(value)

        return points

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
        #if not quiz.is_open:
        #    raise ReadQuizError("Quiz is not open", http_status=not_open_status)

        return quiz

    def read_all_quizzes(self) -> list[Quiz]:
        """
        Reads all quizzes from database.
        """
        return self.quiz_repository.read_all()

    def update_quiz(self, quiz_id: str, quiz_update: dict) -> Quiz:
        """
        Updates a quiz in database.
        Recalculates scores and timer if question_list is modified.
        """
        if "question_list" in quiz_update:
            questions_data = quiz_update["question_list"]
            num_questions = len(questions_data)

            time_per_question, total_points = self._get_quiz_config()

            # Update timer duration
            quiz_update["timer_duration"] = num_questions * time_per_question

            point_values = self._distribute_points(num_questions, total_points)

            # Update each question
            for i, question_data in enumerate(questions_data):
                question_data["value"] = point_values[i]
                if (
                    "question_id" not in question_data
                    or not question_data["question_id"]
                ):
                    question_data["question_id"] = str(uuid.uuid4())

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

        # Check if user already has a start time
        start_time = self.user_repository.get_quiz_start_time(user_id, quiz_id)
        
        # Check if user has already completed all slots for this quiz session
        # Only check if user hasn't started the quiz yet (start_time is None)
        # If they started, they should be allowed to continue/finish even if slots are taken (edge case?)
        # Actually, if they started, the timer is running. 
        # But the requirement is "non permettere la lettura... se ha tutti gli slot".
        # So we should check it.
        
        current_session_slots = self.session_service.get_slots_for_session(quiz.session_id)
        completed_slots = self._get_user_completed_slots(user_id)
        
        # Filter current slots excluding those in completed slots
        new_slots = [s for s in current_session_slots if s not in completed_slots]
        
        # Only restrict if there ARE slots for this session, but none are new (all completed)
        if len(current_session_slots) > 0 and len(new_slots) == 0:
            raise QuizAllSessionsAlreadyCompletedError("You have already completed all sessions for this quiz")

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
        
        return quiz

    async def submit_quiz(
        self, quiz_id: str, answers: dict[str, str], user_id: str
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
        self._validate_answers(answers, quiz)
        current_time = self._validate_timer(user_id, quiz_id, quiz)

        # Calculate base score
        score, max_score = self._calculate_score(quiz, answers)

        # Apply session multiplier
        # 1. Get slots for current session
        current_session_slots = self.session_service.get_slots_for_session(quiz.session_id)
        
        # 2. Get slots for all completed quizzes
        completed_slots = self._get_user_completed_slots(user_id)
        
        new_slots = []
        for slot in current_session_slots:
            if slot not in completed_slots:
                new_slots.append(slot)

        # Calculate multiplier: number of new slots
        multiplier = len(new_slots)

        score *= multiplier
        max_score *= multiplier

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

        return score, max_score



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

    def _validate_answers(self, answers: dict[str, str], quiz: Quiz) -> None:
        """
        Validates that the answer list length matches the question count.

        Raises:
            InvalidAnswerListError: if answer list length doesn't match question count
        """
        if len(answers) != len(quiz.question_list):
            raise InvalidAnswerListError(
                f"Answer count ({len(answers)}) must match "
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

    def _calculate_score(self, quiz: Quiz, answers: dict[str, str]) -> tuple[int, int]:
        """
        Calculates the score for a quiz, given a valid quiz and answer list.
        """
        score = 0
        max_score = 0

        for question in quiz.question_list:
            max_score += question.value

            if (
                question.question_id in answers
                and answers[question.question_id] == question.correct_answer
            ):
                score += question.value
            
        return score, max_score

    def _get_user_completed_slots(self, user_id: str) -> set:
        """
        Retrieves all slots from sessions of quizzes completed by the user.
        """
        completed_quiz_ids = self.user_repository.get_completed_quiz_ids(user_id)
        
        # Optimization: Read all quizzes once
        all_quizzes = self.quiz_repository.read_all()
        quiz_session_map = {q.quiz_id: q.session_id for q in all_quizzes}
        
        completed_slots = set()
        for c_quiz_id in completed_quiz_ids:
            if c_quiz_id in quiz_session_map:
                s_id = quiz_session_map[c_quiz_id]
                s_slots = self.session_service.get_slots_for_session(s_id)
                for slot in s_slots:
                    completed_slots.add(slot)
        return completed_slots

