from sqlalchemy import ForeignKey, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    generation_id: Mapped[int] = mapped_column(
        ForeignKey("question_generations.id", ondelete="CASCADE"),
        nullable=False,
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

    generation = relationship(
        "QuestionGeneration",
        back_populates="questions",
    )
