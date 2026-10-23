from sqlalchemy.orm import Session
from app.models import QuestionGeneration


class QuestionHistoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_generation_history(self, generation_id: int):
        return (
            self.db.query(QuestionGeneration)
            .filter(QuestionGeneration.id == generation_id)
            .first()
        )
