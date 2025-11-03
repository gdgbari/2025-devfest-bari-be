from fastapi import status

from domain.entities.quiz import Quiz
from infrastructure.repositories.quiz_repository import QuizRepository
from infrastructure.errors.quiz_errors import ReadQuizError


class QuizService:
    """
    Service that manages all operations related to quizzes
    """

    def __init__(self, quiz_repository: QuizRepository):
        self.quiz_repository = quiz_repository

    def create_quiz(self, quiz: Quiz) -> Quiz:
        """
        Creates a quiz in database.
        """
        return self.quiz_repository.create(quiz)

    def read_quiz(self, quiz_id: str) -> Quiz:
        """
        Reads a quiz from database.
        Raises ReadQuizError if quiz is not open.
        """

        quiz = self.quiz_repository.read(quiz_id)

        # Check if quiz is open
        if not quiz.is_open:
            raise ReadQuizError("Quiz is not open", http_status=status.HTTP_403_FORBIDDEN)

        return quiz

    def read_all_quizzes(self) -> list[Quiz]:
        """
        Reads all quizzes from database.
        """
        return self.quiz_repository.read_all()

    def delete_quiz(self, quiz_id: str) -> None:
        """
        Deletes a quiz from database.
        """
        self.quiz_repository.delete(quiz_id)

