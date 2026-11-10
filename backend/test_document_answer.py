
from app.db.database import SessionLocal
from app.services.document.document_answer_service import (
    DocumentAnswerService,
)


def test_document_answer():
    db = SessionLocal()

    try:
        answer_service = DocumentAnswerService()

        query = "What technologies are used to build the blog application?"

        answer = answer_service.generate_answer(
            db=db,
            query=query,
            user_id=1,
            top_k=3,
        )

        print("\nQuestion:", query)
        print("\nGenerated Answer:", answer)

    finally:
        db.close()


if __name__ == "__main__":
    test_document_answer()
