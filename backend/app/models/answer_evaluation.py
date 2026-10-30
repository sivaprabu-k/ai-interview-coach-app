from datetime import datetime
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Text,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    __table_args__ = (
        UniqueConstraint(
            "answer_attempt_id",
            name="uq_answer_evaluation_attempt",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            name="fk_answer_evaluations_user_id_users",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )
    answer_attempt_id: Mapped[int | None] = mapped_column(
        ForeignKey("answer_attempts.id", ondelete="SET NULL"),
        nullable=True,
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

    user = relationship("User")

    generated_question = relationship("GeneratedQuestion")

    answer_attempt = relationship(
        "AnswerAttempt",
        back_populates="evaluation",
    )
