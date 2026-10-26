from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    generated_question_id: Mapped[int | None] = mapped_column(
        ForeignKey("generated_questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    expected_answer_points: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )
    user_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    strengths: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )
    areas_to_improve: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )
    suggested_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    generated_question = relationship("GeneratedQuestion")
