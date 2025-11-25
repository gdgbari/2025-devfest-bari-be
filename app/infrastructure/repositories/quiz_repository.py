from domain.entities.quiz import Quiz
from infrastructure.errors.firestore_errors import DocumentNotFoundError
from infrastructure.errors.quiz_errors import (
    CreateQuizError,
    ReadQuizError,
    UpdateQuizError,
    DeleteQuizError
)
from infrastructure.clients.firestore_client import FirestoreClient


class QuizRepository:
    """
    Repository for managing all quiz operations with Firestore
    """

    QUIZ_COLLECTION: str = "quizzes"
    QUIZ_ID: str = "quiz_id"

    def __init__(self, firestore_client: FirestoreClient):
        self.firestore_client = firestore_client

    def create(self, quiz: Quiz) -> Quiz:
        """
        Creates a quiz in Firestore with auto-generated document ID.
        """
        try:
            quiz_id = self.firestore_client.create_doc(
                collection_name=self.QUIZ_COLLECTION,
                doc_id=None,
                doc_data=quiz.to_firestore_data()
            )
            quiz.quiz_id = quiz_id
            return quiz
        except Exception:
            raise CreateQuizError(message="Failed to create quiz", http_status=400)

    def read(self, quiz_id: str) -> Quiz:
        """
        Reads a quiz from Firestore.
        """
        try:
            quiz_data_dict = self.firestore_client.read_doc(
                collection_name=self.QUIZ_COLLECTION,
                doc_id=quiz_id
            )
            return Quiz.from_dict({self.QUIZ_ID: quiz_id, **quiz_data_dict})
        except DocumentNotFoundError:
            raise ReadQuizError(message="Quiz not found", http_status=404)
        except Exception:
            raise ReadQuizError(message="Failed to read quiz", http_status=400)

    def read_all(self) -> list[Quiz]:
        """
        Reads all quizzes from Firestore.
        """
        try:
            quizzes = self.firestore_client.read_all_docs(
                collection_name=self.QUIZ_COLLECTION,
                include_id=True,
                id_field_name=self.QUIZ_ID,
            )
            return [Quiz.from_dict(quiz) for quiz in quizzes]
        except Exception:
            raise ReadQuizError(message="Failed to read all quizzes", http_status=400)

    def update(self, quiz_id: str, quiz_update: dict) -> Quiz:
        """
        Updates a quiz in Firestore.
        """
        try:
            allowed_fields = {"title", "question_list", "is_open", "session_id", "sessions"}
            update_params = {
                k: v for k, v in quiz_update.items()
                if v is not None and k in allowed_fields
            }

            if not update_params:
                # Nothing to update, just return current quiz
                return self.read(quiz_id)

            self.firestore_client.update_doc(
                collection_name=self.QUIZ_COLLECTION,
                doc_id=quiz_id,
                doc_data=update_params
            )
            return self.read(quiz_id)
        except DocumentNotFoundError:
            raise UpdateQuizError(message="Quiz not found", http_status=404)
        except Exception:
            raise UpdateQuizError(message="Failed to update quiz", http_status=400)

    def delete(self, quiz_id: str) -> None:
        """
        Deletes a quiz from Firestore.
        """
        try:
            self.firestore_client.delete_doc(
                collection_name=self.QUIZ_COLLECTION,
                doc_id=quiz_id
            )
        except DocumentNotFoundError:
            raise DeleteQuizError(message="Quiz not found", http_status=404)
        except Exception:
            raise DeleteQuizError(message="Failed to delete quiz", http_status=400)

