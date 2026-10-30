from datetime import datetime, timezone
from unittest.mock import MagicMock, patch


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_answer_evaluation_history_success(mock_service_class, client, auth_headers):
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

    response = client.get(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
    )

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
def test_get_answer_evaluation_history_empty(mock_service_class, client, auth_headers):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["data"] == []


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_history_accepts_custom_pagination(
    mock_service_class, client, auth_headers, auth_user
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get(
        "/api/v1/answer-evaluations?skip=0&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    mock_service.get_evaluation_history.assert_called_once_with(
        user_id=auth_user.id,
        skip=0,
        limit=2,
    )


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_history_accepts_next_page(
    mock_service_class, client, auth_headers, auth_user
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_history.return_value = []

    response = client.get(
        "/api/v1/answer-evaluations?skip=2&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    mock_service.get_evaluation_history.assert_called_once_with(
        user_id=auth_user.id,
        skip=2,
        limit=2,
    )


def test_get_history_rejects_negative_skip(client, auth_headers):
    response = client.get(
        "/api/v1/answer-evaluations?skip=-1&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_get_history_rejects_limit_above_maximum(client, auth_headers):
    response = client.get(
        "/api/v1/answer-evaluations?skip=0&limit=101",
        headers=auth_headers,
    )

    assert response.status_code == 422


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_answer_evaluation_by_id_success(
    mock_service_class, client, auth_headers, auth_user
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.get_evaluation_by_id.return_value = MagicMock(
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

    response = client.get(
        "/api/v1/answer-evaluations/1",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["data"]["id"] == 1
    assert body["data"]["score"] == 85
    assert body["message"] == "Answer evaluation retrieved successfully"

    mock_service.get_evaluation_by_id.assert_called_once_with(
        1,
        user_id=auth_user.id,
    )


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationHistoryService"
)
def test_get_answer_evaluation_by_id_not_found(
    mock_service_class, client, auth_headers, auth_user
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.get_evaluation_by_id.return_value = None

    response = client.get(
        "/api/v1/answer-evaluations/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    body = response.json()
    assert body["status"] is False
    assert body["data"] == {}
    assert body["message"] == "Answer evaluation not found"

    mock_service.get_evaluation_by_id.assert_called_once_with(
        99999,
        user_id=auth_user.id,
    )
