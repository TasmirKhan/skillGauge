from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import SessionLocal, init_db
from app.routes.assessments import router as assessments_router
from app.routes.questions import router as questions_router
from app.routes.skills import router as skills_router
from data.seed_questions import seed_question_bank

app = FastAPI(title="SkillGauge", version="1.0.0")

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
app.include_router(skills_router)
app.include_router(questions_router)
app.include_router(assessments_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.on_event("startup")
def initialize_application() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_question_bank(db)
    finally:
        db.close()


@app.get("/")
def serve_frontend() -> FileResponse:
    return FileResponse(frontend_dir / "index.html")
