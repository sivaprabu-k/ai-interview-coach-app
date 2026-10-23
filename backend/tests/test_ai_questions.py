from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.ai_questions import (
    QuestionGenerationResponse,
    InterviewQuestion,
)

client = TestClient(app)


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_success(mock_service_class):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.generate_questions.return_value = (
        QuestionGenerationResponse(
            role="Python Developer",
            questions=[
                InterviewQuestion(
                    question="What is a Python decorator?",
                    expected_answer_points=[
                        "A decorator modifies a function's behavior",
                        "It uses callable wrapping",
                    ],
                ),
                InterviewQuestion(
                    question="What is FastAPI?",
                    expected_answer_points=[
                        "A Python web framework",
                        "Supports request validation",
                    ],
                ),
            ],
        )
    )

    response = client.post(
        "/api/v1/ai-questions/generate",
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python", "FastAPI"],
            "difficulty": "medium",
            "number_of_questions": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["message"] == (
        "AI interview questions generated successfully"
    )
    assert len(body["data"]["questions"]) == 2

    mock_service.generate_questions.assert_called_once()


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_configuration_error(mock_service_class):
    mock_service_class.side_effect = ValueError(
        "GEMINI_API_KEY is not configured"
    )

    response = client.post(
        "/api/v1/ai-questions/generate",
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "easy",
            "number_of_questions": 1,
        },
    )

    assert response.status_code == 503
    assert response.json()["status"] is False
    assert response.json()["message"] == (
        "GEMINI_API_KEY is not configured"
    )


def test_generate_questions_invalid_request():
    response = client.post(
        "/api/v1/ai-questions/generate",
        json={
            "role": "Python Developer",
            "experience_years": -1,
            "skills": [],
            "difficulty": "invalid",
            "number_of_questions": 20,
        },
    )

    assert response.status_code == 422
