from api.schemas.quizzes.read_quiz_schema import (
    GetQuizResponse,
    GetQuizWithCorrectResponse,
    GetQuizListWithCorrectResponse,
    ReadQuestionSchema,
    ReadQuestionWithCorrectSchema,
    ReadAnswerSchema,
)
from domain.entities.quiz import Quiz


class ReadQuizAdapter:
    """
    Class with static methods used for converting domain objects to response
    for quiz reading endpoints
    """

    @staticmethod
    def to_get_quiz_response(quiz: Quiz) -> GetQuizResponse:
        """
        Convert Quiz domain object to GetQuizResponse.

        Note: correct_answer is NOT included in the response for security
        """

        questions_response = []
        for q in quiz.question_list:
            # Convert answers without exposing which one is correct
            answers_response = [
                ReadAnswerSchema(id=a.id, text=a.text) for a in q.answer_list
            ]
            question_response = ReadQuestionSchema(
                text=q.text,
                answer_list=answers_response,
                value=q.value,
            )
            questions_response.append(question_response)

        return GetQuizResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            question_list=questions_response,
            is_open=quiz.is_open,
            timer_duration=quiz.timer_duration,
        )

    @staticmethod
    def to_get_quiz_with_correct_response(quiz: Quiz) -> GetQuizWithCorrectResponse:
        """
        Convert Quiz domain object to GetQuizWithCorrectResponse.

        Note: Includes correct_answer - for staff use only
        """

        questions_response = []
        for q in quiz.question_list:
            # Convert answers including which one is correct
            answers_response = [
                ReadAnswerSchema(id=a.id, text=a.text) for a in q.answer_list
            ]
            question_response = ReadQuestionWithCorrectSchema(
                text=q.text,
                answer_list=answers_response,
                correct_answer=q.correct_answer,
                value=q.value,
            )
            questions_response.append(question_response)

        return GetQuizWithCorrectResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            question_list=questions_response,
            is_open=quiz.is_open,
            timer_duration=quiz.timer_duration,
        )

    @staticmethod
    def to_get_quizzes_with_correct_response(quizzes: list[Quiz]) -> GetQuizListWithCorrectResponse:
        """Convert list of Quiz domain objects to GetQuizListWithCorrectResponse (staff only)"""
        return GetQuizListWithCorrectResponse(
            quizzes=[
                ReadQuizAdapter.to_get_quiz_with_correct_response(quiz)
                for quiz in quizzes
            ],
            total=len(quizzes),
        )

