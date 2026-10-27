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


def test_create_interview(client):
    response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "medium",
        },
    )

    assert response.status_code == 201

    result = response.json()

    assert result["status"] is True
    assert result["data"] == {}
    assert result["status_code"] == 201
    assert result["message"] == "Interview created successfully"


def test_create_interview_invalid_role(client):
    response = client.post(
        "/api/v1/interviews",
        json={
            "role": "A",
            "difficulty": "medium",
        },
    )

    assert response.status_code == 422


def test_list_interviews_pagination(client):
    response = client.get(
        "/api/v1/interviews?skip=0&limit=5"
    )

    assert response.status_code == 200

    result = response.json()

    assert result["status"] is True
    assert result["status_code"] == 200
    assert result["message"] == "Interviews retrieved successfully"
    assert isinstance(result["data"], list)
    assert len(result["data"]) <= 5


def test_list_interviews_invalid_pagination(client):
    response = client.get(
        "/api/v1/interviews?skip=-1&limit=101"
    )

    assert response.status_code == 422


def test_list_interviews_pagination(client):
    response = client.get("/api/v1/interviews?skip=0&limit=5")

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


def test_list_interviews_total_count(client):
    response = client.get("/api/v1/interviews")

    assert response.status_code == 200

    data = response.json()["data"]

    assert data["total"] == len(data["interviews"])


def test_get_interview_not_found(client):
    response = client.get("/api/v1/interviews/9999")

    assert response.status_code == 404

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 404
    assert result["message"] == "Interview not found"


def test_get_interview_by_id(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
    )

    assert create_response.status_code == 201

    list_response = client.get(
        "/api/v1/interviews?skip=0&limit=1"
    )
    assert list_response.status_code == 200

    interviews = list_response.json()["data"]["interviews"]
    assert len(interviews) == 1

    interview_id = interviews[0]["id"]

    response = client.get(
        f"/api/v1/interviews/{interview_id}"
    )

    assert response.status_code == 200

    result = response.json()
    assert result["status"] is True
    assert result["data"]["id"] == interview_id
    assert result["data"]["role"] == "Python Developer"
    assert result["data"]["difficulty"] == "Beginner"
    assert result["message"] == "Interview retrieved successfully"


def test_update_interview(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews?skip=0&limit=1")
    interview_id = list_response.json()["data"]["interviews"][0]["id"]

    update_response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"difficulty": "Advanced"},
    )

    assert update_response.status_code == 200

    result = update_response.json()
    assert result["status"] is True
    assert result["data"]["id"] == interview_id
    assert result["data"]["role"] == "Python Developer"
    assert result["data"]["difficulty"] == "Advanced"
    assert result["message"] == "Interview updated successfully"


def test_update_interview_not_found(client):
    response = client.put(
        "/api/v1/interviews/9999",
        json={"difficulty": "Advanced"},
    )

    assert response.status_code == 404

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 404
    assert result["message"] == "Interview not found"


def test_update_interview_null_field(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews?skip=0&limit=1")
    interview_id = list_response.json()["data"]["interviews"][0]["id"]

    response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"difficulty": None},
    )

    assert response.status_code == 422

    result = response.json()
    assert result["status"] is False
    assert result["status_code"] == 422
    assert result["message"] == "Fields cannot be null"


def test_update_interview_empty_body(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Beginner",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews?skip=0&limit=1")
    interview_id = list_response.json()["data"]["interviews"][0]["id"]

    response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={},
    )

    assert response.status_code == 400

    result = response.json()
    assert result["status"] is False
    assert result["data"] == {}
    assert result["status_code"] == 400
    assert result["message"] == "At least one field must be provided"


def test_delete_interview_soft_delete(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews")
    interviews = list_response.json()["data"]["interviews"]
    interview_id = interviews[0]["id"]

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["status"] is True
    assert delete_response.json()["data"] == {}

    detail_response = client.get(
        f"/api/v1/interviews/{interview_id}"
    )
    assert detail_response.status_code == 404

    list_after_delete = client.get("/api/v1/interviews")
    remaining_ids = [
        item["id"]
        for item in list_after_delete.json()["data"]["interviews"]
    ]
    assert interview_id not in remaining_ids


def test_delete_interview_not_found(client):
    response = client.delete("/api/v1/interviews/999999")

    assert response.status_code == 404
    assert response.json()["status"] is False
    assert response.json()["message"] == "Interview not found"


def test_delete_interview_twice(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews")
    interview_id = list_response.json()["data"]["interviews"][0]["id"]

    first_delete = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )
    assert first_delete.status_code == 200

    second_delete = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )
    assert second_delete.status_code == 404


def test_update_deleted_interview_returns_404(client):
    create_response = client.post(
        "/api/v1/interviews",
        json={
            "role": "Python Developer",
            "difficulty": "Medium",
        },
    )
    assert create_response.status_code == 201

    list_response = client.get("/api/v1/interviews")
    interviews = list_response.json()["data"]["interviews"]
    interview_id = interviews[0]["id"]

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )
    assert delete_response.status_code == 200

    update_response = client.put(
        f"/api/v1/interviews/{interview_id}",
        json={"role": "Senior Python Developer"},
    )

    assert update_response.status_code == 404
    assert update_response.json()["status"] is False
    assert update_response.json()["message"] == "Interview not found"



def test_interview_count_decreases_after_soft_delete(client):
    for role in ["Python Developer", "AI Engineer"]:
        response = client.post(
            "/api/v1/interviews",
            json={
                "role": role,
                "difficulty": "Medium",
            },
        )
        assert response.status_code == 201

    before_delete = client.get("/api/v1/interviews")
    before_data = before_delete.json()["data"]
    initial_count = before_data["total"]
    interview_id = before_data["interviews"][0]["id"]

    delete_response = client.delete(
        f"/api/v1/interviews/{interview_id}"
    )
    assert delete_response.status_code == 200

    after_delete = client.get("/api/v1/interviews")
    final_data = after_delete.json()["data"]

    assert final_data["total"] == initial_count - 1
