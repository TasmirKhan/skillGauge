from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.question_repository import QuestionRepository
from app.schemas.assessment import AssessmentCreate, SubmitAssessment
from app.services.assessment_service import AssessmentService
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/v1", tags=["assessments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/assessments", status_code=status.HTTP_201_CREATED)
def create_assessment(payload: AssessmentCreate, db: Session = Depends(get_db)):
    try:
        service = AssessmentService(db)
        assessment = service.create_assessment(
            candidate_name=payload.candidate_name,
            target_role=payload.target_role,
            skill_ids=payload.skills,
            question_count=payload.question_count,
            difficulties=payload.difficulties,
        )
        return {
            "id": assessment.id,
            "candidate_name": assessment.candidate_name,
            "target_role": assessment.target_role,
            "status": assessment.status,
            "total_questions": assessment.total_questions,
            "started_at": assessment.started_at,
            "completed_at": assessment.completed_at,
        }
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.get("/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    service = AssessmentService(db)
    assessment = service.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return service.get_assessment_detail(assessment_id)


@router.post("/assessments/{assessment_id}/submit")
def submit_assessment(assessment_id: int, payload: SubmitAssessment, db: Session = Depends(get_db)):
    service = AssessmentService(db)
    try:
        result = service.submit_assessment(assessment_id, [answer.model_dump() for answer in payload.answers])
        return result
    except ValueError as error:
        detail = str(error)
        status_code = status.HTTP_409_CONFLICT if "already" in detail.lower() or "duplicate" in detail.lower() else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=status_code, detail=detail) from error


@router.get("/assessments/{assessment_id}/report")
def get_assessment_report(assessment_id: int, db: Session = Depends(get_db)):
    service = AssessmentService(db)
    assessment = service.get_assessment(assessment_id)
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    if assessment.status != "completed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This assessment has not been submitted yet.")
    report = ReportService().build_report(assessment)
    return report


@router.get("/candidates/{candidate_id}/history")
def get_candidate_history(candidate_id: str, db: Session = Depends(get_db)):
    service = AssessmentService(db)
    results = service.list_history_for_candidate(candidate_id)
    return {
        "candidate_id": candidate_id,
        "history": [
            {
                "id": item.id,
                "candidate_name": item.candidate_name,
                "target_role": item.target_role,
                "started_at": item.started_at,
                "completed_at": item.completed_at,
                "status": item.status,
                "total_questions": item.total_questions,
                "correct_answers": item.correct_answers,
                "readiness_score": item.readiness_score,
            }
            for item in results
        ],
    }


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    from app.models.assessment import Assessment
    from app.models.question import Question
    import numpy as np
    import pandas as pd

    assessments = db.query(Assessment).filter(Assessment.status == "completed").all()
    if not assessments:
        return {
            "total_assessments": 0,
            "average_score": 0.0,
            "strongest_skill": "Not enough data",
            "needs_improvement": "Not enough data",
            "recent_history": [],
            "skill_summary": [],
        }

    scores = [float(item.readiness_score) for item in assessments]
    average_score = float(np.mean(scores))

    question_rows = []
    for assessment in assessments:
        for attempt_question in assessment.attempt_questions:
            question = attempt_question.question
            user_answer = attempt_question.user_answer
            selected_option = user_answer.selected_option if user_answer else None
            is_correct = bool(user_answer and user_answer.is_correct)
            question_rows.append({
                "skill": question.skill.name,
                "correct": is_correct,
                "question_id": question.id,
            })

    skill_frame = pd.DataFrame(question_rows)
    if not skill_frame.empty:
        skill_summary = (
            skill_frame.groupby("skill")
            .agg(correct=("correct", "sum"), total=("question_id", "count"))
            .assign(score=lambda frame: (frame["correct"] / frame["total"]) * 100)
            .sort_values("score")
        )
        strongest_skill = skill_summary.sort_values("score", ascending=False).index[0]
        weakest_skill = skill_summary.index[0]
        skill_summary_payload = [
            {
                "skill": skill,
                "score": round(float(row["score"]), 2),
                "correct": int(row["correct"]),
                "total": int(row["total"]),
            }
            for skill, row in skill_summary.to_dict(orient="index").items()
        ]
    else:
        strongest_skill = "Not enough data"
        weakest_skill = "Not enough data"
        skill_summary_payload = []

    recent_history = [
        {
            "id": item.id,
            "candidate_name": item.candidate_name,
            "target_role": item.target_role,
            "readiness_score": item.readiness_score,
            "started_at": item.started_at,
        }
        for item in sorted(assessments, key=lambda item: item.started_at, reverse=True)[:5]
    ]

    return {
        "total_assessments": len(assessments),
        "average_score": round(average_score, 2),
        "strongest_skill": strongest_skill,
        "needs_improvement": weakest_skill,
        "recent_history": recent_history,
        "skill_summary": skill_summary_payload,
    }
