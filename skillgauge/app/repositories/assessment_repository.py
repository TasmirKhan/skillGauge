from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.attempt_question import AttemptQuestion
from app.models.question import Question


class AssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_assessment_by_id(self, assessment_id: int) -> Assessment | None:
        return self.db.get(Assessment, assessment_id)

    def create_assessment(self, candidate_name: str, target_role: str, total_questions: int) -> Assessment:
        assessment = Assessment(
            candidate_name=candidate_name,
            target_role=target_role,
            total_questions=total_questions,
            status="in_progress",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def add_attempt_questions(self, assessment: Assessment, question_order: list[Question]) -> list[AttemptQuestion]:
        assigned: list[AttemptQuestion] = []
        for index, question in enumerate(question_order, start=1):
            attempt_question = AttemptQuestion(
                attempt_id=assessment.id,
                question_id=question.id,
                question_order=index,
            )
            self.db.add(attempt_question)
            assigned.append(attempt_question)
        self.db.commit()
        for item in assigned:
            self.db.refresh(item)
        return assigned

    def list_candidate_history(self, candidate_name: str) -> list[Assessment]:
        return (
            self.db.query(Assessment)
            .filter(Assessment.candidate_name == candidate_name)
            .order_by(Assessment.started_at.desc())
            .all()
        )
