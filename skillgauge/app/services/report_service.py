from __future__ import annotations

import numpy as np
import pandas as pd

from app.models.assessment import Assessment


class ReportService:
    def build_report(self, assessment: Assessment) -> dict:
        if assessment.status != "completed":
            raise ValueError("A report is only available for completed assessments.")

        rows = []
        for attempt_question in sorted(assessment.attempt_questions, key=lambda item: item.question_order):
            question = attempt_question.question
            user_answer = attempt_question.user_answer
            selected_option = user_answer.selected_option if user_answer else None
            is_correct = bool(user_answer and user_answer.is_correct)
            rows.append(
                {
                    "question_id": question.id,
                    "skill": question.skill.name,
                    "topic": question.topic,
                    "difficulty": question.difficulty,
                    "question_text": question.question_text,
                    "selected_option": selected_option,
                    "correct_option": question.correct_option,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                    "marks_awarded": attempt_question.marks_awarded,
                }
            )

        if rows:
            df = pd.DataFrame(rows)
            skill_summary = (
                df.groupby("skill", as_index=False)
                .agg(correct=("is_correct", "sum"), total=("question_id", "count"))
                .assign(score=lambda frame: (frame["correct"] / frame["total"]) * 100)
            )
            skill_summary = skill_summary.sort_values("score").reset_index(drop=True)
            average_score = float(np.mean(skill_summary["score"])) if not skill_summary.empty else 0.0
        else:
            skill_summary = pd.DataFrame(columns=["skill", "correct", "total", "score"])
            average_score = 0.0

        skill_scores = [
            {
                "skill": row["skill"],
                "correct": int(row["correct"]),
                "total": int(row["total"]),
                "score": round(float(row["score"]), 2),
            }
            for row in skill_summary.to_dict(orient="records")
        ]

        weaknesses = sorted(skill_scores, key=lambda item: item["score"])[:3]
        strengths = sorted(skill_scores, key=lambda item: item["score"], reverse=True)[:3]
        recommendations = [
            {
                "skill": item["skill"],
                "focus": "Review the most error-prone concepts in this skill and retake a smaller set of targeted practice questions.",
            }
            for item in weaknesses
        ]

        return {
            "assessment_id": assessment.id,
            "candidate_name": assessment.candidate_name,
            "target_role": assessment.target_role,
            "overall_score": float(assessment.readiness_score or 0.0),
            "correct_answers": int(assessment.correct_answers or 0),
            "total_questions": int(assessment.total_questions or 0),
            "skill_scores": skill_scores,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "question_results": rows,
            "average_skill_score": round(average_score, 2),
        }
