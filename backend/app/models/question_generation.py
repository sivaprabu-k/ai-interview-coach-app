from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class QuestionGeneration(Base):
    __tablename__ = "question_generations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    role: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    skills: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )
    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    questions = relationship(
        "GeneratedQuestion",
        back_populates="generation",
        cascade="all, delete-orphan",
    )

    interview_id: Mapped[int | None] = mapped_column(
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    interview = relationship("Interview")
