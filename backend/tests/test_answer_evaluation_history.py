from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_answer_evaluation_history_success(
    mock_service_class, client
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.get_evaluation_history.return_value = [
        MagicMock(
            id=1,
            generated_question_id=None,
            question="What is FastAPI?",
            expected_answer_points=["Python web framework"],
            user_answer="FastAPI is a Python web framework.",
            score=85,
            strengths=["Clear explanation"],
            areas_to_improve=["Add an example"],
            suggested_answer="FastAPI is a modern Python web framework.",
            feedback="Good answer.",
            created_at=datetime(2026, 10, 26, tzinfo=timezone.utc),
        )
    ]

    response = client.get("/api/v1/answer-evaluations")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["message"] == "Answer evaluation history retrieved successfully"
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == 1
    assert body["data"][0]["score"] == 85
    assert body["data"][0]["question"] == "What is FastAPI?"


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_answer_evaluation_history_empty(
    mock_service_class, client
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get("/api/v1/answer-evaluations")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["data"] == []


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_history_accepts_custom_pagination(
    mock_service_class, client
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get(
        "/api/v1/answer-evaluations?skip=0&limit=2"
    )

    assert response.status_code == 200
    mock_service.get_evaluation_history.assert_called_once_with(
        skip=0,
        limit=2,
    )


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_history_accepts_next_page(
    mock_service_class, client
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get(
        "/api/v1/answer-evaluations?skip=2&limit=2"
    )

    assert response.status_code == 200
    mock_service.get_evaluation_history.assert_called_once_with(
        skip=2,
        limit=2,
    )


def test_get_history_rejects_negative_skip(client):
    response = client.get(
        "/api/v1/answer-evaluations?skip=-1&limit=2"
    )

    assert response.status_code == 422


def test_get_history_rejects_limit_above_maximum(client):
    response = client.get(
        "/api/v1/answer-evaluations?skip=0&limit=101"
    )

    assert response.status_code == 422
