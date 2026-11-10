from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.ai.embedding_service import EmbeddingService

SIMILARITY_THRESHOLD = 0.35

class DocumentRetrievalService:

    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    def retrieve_relevant_chunks(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = 5,
    ) -> list[tuple[DocumentChunk, float]]:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            raise ValueError("top_k must be greater than zero")
        
        query_embedding = self.embedding_service.generate_embedding(
            query.strip()
        )

        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        ).label("cosine_distance")

        results = (
            db.query(DocumentChunk, distance)
            .join(Document)
            .filter(Document.status == "processed")
            .filter(Document.user_id == user_id)
            .filter(distance <= SIMILARITY_THRESHOLD)
            .order_by(distance)
            .limit(top_k)
            .all()
        )

        relevant_results = [
            (chunk, float(cosine_distance))
            for chunk, cosine_distance in results
            if cosine_distance <= SIMILARITY_THRESHOLD
        ]

        return relevant_results

