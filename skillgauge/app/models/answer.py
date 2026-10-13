from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    attempt_question_id: Mapped[int] = mapped_column(
        ForeignKey("attempt_questions.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    selected_option: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    attempt_question: Mapped["AttemptQuestion"] = relationship(back_populates="user_answer")
