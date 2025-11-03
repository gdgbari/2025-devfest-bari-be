from api.schemas.quizzes.read_quiz_schema import (
    GetQuizResponse,
    ReadQuestionSchema,
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

