from fastapi.testclient import TestClient
from app.main import app
from app.core.config import Settings
from sqlalchemy import text

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to AI Interview Coach!"


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_settings_reads_environment_variable(monkeypatch):
    monkeypatch.setenv("APP_NAME", "Interview Coach Test")

    test_settings = Settings()

    assert test_settings.app_name == "Interview Coach Test"


def test_database_connection(db_session):
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_create_interview(client, auth_headers):
    response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "medium",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201

    result = response.json()

    assert result["status"] is True
    assert result["data"] == {}
    assert result["status_code"] == 201
    assert result["message"] == "Interview created successfully"


def test_create_interview_invalid_role(client, auth_headers):
    response = client.post(
        "/api/v1/interviews",
        json={
            "role": "A",
            "difficulty": "medium",
        },
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_interviews_pagination(client, auth_headers):
    response = client.get(
        "/api/v1/interviews?skip=0&limit=5",
        headers=auth_headers,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] is True
    assert result["status_code"] == 200
    assert result["message"] == "Interviews retrieved successfully"

    data = result["data"]

    assert isinstance(data, dict)
    assert isinstance(data["interviews"], list)
    assert data["skip"] == 0
    assert data["limit"] == 5
    assert isinstance(data["total"], int)
    assert data["total"] >= len(data["interviews"])
    assert len(data["interviews"]) <= 5


def test_list_interviews_invalid_pagination(client, auth_headers):
    response = client.get(
        "/api/v1/interviews?skip=-1&limit=101",
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_list_interviews_total_count(client, auth_headers):
    response = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["total"] == len(data["interviews"])


def test_get_interview_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/interviews/9999",
        headers=auth_headers,
    )

    assert response.status_code == 404

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 404
    assert result["message"] == "Interview not found"


def test_get_interview_by_id(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
        headers=auth_headers,
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews?skip=0&limit=5",
        headers=auth_headers,
    )
    assert list_response.status_code == 200

    interviews = list_response.json()["data"]["interviews"]
    matching_interviews = [
        item for item in interviews
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Beginner"
    ]
    assert matching_interviews

    interview_id = matching_interviews[-1]["id"]

    response = client.get(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    result = response.json()
    assert result["status"] is True
    assert result["data"]["id"] == interview_id
    assert result["data"]["role"] == "Python Developer"
    assert result["data"]["difficulty"] == "Beginner"
    assert result["message"] == "Interview retrieved successfully"


def test_update_interview(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews?skip=0&limit=5",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Beginner"
    )

    update_response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"difficulty": "Advanced"},
        headers=auth_headers,
    )

    assert update_response.status_code == 200

    result = update_response.json()
    assert result["status"] is True
    assert result["data"]["id"] == interview_id
    assert result["data"]["role"] == "Python Developer"
    assert result["data"]["difficulty"] == "Advanced"
    assert result["message"] == "Interview updated successfully"


def test_update_interview_not_found(client, auth_headers):
    response = client.put(
        "/api/v1/interviews/9999",
        json={"difficulty": "Advanced"},
        headers=auth_headers,
    )

    assert response.status_code == 404

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 404
    assert result["message"] == "Interview not found"


def test_update_interview_null_field(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews?skip=0&limit=5",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Beginner"
    )

    response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"difficulty": None},
        headers=auth_headers,
    )

    assert response.status_code == 422

    result = response.json()
    assert result["status"] is False
    assert result["status_code"] == 422
    assert result["message"] == "Fields cannot be null"


def test_update_interview_empty_body(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews?skip=0&limit=5",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Beginner"
    )

    response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={},
        headers=auth_headers,
    )

    assert response.status_code == 400

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 400
    assert result["message"] == "At least one field must be provided"


def test_delete_interview_soft_delete(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Medium"
    )

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] is True
    assert delete_response.json()["data"] == {}

    detail_response = client.get(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert detail_response.status_code == 404

    list_after_delete = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    remaining_ids = [
        item["id"]
        for item in list_after_delete.json()["data"]["interviews"]
    ]
    assert interview_id not in remaining_ids


def test_delete_interview_not_found(client, auth_headers):
    response = client.delete(
        "/api/v1/interviews/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["status"] is False
    assert response.json()["message"] == "Interview not found"


def test_delete_interview_twice(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Medium"
    )

    first_delete = client.delete(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert first_delete.status_code == 200

    second_delete = client.delete(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert second_delete.status_code == 404


def test_update_deleted_interview_returns_404(client, auth_headers):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    interviews = list_response.json()["data"]["interviews"]
    interview_id = next(
        item["id"] for item in reversed(interviews)
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Medium"
    )

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200

    update_response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"role": "Senior Python Developer"},
        headers=auth_headers,
    )

    assert update_response.status_code == 404
    assert update_response.json()["status"] is False
    assert update_response.json()["message"] == "Interview not found"


def test_interview_count_decreases_after_soft_delete(client, auth_headers):
    for role in ["Python Developer", "AI Engineer"]:
        response = client.post(
            "/api/v1/interviews",
            json={
                "role": role,
                "difficulty": "Medium",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

    before_delete = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    before_data = before_delete.json()["data"]
    initial_count = before_data["total"]

    interview_id = next(
        item["id"] for item in before_data["interviews"]
        if item["role"] == "Python Developer"
        and item["difficulty"] == "Medium"
    )

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 200

    after_delete = client.get(
        "/api/v1/interviews",
        headers=auth_headers,
    )
    final_data = after_delete.json()["data"]

    assert final_data["total"] == initial_count - 1


def test_get_interview_session_results_not_found(client, auth_headers):
    response = client.get(
        "/api/v1/sessions/999999/results",
        headers=auth_headers,
    )

    assert response.status_code == 404

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 404
    assert result["message"] == "Interview session not found."
