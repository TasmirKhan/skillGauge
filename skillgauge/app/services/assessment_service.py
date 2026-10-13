from __future__ import annotations

import random
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.attempt_question import AttemptQuestion
from app.models.question import Question
from app.models.skill import Skill
from app.repositories.assessment_repository import AssessmentRepository
from app.services.question_service import QuestionService
from app.services.scoring_service import ScoringService


class AssessmentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.question_service = QuestionService(db)
        self.scoring_service = ScoringService()

    def validate_selected_skills(self, skill_ids: list[int]) -> list[Skill]:
        skills = []
        for skill_id in skill_ids:
            skill = self.question_service.get_skill(skill_id)
            if skill is None:
                raise ValueError(f"Invalid skill id: {skill_id}")
            skills.append(skill)
        return skills

    def create_assessment(
        self,
        candidate_name: str,
        target_role: str,
        skill_ids: list[int],
        question_count: int,
        difficulties: list[str] | None = None,
        rng: random.Random | None = None,
    ) -> Assessment:
        skills = self.validate_selected_skills(skill_ids)
        selected_question_ids = [skill.id for skill in skills]
        if not selected_question_ids:
            raise ValueError("You must choose at least one skill.")

        chosen_questions = self.question_service.select_questions(
            skill_ids=skill_ids,
            question_count=question_count,
            difficulties=difficulties,
            rng=rng,
        )
        assessment = self.repo.create_assessment(candidate_name, target_role, len(chosen_questions))
        for index, question in enumerate(chosen_questions, start=1):
            attempt_question = AttemptQuestion(
                attempt_id=assessment.id,
                question_id=question.id,
                question_order=index,
            )
            self.db.add(attempt_question)
        self.db.commit()
        self.db.refresh(assessment)
        return assessment

    def get_assessment(self, assessment_id: int) -> Assessment | None:
        return self.repo.get_assessment_by_id(assessment_id)

    def get_assessment_detail(self, assessment_id: int) -> dict:
        assessment = self.get_assessment(assessment_id)
        if assessment is None:
            raise ValueError(f"Assessment {assessment_id} not found.")
        questions = []
        for attempt_question in sorted(assessment.attempt_questions, key=lambda item: item.question_order):
            question = attempt_question.question
            questions.append(
                {
                    "id": question.id,
                    "skill_id": question.skill_id,
                    "question_text": question.question_text,
                    "options": question.options_json,
                    "difficulty": question.difficulty,
                    "topic": question.topic,
                }
            )
        return {
            "id": assessment.id,
            "candidate_name": assessment.candidate_name,
            "target_role": assessment.target_role,
            "status": assessment.status,
            "total_questions": assessment.total_questions,
            "correct_answers": assessment.correct_answers,
            "total_score": assessment.total_score,
            "readiness_score": assessment.readiness_score,
            "started_at": assessment.started_at,
            "completed_at": assessment.completed_at,
            "questions": questions,
        }

    def submit_assessment(self, assessment_id: int, answers: list[dict]) -> dict:
        assessment = self.get_assessment(assessment_id)
        if assessment is None:
            raise ValueError(f"Assessment {assessment_id} not found.")
        if assessment.status == "completed":
            raise ValueError("This assessment has already been submitted.")

        assigned_question_ids = {attempt.question_id for attempt in assessment.attempt_questions}
        answer_questions = [answer["question_id"] for answer in answers]
        unknown_ids = set(answer_questions) - assigned_question_ids
        if unknown_ids:
            raise ValueError(f"Unknown question ids: {sorted(unknown_ids)}")

        seen_ids: set[int] = set()
        for answer in answers:
            question_id = int(answer["question_id"])
            if question_id in seen_ids:
                raise ValueError(f"Duplicate answer for question {question_id}.")
            seen_ids.add(question_id)

        score_result = self.scoring_service.score_submission(assessment, answers)
        for attempt_question in assessment.attempt_questions:
            question = attempt_question.question
            selected_option = next(
                (answer["selected_option"] for answer in answers if int(answer["question_id"]) == question.id),
                None,
            )
            if selected_option is not None and selected_option not in question.options_json:
                raise ValueError(f"Invalid option for question {question.id}.")

            user_answer = attempt_question.user_answer
            if user_answer is None:
                user_answer = attempt_question.user_answer = self.db.query(type(attempt_question.user_answer)).first() if False else None

        self.db.flush()
        assessment.correct_answers = score_result["correct_answers"]
        assessment.total_score = float(score_result["overall_score"])
        assessment.readiness_score = float(score_result["overall_score"])
        assessment.completed_at = datetime.now(timezone.utc)
        assessment.status = "completed"
        self.db.commit()
        self.db.refresh(assessment)
        return {
            "id": assessment.id,
            "candidate_name": assessment.candidate_name,
            "target_role": assessment.target_role,
            "status": assessment.status,
            "total_questions": assessment.total_questions,
            "correct_answers": assessment.correct_answers,
            "incorrect_answers": score_result["incorrect_answers"],
            "unanswered": score_result["unanswered"],
            "overall_score": score_result["overall_score"],
            "readiness_score": score_result["readiness_score"],
            "skill_scores": score_result["skill_scores"],
            "detailed_results": score_result["detailed_results"],
        }

    def list_history_for_candidate(self, candidate_name: str):
        return self.repo.list_candidate_history(candidate_name)
