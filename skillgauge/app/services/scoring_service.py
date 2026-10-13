from __future__ import annotations

from collections import defaultdict

from app.models.answer import UserAnswer
from app.models.assessment import Assessment
from app.models.attempt_question import AttemptQuestion


class ScoringService:
    @staticmethod
    def normalize_option(question, selected_option):
        if selected_option is None:
            return None
        raw = str(selected_option).strip()
        if not raw:
            return None
        upper = raw.upper()
        valid_labels = {chr(65 + idx) for idx in range(4)}
        if upper in valid_labels:
            return upper
        for index, option_text in enumerate(question.options_json):
            option_label = chr(65 + index)
            if raw.upper() in {option_label, option_label + ".", option_label + ")"}:
                return option_label
            if raw.lower() == str(option_text).lower():
                return option_label
            if raw.lower() in str(option_text).lower().split(": ", 1)[-1].split(". ", 1)[-1]:
                return option_label
        return raw.upper()

    def score_submission(self, assessment: Assessment, answer_payload: list[dict]) -> dict:
        if not assessment.attempt_questions:
            return {
                "correct_answers": 0,
                "incorrect_answers": 0,
                "unanswered": 0,
                "overall_score": 0.0,
                "readiness_score": 0.0,
                "skill_scores": [],
                "detailed_results": [],
            }

        answer_by_question: dict[int, str | None] = {}
        for item in answer_payload:
            qid = int(item["question_id"])
            if qid in answer_by_question:
                raise ValueError(f"Duplicate answer for question {qid}.")
            answer_by_question[qid] = item.get("selected_option")

        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        detailed_results: list[dict] = []
        skill_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})

        for attempt_question in assessment.attempt_questions:
            question = attempt_question.question
            selected_option = answer_by_question.get(attempt_question.question_id)
            normalized_option = self.normalize_option(question, selected_option)
            is_correct = normalized_option is not None and normalized_option == question.correct_option.upper()
            if selected_option is None or normalized_option is None:
                unanswered_count += 1
            elif is_correct:
                correct_count += 1
            else:
                incorrect_count += 1

            skill_name = question.skill.name
            skill_totals[skill_name]["total"] += 1
            if is_correct:
                skill_totals[skill_name]["correct"] += 1

            user_answer = UserAnswer(
                attempt_question_id=attempt_question.id,
                selected_option=normalized_option,
                is_correct=is_correct,
            )
            attempt_question.user_answer = user_answer
            attempt_question.marks_awarded = 1.0 if is_correct else 0.0

            detailed_results.append(
                {
                    "question_id": question.id,
                    "skill": skill_name,
                    "question_text": question.question_text,
                    "selected_option": normalized_option,
                    "correct_option": question.correct_option,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                    "difficulty": question.difficulty,
                    "topic": question.topic,
                }
            )

        overall_score = round((correct_count / assessment.total_questions) * 100, 2) if assessment.total_questions else 0.0
        skill_scores = []
        for skill_name, stats in sorted(skill_totals.items()):
            percentage = round((stats["correct"] / stats["total"]) * 100, 2) if stats["total"] else 0.0
            skill_scores.append(
                {
                    "skill": skill_name,
                    "correct": stats["correct"],
                    "total": stats["total"],
                    "score": percentage,
                }
            )

        return {
            "correct_answers": correct_count,
            "incorrect_answers": incorrect_count,
            "unanswered": unanswered_count,
            "overall_score": overall_score,
            "readiness_score": overall_score,
            "skill_scores": skill_scores,
            "detailed_results": detailed_results,
        }
