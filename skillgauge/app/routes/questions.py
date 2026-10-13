from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionRead

router = APIRouter(prefix="/api/v1", tags=["questions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/questions", response_model=dict)
def list_questions(
    skill: int | None = Query(default=None, alias="skill_id"),
    difficulty: str | None = None,
    topic: str | None = None,
    db: Session = Depends(get_db),
):
    repository = QuestionRepository(db)
    skill_ids = [skill] if skill is not None else None
    difficulties = [difficulty] if difficulty else None
    questions = repository.filter_questions(skill_ids=skill_ids, difficulties=difficulties, topic=topic)
    return {
        "questions": [
            QuestionRead(
                id=q.id,
                skill_id=q.skill_id,
                question_text=q.question_text,
                options=q.options_json,
                difficulty=q.difficulty,
                topic=q.topic,
            ).model_dump()
            for q in questions
        ]
    }


@router.get("/skills/{skill_id}/question-count", response_model=dict)
def get_question_counts(skill_id: int, db: Session = Depends(get_db)):
    repository = QuestionRepository(db)
    skill = repository.get_skill_by_id(skill_id)
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found.")
    return {"skill_id": skill_id, "counts": repository.get_question_count_by_skill(skill_id)}
