from api.schemas.quizzes.create_quiz_schema import CreateQuizRequest, CreateQuizResponse
from api.schemas.quizzes.base_schema import QuestionSchema, AnswerSchema
from domain.entities.quiz import Quiz
from domain.entities.question import Question
from domain.entities.answer import Answer


class CreateQuizAdapter:
    """
    Class with static methods used for converting request and response to domain objs
    for quiz creation endpoints
    """

    @staticmethod
    def to_create_quiz_domain(request: CreateQuizRequest) -> Quiz:
        """
        Convert CreateQuizRequest to Quiz domain object.
        Note: timer_duration will be set by the service from remote_config.
        """
        # Convert questions
        questions = []
        for q_schema in request.question_list:
            answers = [Answer(id=a.id, text=a.text) for a in q_schema.answer_list]
            question = Question(
                text=q_schema.text,
                answer_list=answers,
                correct_answer=q_schema.correct_answer,
                value=q_schema.value
            )
            questions.append(question)

        return Quiz(
            title=request.title,
            question_list=questions,
            is_open=False,  # Always default to False on creation
            timer_duration=0  # Will be set by service from config
        )

    @staticmethod
    def to_create_quiz_response(quiz: Quiz) -> CreateQuizResponse:
        """Convert Quiz domain object to CreateQuizResponse"""

        questions_response = []
        for q in quiz.question_list:
            answers_response = [AnswerSchema(id=a.id, text=a.text) for a in q.answer_list]
            question_response = QuestionSchema(
                text=q.text,
                answer_list=answers_response,
                correct_answer=q.correct_answer,
                value=q.value
            )
            questions_response.append(question_response)

        return CreateQuizResponse(
            quiz_id=quiz.quiz_id,
            title=quiz.title,
            question_list=questions_response,
            is_open=quiz.is_open,
            timer_duration=quiz.timer_duration  # Return in milliseconds
        )

