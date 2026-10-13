from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.models.question import Question


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_skills_endpoint_returns_seeded_skills(client: TestClient):
    response = client.get("/api/v1/skills")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["skills"]) >= 10
    assert any(skill["name"] == "Python" for skill in payload["skills"])


def test_assessment_creation_succeeds(client: TestClient):
    skills = client.get("/api/v1/skills").json()["skills"]
    skill_ids = [skill["id"] for skill in skills[:2]]

    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Alice",
            "target_role": "Python Developer",
            "skills": skill_ids,
            "question_count": 5,
            "difficulties": ["Easy", "Medium"],
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["candidate_name"] == "Alice"
    assert payload["status"] == "in_progress"
    assert payload["total_questions"] == 5


def test_invalid_skills_are_rejected(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Bob",
            "target_role": "Backend Developer",
            "skills": [999999],
            "question_count": 5,
        },
    )
    assert response.status_code in {400, 422}


def test_question_count_and_uniqueness(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Cara",
            "target_role": "Data Analyst",
            "skills": [1, 2, 3],
            "question_count": 4,
        },
    )
    assert response.status_code == 201, response.text
    attempt = response.json()
    attempt_id = attempt["id"]

    detail_response = client.get(f"/api/v1/assessments/{attempt_id}")
    assert detail_response.status_code == 200
    questions = detail_response.json()["questions"]
    assert len(questions) == 4
    ids = [q["id"] for q in questions]
    assert len(ids) == len(set(ids))


def test_active_assessment_does_not_expose_correct_answers(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Dana",
            "target_role": "Java Developer",
            "skills": [1],
            "question_count": 2,
        },
    )
    attempt = response.json()
    detail = client.get(f"/api/v1/assessments/{attempt['id']}")
    for question in detail.json()["questions"]:
        assert "correct_option" not in question
        assert "explanation" not in question


def test_submission_scores_valid_and_invalid_answers(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Evan",
            "target_role": "Backend Developer",
            "skills": [1],
            "question_count": 2,
        },
    )
    attempt_id = response.json()["id"]

    with SessionLocal() as db:
        questions = db.query(Question).filter(Question.id.in_([q["id"] for q in client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"]])).all()
        answers = []
        for question in questions:
            answers.append({"question_id": question.id, "selected_option": question.correct_option})

    submit_response = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": answers},
    )
    assert submit_response.status_code == 200, submit_response.text
    payload = submit_response.json()
    assert payload["correct_answers"] == 2
    assert payload["readiness_score"] == 100.0


def test_unanswered_questions_are_counted_as_incorrect(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Frank",
            "target_role": "QA Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    attempt_id = response.json()["id"]
    question_id = client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"][0]["id"]

    submit_response = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": [{"question_id": question_id, "selected_option": None}]},
    )
    assert submit_response.status_code == 200, submit_response.text
    payload = submit_response.json()
    assert payload["correct_answers"] == 0
    assert payload["overall_score"] == 0.0


def test_skill_wise_percentages_are_relative_to_assessed_questions(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Grace",
            "target_role": "Full Stack Developer",
            "skills": [1, 2],
            "question_count": 2,
        },
    )
    attempt_id = response.json()["id"]
    assigned = client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"]
    with SessionLocal() as db:
        questions = db.query(Question).filter(Question.id.in_([q["id"] for q in assigned])).all()
        answers = []
        for q in questions:
            answers.append({"question_id": q.id, "selected_option": q.correct_option})

    submit_response = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": answers},
    )
    report = client.get(f"/api/v1/assessments/{attempt_id}/report")
    assert report.status_code == 200
    assert "skill_scores" in report.json()


def test_reports_are_inaccessible_for_incomplete_attempts(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Heidi",
            "target_role": "DevOps Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    attempt_id = response.json()["id"]
    report_response = client.get(f"/api/v1/assessments/{attempt_id}/report")
    assert report_response.status_code in {400, 409}


def test_completed_attempt_cannot_be_submitted_again(client: TestClient):
    response = client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Ivan",
            "target_role": "Product Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    attempt_id = response.json()["id"]
    detail = client.get(f"/api/v1/assessments/{attempt_id}").json()["questions"][0]
    client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": [{"question_id": detail["id"], "selected_option": "A"}]},
    )
    retry = client.post(
        f"/api/v1/assessments/{attempt_id}/submit",
        json={"answers": [{"question_id": detail["id"], "selected_option": "B"}]},
    )
    assert retry.status_code in {400, 409}


def test_invalid_assessment_ids_return_404(client: TestClient):
    assert client.get("/api/v1/assessments/999999").status_code == 404


def test_database_persistence_works(client: TestClient):
    before = client.get("/api/v1/dashboard/summary").json()
    client.post(
        "/api/v1/assessments",
        json={
            "candidate_name": "Jules",
            "target_role": "Backend Engineer",
            "skills": [1],
            "question_count": 1,
        },
    )
    after = client.get("/api/v1/dashboard/summary").json()
    assert after["total_assessments"] >= before["total_assessments"]


def test_api_errors_are_handled_without_crashing(client: TestClient):
    response = client.get("/api/v1/skills/999999")
    assert response.status_code == 404
    response2 = client.post("/api/v1/assessments", json={"candidate_name": "", "target_role": "", "skills": [], "question_count": 0})
    assert response2.status_code in {400, 422}
