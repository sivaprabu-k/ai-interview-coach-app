from unittest.mock import MagicMock, patch
from app.schemas.answer_evaluation import AnswerEvaluationResponse


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationService"
)
def test_evaluate_answer_success(mock_service_class, client, auth_headers,
):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service

    mock_service.evaluate_answer.return_value = AnswerEvaluationResponse(
        score=85,
        strengths=["Explained decorators correctly"],
        areas_to_improve=["Add a practical example"],
        suggested_answer="A decorator wraps a function to extend its behavior.",
        feedback="Good understanding; include an example for clarity.",
    )

    response = client.post(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
        json={
            "question": "What is a Python decorator?",
            "expected_answer_points": [
                "Modifies function behavior",
                "Uses callable wrapping",
            ],
            "user_answer": "A decorator wraps a function to modify its behavior.",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["status"] is True
    assert body["message"] == "Answer evaluated successfully"
    assert body["data"]["score"] == 85
    assert body["data"]["strengths"] == [
        "Explained decorators correctly"
    ]
    assert body["data"]["areas_to_improve"] == [
        "Add a practical example"
    ]

    mock_service.evaluate_answer.assert_called_once()


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationService"
)
def test_evaluate_answer_configuration_error(
    mock_service_class,
    client,
    auth_headers,
):
    mock_service_class.side_effect = ValueError(
        "GEMINI_API_KEY is not configured"
    )

    response = client.post(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
        json={
            "question": "What is FastAPI?",
            "expected_answer_points": ["Python web framework"],
            "user_answer": "FastAPI is a Python web framework.",
        },
    )

    assert response.status_code == 503

    body = response.json()

    assert body["status"] is False
    assert body["data"] == {}
    assert body["status_code"] == 503
    assert body["message"] == "GEMINI_API_KEY is not configured"


def test_evaluate_answer_invalid_request(client, auth_headers):
    response = client.post(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
        json={
            "question": "",
            "expected_answer_points": [],
            "user_answer": "",
        },
    )

    assert response.status_code == 422


@patch(
    "app.api.v1.endpoints.answer_evaluation.AnswerEvaluationService"
)
def test_evaluate_answer_gemini_failure(mock_service_class, client, auth_headers):
    mock_service = MagicMock()
    mock_service_class.return_value = mock_service
    mock_service.evaluate_answer.side_effect = RuntimeError(
        "Gemini returned an empty response"
    )

    response = client.post(
        "/api/v1/answer-evaluations",
        headers=auth_headers,
        json={
            "question": "What is FastAPI?",
            "expected_answer_points": ["A Python web framework"],
            "user_answer": "FastAPI is a Python web framework.",
        },
    )

    assert response.status_code == 503

    body = response.json()
    assert body["status"] is False
    assert body["status_code"] == 503
