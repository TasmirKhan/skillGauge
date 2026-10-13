from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.question_repository import QuestionRepository
from app.schemas.skill import SkillRead

router = APIRouter(prefix="/api/v1", tags=["skills"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/skills", response_model=dict)
def list_skills(db: Session = Depends(get_db)):
    repository = QuestionRepository(db)
    skills = repository.list_skills()
    return {"skills": [SkillRead.model_validate(skill).model_dump() for skill in skills]}


@router.get("/skills/{skill_id}", response_model=dict)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    repository = QuestionRepository(db)
    skill = repository.get_skill_by_id(skill_id)
    if skill is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found.")
    return SkillRead.model_validate(skill).model_dump()
