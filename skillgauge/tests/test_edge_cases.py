from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.models.answer import UserAnswer
from app.models.assessment import Assessment
from app.models.attempt_question import AttemptQuestion


def reset_assessment_state():
    with SessionLocal() as db:
        db.query(UserAnswer).delete()
        db.query(AttemptQuestion).delete()
        db.query(Assessment).delete()
        db.commit()


def test_dashboard_summary_handles_no_completed_assessments(client: TestClient):
    reset_assessment_state()
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_assessments"] == 0
    assert payload["average_score"] == 0.0
    assert payload["strongest_skill"] == "Not enough data"
    assert payload["needs_improvement"] == "Not enough data"
    assert payload["skill_summary"] == []


def test_get_skill_by_unknown_id_returns_404(client: TestClient):
    response = client.get("/api/v1/skills/999999")
    assert response.status_code == 404


def test_create_assessment_rejects_invalid_question_requests(client: TestClient):
    cases = [
        {"candidate_name": "Edge", "target_role": "Engineer", "skills": [1], "question_count": 0},
        {"candidate_name": "Edge", "target_role": "Engineer", "skills": [1], "question_count": -2},
        {"candidate_name": "Edge", "target_role": "Engineer", "skills": [999999], "question_count": 1},
        {"candidate_name": "Edge", "target_role": "Engineer", "skills": [], "question_count": 1},
    ]
    for payload in cases:
        response = client.post("/api/v1/assessments", json=payload)
        assert response.status_code in {400, 422}, response.text


def test_duplicate_answers_are_rejected(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Duplicate",
            "target_role": "Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    assert response.status_code == 201, response.text
    attempt_id = response.json()["id"]
    question_id = client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"][0]["id"]

    submit_response = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={
            "answers": [
                {"question_id": question_id, "selected_option": "A"},
                {"question_id": question_id, "selected_option": "B"},
            ]
        },
    )
    assert submit_response.status_code in {400, 409, 422}


def test_invalid_answer_option_is_rejected(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "InvalidOption",
            "target_role": "Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    assert response.status_code == 201, response.text
    attempt_id = response.json()["id"]
    question_id = client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"][0]["id"]

    submit_response = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": [{"question_id": question_id, "selected_option": "Z"}]},
    )
    assert submit_response.status_code in {400, 409, 422}


def test_candidate_history_for_unknown_person_returns_empty_history(client: TestClient):
    response = client.get("/api/v1/candidates/does-not-exist/history")
    assert response.status_code == 200
    assert response.json()["history"] == []
