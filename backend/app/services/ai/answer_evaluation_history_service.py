from sqlalchemy.orm import Session
from app.models.answer_evaluation import AnswerEvaluation


class AnswerEvaluationHistoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_evaluation_history(
        self,
        evaluation_id: int | None = None,
        skip: int = 0,
        limit: int = 10,
    ) -> list[AnswerEvaluation]:
        query = self.db.query(AnswerEvaluation)

        if evaluation_id is not None:
            query = query.filter(AnswerEvaluation.id == evaluation_id)

        return (
            query.order_by(
                AnswerEvaluation.created_at.desc(),
                AnswerEvaluation.id.desc(),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_evaluation_by_id(
        self,
        evaluation_id: int,
    ) -> AnswerEvaluation | None:
        return (
            self.db.query(AnswerEvaluation)
            .filter(AnswerEvaluation.id == evaluation_id)
            .first()
        )
