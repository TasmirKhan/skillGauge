from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.skill import Skill


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_skills(self) -> list[Skill]:
        return self.db.query(Skill).order_by(Skill.name).all()

    def get_skill_by_id(self, skill_id: int) -> Skill | None:
        return self.db.get(Skill, skill_id)

    def get_question_by_id(self, question_id: int) -> Question | None:
        return self.db.get(Question, question_id)

    def filter_questions(
        self,
        skill_ids: Iterable[int] | None = None,
        difficulties: Iterable[str] | None = None,
        topic: str | None = None,
    ) -> list[Question]:
        query = self.db.query(Question)
        if skill_ids:
            query = query.filter(Question.skill_id.in_(list(skill_ids)))
        if difficulties:
            normalized = [d.strip().title() for d in difficulties if d]
            if normalized:
                query = query.filter(Question.difficulty.in_(normalized))
        if topic:
            query = query.filter(Question.topic.ilike(f"%{topic}%"))
        return query.order_by(Question.id).all()

    def get_question_count_by_skill(self, skill_id: int) -> dict[str, int]:
        counts = self.db.query(Question.difficulty, Question.id).filter(Question.skill_id == skill_id).all()
        result: dict[str, int] = {"Easy": 0, "Medium": 0, "Hard": 0}
        for difficulty, _ in counts:
            result[difficulty] = result.get(difficulty, 0) + 1
        return result
