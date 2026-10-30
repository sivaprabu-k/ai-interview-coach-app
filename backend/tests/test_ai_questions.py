from unittest.mock import MagicMock, patch
from app.core.security import create_access_token, hash_password
from app.models import GeneratedQuestion, QuestionGeneration, User
from app.models.interview import Interview
from app.schemas.ai_questions import (
    QuestionGenerationResponse,
    InterviewQuestion,
)


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_success(
    mock_service_class,
    client,
    db_session,
    auth_headers,
    auth_user,
):
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
        headers=auth_headers,
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

    assert generation.user_id == auth_user.id
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
def test_generate_questions_configuration_error(mock_service_class, client, auth_headers):
    mock_service_class.side_effect = ValueError(
        "GEMINI_API_KEY is not configured"
    )

    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
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


def test_generate_questions_invalid_request(client, auth_headers):
    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": -1,
            "skills": [],
            "difficulty": "invalid",
            "number_of_questions": 20,
        },
    )

    assert response.status_code == 422


def test_generate_questions_rejects_whitespace_skill(client, auth_headers):
    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python", "   "],
            "difficulty": "medium",
            "number_of_questions": 2,
        },
    )

    assert response.status_code == 422


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_links_to_interview(
    mock_service_class,
    client,
    db_session,
    auth_headers,
    auth_user,
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.generate_questions.return_value = (
        QuestionGenerationResponse(
            role="Python Developer",
            questions=[
                InterviewQuestion(
                    question="What is Python?",
                    expected_answer_points=["A programming language"],
                )
            ],
        )
    )

    interview = Interview(
        user_id=auth_user.id,
        role="Python Developer",
        difficulty="medium",
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)

    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "medium",
            "number_of_questions": 1,
            "interview_id": interview.id,
        },
    )

    assert response.status_code == 200

    generation = db_session.query(QuestionGeneration).one()
    assert generation.user_id == auth_user.id
    assert generation.interview_id == interview.id


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_interview_not_found(
    mock_service_class,
    client,
    db_session,
    auth_headers,
):
    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "medium",
            "number_of_questions": 1,
            "interview_id": 99999,
        },
    )

    assert response.status_code == 404
    mock_service_class.assert_not_called()
    assert db_session.query(QuestionGeneration).count() == 0


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_rejects_deleted_interview(
    mock_service_class,
    client,
    db_session,
    auth_headers,
    auth_user,
):
    interview = Interview(
        user_id=auth_user.id,
        role="Python Developer",
        difficulty="medium",
        is_deleted=True,
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)

    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "medium",
            "number_of_questions": 1,
            "interview_id": interview.id,
        },
    )

    assert response.status_code == 404
    mock_service_class.assert_not_called()
    assert db_session.query(QuestionGeneration).count() == 0


@patch("app.api.v1.endpoints.ai_questions.AIQuestionService")
def test_generate_questions_rejects_another_users_interview(
    mock_service_class,
    client,
    db_session,
    auth_headers,
):
    another_user = User(
        name="Another User",
        email="another-user@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )
    db_session.add(another_user)
    db_session.flush()

    interview = Interview(
        user_id=another_user.id,
        role="Python Developer",
        difficulty="medium",
    )
    db_session.add(interview)
    db_session.commit()
    db_session.refresh(interview)

    response = client.post(
        "/api/v1/ai-questions/generate",
        headers=auth_headers,
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "medium",
            "number_of_questions": 1,
            "interview_id": interview.id,
        },
    )

    assert response.status_code == 404
    mock_service_class.assert_not_called()
    assert db_session.query(QuestionGeneration).count() == 0


def test_get_question_generation_history_success(
    client,
    db_session,
    auth_headers,
    auth_user,
):
    generation = QuestionGeneration(
        user_id=auth_user.id,
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
        f"/api/v1/ai-questions/history/{generation.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["message"] == (
        "Question generation history retrieved successfully"
    )
    assert body["data"]["role"] == "Python Developer"
    assert body["data"]["experience_years"] == 2
    assert len(body["data"]["questions"]) == 1
    assert body["data"]["questions"][0]["question"] == (
        "What is a Python decorator?"
    )


def test_get_question_generation_history_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/ai-questions/history/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    body = response.json()
    assert body["status"] is False
    assert body["data"] == {}
    assert body["message"] == "Question generation history not found"


def test_get_question_generation_history_rejects_another_users_data(
    client,
    db_session,
    auth_headers,
):
    another_user = User(
        name="Another User",
        email="another-user@example.com",
        hashed_password=hash_password("TestPass123!"),
        is_active=True,
    )
    db_session.add(another_user)
    db_session.flush()

    generation = QuestionGeneration(
        user_id=another_user.id,
        role="Java Developer",
        experience_years=3,
        skills=["Java"],
        difficulty="hard",
    )
    db_session.add(generation)
    db_session.commit()
    db_session.refresh(generation)

    response = client.get(
        f"/api/v1/ai-questions/history/{generation.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["status"] is False


def test_get_question_generation_history_filtered_by_interview(
    client,
    db_session,
    auth_headers,
    auth_user,
):
    interview = Interview(
        user_id=auth_user.id,
        role="Python Developer",
        difficulty="medium",
    )
    db_session.add(interview)
    db_session.flush()

    linked_generation = QuestionGeneration(
        user_id=auth_user.id,
        interview_id=interview.id,
        role="Python Developer",
        experience_years=2,
        skills=["Python"],
        difficulty="medium",
    )

    unrelated_generation = QuestionGeneration(
        user_id=auth_user.id,
        role="Java Developer",
        experience_years=3,
        skills=["Java"],
        difficulty="hard",
    )

    db_session.add_all([linked_generation, unrelated_generation])
    db_session.commit()

    response = client.get(
        f"/api/v1/ai-questions/history?interview_id={interview.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    generations = body["data"]

    assert len(generations) == 1
    assert generations[0]["interview_id"] == interview.id
    assert generations[0]["role"] == "Python Developer"


def test_get_question_generation_history_pagination(
    client,
    db_session,
    auth_headers,
    auth_user,
):
    generations = [
        QuestionGeneration(
            user_id=auth_user.id,
            role=f"Developer {i}",
            experience_years=2,
            skills=["Python"],
            difficulty="medium",
        )
        for i in range(3)
    ]

    db_session.add_all(generations)
    db_session.commit()

    response = client.get(
        "/api/v1/ai-questions/history?skip=0&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body["data"]) == 2


def test_get_question_generation_history_rejects_invalid_pagination(client, auth_headers):
    response = client.get(
        "/api/v1/ai-questions/history?skip=-1",
        headers=auth_headers,
    )
    assert response.status_code == 422

    response = client.get(
        "/api/v1/ai-questions/history?limit=0",
        headers=auth_headers,
    )
    assert response.status_code == 422

    response = client.get(
        "/api/v1/ai-questions/history?limit=101",
        headers=auth_headers,
    )
    assert response.status_code == 422

    response = client.get(
        "/api/v1/ai-questions/history?interview_id=0",
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_generate_questions_requires_authentication(client):
    response = client.post(
        "/api/v1/ai-questions/generate",
        json={
            "role": "Python Developer",
            "experience_years": 2,
            "skills": ["Python"],
            "difficulty": "medium",
            "number_of_questions": 1,
        },
    )

    assert response.status_code == 401

def test_question_generation_history_list_requires_authentication(client):
    response = client.get("/api/v1/ai-questions/history")

    assert response.status_code == 401


def test_question_generation_history_detail_requires_authentication(client):
    response = client.get("/api/v1/ai-questions/history/1")

    assert response.status_code == 401
