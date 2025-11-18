from api.schemas.quizzes.update_quiz_schema import UpdateQuizRequest, UpdateQuizResponse
from api.schemas.quizzes.base_schema import QuestionSchema, AnswerSchema
from domain.entities.quiz import Quiz
from domain.entities.question import Question
from domain.entities.answer import Answer


class UpdateQuizAdapter:
    """
    Class with static methods used for converting request and response to domain objs
    for quiz updating endpoints
    """

    @staticmethod
    def to_update_quiz_dict(request: UpdateQuizRequest) -> dict:
        """
        Convert UpdateQuizRequest to a dictionary suitable for Firestore update.
        Only includes fields that are not None.
        """
        update_dict = {}

        if request.title is not None:
            update_dict["title"] = request.title

        if request.question_list is not None:
            questions = []
            for q_schema in request.question_list:
                answers = [Answer(id=a.id, text=a.text) for a in q_schema.answer_list]
                question = Question(
                    text=q_schema.text,
                    answer_list=answers,
                    correct_answer=q_schema.correct_answer,
                    value=q_schema.value,
                    question_id=q_schema.question_id
                )
                questions.append(question)
            # Convert to firestore format
            update_dict["question_list"] = [q.to_firestore_data() for q in questions]

        if request.is_open is not None:
            update_dict["is_open"] = request.is_open

        return update_dict

    @staticmethod
    def to_update_response(quiz: Quiz) -> UpdateQuizResponse:
        """Convert Quiz domain object to UpdateQuizResponse"""

        questions_response = []
        for q in quiz.question_list:
            answers_response = [AnswerSchema(id=a.id, text=a.text) for a in q.answer_list]
            question_response = QuestionSchema(
                text=q.text,
                answer_list=answers_response,
                correct_answer=q.correct_answer,
                value=q.value,
                question_id=q.question_id
            )
            questions_response.append(question_response)

        return UpdateQuizResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            question_list=questions_response,
            is_open=quiz.is_open,
            timer_duration=quiz.timer_duration
        )

