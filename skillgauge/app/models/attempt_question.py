from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AttemptQuestion(Base):
    __tablename__ = "attempt_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("assessments.id"), nullable=False, index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False, index=True)
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)
    marks_awarded: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="attempt_questions")
    question: Mapped["Question"] = relationship("Question")
    user_answer: Mapped["UserAnswer"] = relationship(
        back_populates="attempt_question",
        uselist=False,
        cascade="all, delete-orphan",
    )
