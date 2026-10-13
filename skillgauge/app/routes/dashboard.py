from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard/summary")
def summary(db: Session = Depends(get_db)):
    return {"total_assessments": 0, "average_score": 0.0, "strongest_skill": "N/A", "needs_improvement": "N/A"}
