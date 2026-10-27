from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class AnswerAttempt(Base):
    __tablename__ = "answer_attempts"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "generated_question_id",
            "attempt_number",
            name="uq_answer_attempt_session_question_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    generated_question_id: Mapped[int] = mapped_column(
        ForeignKey("generated_questions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    user_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    evaluation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session = relationship(
        "InterviewSession",
        back_populates="answer_attempts",
    )
    generated_question = relationship("GeneratedQuestion")
    evaluation = relationship(
        "AnswerEvaluation",
        back_populates="answer_attempt",
        uselist=False,
    )
