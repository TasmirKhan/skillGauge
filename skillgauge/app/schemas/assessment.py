from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class QuestionAnswer(BaseModel):
    question_id: int
    selected_option: str | None = None


class AssessmentCreate(BaseModel):
    candidate_name: str = Field(..., min_length=2, max_length=200)
    target_role: str = Field(..., min_length=2, max_length=200)
    skills: list[int] = Field(..., min_length=1)
    question_count: int = Field(default=20, ge=1, le=40)
    difficulties: list[str] = Field(default_factory=lambda: ["Easy", "Medium", "Hard"])


class SubmitAssessment(BaseModel):
    answers: list[QuestionAnswer]


class AssessmentRead(BaseModel):
    id: int
    candidate_name: str
    target_role: str
    status: str
    total_questions: int
    correct_answers: int | None = None
    total_score: float | None = None
    readiness_score: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    questions: list[dict] = []

    model_config = {"from_attributes": True}
