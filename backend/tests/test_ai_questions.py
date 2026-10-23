from unittest.mock import MagicMock, patch
from app.db.database import get_db
from app.models import GeneratedQuestion, QuestionGeneration
from app.schemas.ai_questions import (
    QuestionGenerationResponse,
    InterviewQuestion,
)



@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_success(mock_service_class, client, db_session):
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

    generation = db_session.query(QuestionGeneration).one()

    assert generation.role == "Python Developer"
    assert generation.experience_years == 2
    assert generation.skills == ["Python", "FastAPI"]
    assert generation.difficulty == "medium"

    saved_questions = (
        db_session.query(GeneratedQuestion)
        .filter_by(generation_id=generation.id)
        .all()
    )

    assert len(saved_questions) == 2
    assert saved_questions[0].question == "What is a Python decorator?"
    assert saved_questions[0].expected_answer_points == [
        "A decorator modifies a function's behavior",
        "It uses callable wrapping",
    ]

    mock_service.generate_questions.assert_called_once()


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_configuration_error(mock_service_class, client):
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


def test_generate_questions_invalid_request(client):
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


def test_get_question_generation_history_success(client, db_session):
    from app.models import GeneratedQuestion, QuestionGeneration

    generation = QuestionGeneration(
        role="Python Developer",
        experience_years=2,
        skills=["Python", "FastAPI"],
        difficulty="medium",
    )
    generation.questions = [
        GeneratedQuestion(
            question="What is a Python decorator?",
            expected_answer_points=[
                "Modifies a function's behavior",
                "Uses callable wrapping",
            ],
        )
    ]

    db_session.add(generation)
    db_session.commit()
    db_session.refresh(generation)

    response = client.get(
        f"/api/v1/ai-questions/history/{generation.id}"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["message"] == "Question generation history retrieved successfully"
    assert body["data"]["role"] == "Python Developer"
    assert body["data"]["experience_years"] == 2
    assert len(body["data"]["questions"]) == 1
    assert body["data"]["questions"][0]["question"] == (
        "What is a Python decorator?"
    )


def test_get_question_generation_history_not_found(client):
    response = client.get("/api/v1/ai-questions/history/999999")

    assert response.status_code == 404

    body = response.json()
    assert body["status"] is False
    assert body["data"] == {}
    assert body["message"] == "Question generation history not found"
