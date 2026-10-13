from __future__ import annotations

import random
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models.question import Question
from app.repositories.question_repository import QuestionRepository


class QuestionService:
    def __init__(self, db: Session):
        self.repo = QuestionRepository(db)

    def get_skills(self):
        return self.repo.list_skills()

    def get_skill(self, skill_id: int):
        return self.repo.get_skill_by_id(skill_id)

    def get_questions(
        self,
        skill_ids: Iterable[int] | None = None,
        difficulties: Iterable[str] | None = None,
        topic: str | None = None,
    ) -> list[Question]:
        return self.repo.filter_questions(skill_ids=skill_ids, difficulties=difficulties, topic=topic)

    def get_question_count_for_skill(self, skill_id: int) -> dict[str, int]:
        return self.repo.get_question_count_by_skill(skill_id)

    def select_questions(
        self,
        skill_ids: list[int],
        question_count: int,
        difficulties: Iterable[str] | None = None,
        rng: random.Random | None = None,
    ) -> list[Question]:
        if not skill_ids:
            raise ValueError("At least one skill must be selected.")

        allowed_difficulties = [d.title() for d in (difficulties or []) if d]
        query = self.repo.filter_questions(skill_ids=skill_ids, difficulties=allowed_difficulties or None)
        if question_count < 1:
            raise ValueError("Question count must be at least 1.")
        if len(query) < question_count:
            raise ValueError(
                f"Only {len(query)} eligible questions are available for the selected criteria; "
                f"requested {question_count}."
            )

        candidate_ids = [question.id for question in query]
        rng = rng or random.Random()
        chosen_ids = rng.sample(candidate_ids, question_count)
        chosen = [question for question in query if question.id in chosen_ids]
        chosen.sort(key=lambda q: chosen_ids.index(q.id))
        return chosen
