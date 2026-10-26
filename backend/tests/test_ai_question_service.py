import json
from unittest.mock import MagicMock, patch

from pydantic import ValidationError
import pytest

from app.core.config import settings
from app.schemas.ai_questions import QuestionGenerationRequest
from app.services.ai.ai_question_service import AIQuestionService


def test_generate_questions_success():
    request = QuestionGenerationRequest(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
        number_of_questions=2,
    )

    mock_response = MagicMock()
    mock_response.text = json.dumps(
        {
            "role": "Python Developer",
            "questions": [
                {
                    "question": "What is a Python decorator?",
                    "expected_answer_points": [
                        "A function that wraps another function",
                        "Used to extend behavior",
                    ],
                },
                {
                    "question": "What is dependency injection in FastAPI?",
                    "expected_answer_points": [
                        "Provides dependencies to endpoints",
                        "Commonly implemented using Depends",
                    ],
                },
            ],
        }
    )

    with patch("app.services.ai.ai_question_service.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response

        service = AIQuestionService.__new__(AIQuestionService)
        service.client = mock_client.return_value

        result = service.generate_questions(request)

    assert result.role == "Python Developer"
    assert len(result.questions) == 2
    assert result.questions[0].question == "What is a Python decorator?"
    mock_client.return_value.models.generate_content.assert_called_once()


def test_generate_questions_unexpected_question_count():
    request = QuestionGenerationRequest(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
        number_of_questions=2,
    )

    mock_response = MagicMock()
    mock_response.text = json.dumps(
        {
            "role": "Python Developer",
            "questions": [
                {
                    "question": "What is a Python decorator?",
                    "expected_answer_points": [
                        "Modifies a function's behavior",
                    ],
                },
            ],
        }
    )

    with patch("app.services.ai.ai_question_service.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response

        service = AIQuestionService.__new__(AIQuestionService)
        service.client = mock_client.return_value

        with pytest.raises(
            ValueError,
            match="Gemini returned an unexpected number of questions",
        ):
            service.generate_questions(request)



def test_generate_questions_rejects_empty_answer_points():
    request = QuestionGenerationRequest(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
        number_of_questions=1,
    )

    mock_response = MagicMock()
    mock_response.text = json.dumps(
        {
            "role": "Python Developer",
            "questions": [
                {
                    "question": "What is a Python decorator?",
                    "expected_answer_points": [],
                }
            ],
        }
    )

    with patch("app.services.ai.ai_question_service.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response

        service = AIQuestionService.__new__(AIQuestionService)
        service.client = mock_client.return_value

        with pytest.raises(ValidationError):
            service.generate_questions(request)


def test_generate_questions_invalid_json():
    request = QuestionGenerationRequest(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
        number_of_questions=1,
    )

    mock_response = MagicMock()
    mock_response.text = "This is not valid JSON"

    with patch("app.services.ai.ai_question_service.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response

        service = AIQuestionService.__new__(AIQuestionService)
        service.client = mock_client.return_value

        with pytest.raises(
            RuntimeError,
            match="Gemini returned invalid JSON",
        ):
            service.generate_questions(request)


def test_generate_questions_empty_response():
    request = QuestionGenerationRequest(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
        number_of_questions=1,
    )

    mock_response = MagicMock()
    mock_response.text = ""

    with patch("app.services.ai.ai_question_service.genai.Client") as mock_client:
        mock_client.return_value.models.generate_content.return_value = mock_response

        service = AIQuestionService.__new__(AIQuestionService)
        service.client = mock_client.return_value

        with pytest.raises(
            RuntimeError,
            match="Gemini returned an empty response",
        ):
            service.generate_questions(request)
