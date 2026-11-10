import sys
from pathlib import Path

from app.db.database import SessionLocal
from app.models.document import Document
from app.services.document.document_ingestion_service import (
    DocumentIngestionService,
)


def ingest_document(file_path: str, user_id: int = 1):
    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"File not found: {pdf_path}")

    if pdf_path.suffix.lower() not in {".pdf", ".docx"}:
        raise ValueError("Only PDF and DOCX files are supported")

    db = SessionLocal()

    try:
        document = Document(
            user_id=user_id,
            filename=pdf_path.name,
            file_path=str(pdf_path.resolve()),
            content_type=(
                "application/pdf"
                if pdf_path.suffix.lower() == ".pdf"
                else "application/vnd.openxmlformats-officedocument."
                     "wordprocessingml.document"
            ),
            file_size=pdf_path.stat().st_size,
            status="uploaded",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        print(f"Document created. ID: {document.id}")

        ingestion_service = DocumentIngestionService()

        result = ingestion_service.ingest_document(
            db=db,
            document=document,
        )

        db.refresh(result)

        print(f"Document status: {result.status}")
        print(f"Document ID: {result.id}")
        print(f"Total chunks stored: {len(result.chunks)}")

        for chunk in result.chunks[:3]:
            print(f"\nChunk index: {chunk.chunk_index}")
            print(f"Content length: {len(chunk.content)}")
            print(f"Embedding dimensions: {len(chunk.embedding)}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            'Usage: python ingest_document.py "path/to/document.pdf"'
        )
        sys.exit(1)

    ingest_document(sys.argv[1])