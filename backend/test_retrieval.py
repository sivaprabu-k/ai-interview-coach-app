from app.db.database import SessionLocal
from app.services.document.document_retrieval_service import (
    DocumentRetrievalService,
)


def test_document_retrieval():
    db = SessionLocal()

    try:
        retrieval_service = DocumentRetrievalService()

        query = "Explain diabetes symptoms and treatment options"

        results = retrieval_service.retrieve_relevant_chunks(
            db=db,
            query=query,
            top_k=3,
        )

        print(f"Query: {query}")
        print(f"Retrieved chunks: {len(results)}")

        for chunk, distance in results:
            print(
                f"Chunk: {chunk.chunk_index} | "
                f"Cosine Distance: {distance:.4f}"
            )
            print(f"Content: {chunk.content[:300]}")

    finally:
        db.close()


if __name__ == "__main__":
    test_document_retrieval()
