from domain.entities.quiz import Quiz
from infrastructure.repositories.quiz_repository import QuizRepository


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
        """
        return self.quiz_repository.read(quiz_id)

    def delete_quiz(self, quiz_id: str) -> None:
        """
        Deletes a quiz from database.
        """
        self.quiz_repository.delete(quiz_id)

