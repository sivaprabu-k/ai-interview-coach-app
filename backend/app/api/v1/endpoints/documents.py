import logging
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.document import Document
from app.models.user import User
from app.services.document.document_ingestion_service import (
    DocumentIngestionService,
)
from app.schemas.document import DocumentQuestionRequest
from pydantic import BaseModel, Field
from app.services.document.document_answer_service import (
    DocumentAnswerService,
)
from app.utils.response import global_response_format

logger = logging.getLogger(__name__)

router = APIRouter()

BACKEND_DIR = Path(__file__).resolve().parents[4]
UPLOAD_DIR = BACKEND_DIR / "uploads" / "documents"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        if not file.filename:
            return global_response_format(
                status_value=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                status_message="Filename is required",
            )

        filename = Path(file.filename).name
        extension = Path(filename).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            return global_response_format(
                status_value=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                status_message="Only PDF and DOCX files are supported",
            )

        file_content = await file.read(MAX_FILE_SIZE + 1)

        if len(file_content) > MAX_FILE_SIZE:
            return global_response_format(
                status_value=False,
                data=None,
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                status_message="File size cannot exceed 10 MB",
            )

        if not file_content:
            return global_response_format(
                status_value=False,
                data=None,
                status_code=status.HTTP_400_BAD_REQUEST,
                status_message="Uploaded file is empty",
            )

        user_upload_dir = UPLOAD_DIR / str(current_user.id)
        user_upload_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = user_upload_dir / stored_filename

        file_path.write_bytes(file_content)

        document = Document(
            user_id=current_user.id,
            filename=filename,
            file_path=str(file_path.resolve()),
            content_type=file.content_type or "application/octet-stream",
            file_size=len(file_content),
            status="uploaded",
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        ingestion_service = DocumentIngestionService()
        processed_document = ingestion_service.ingest_document(
            db=db,
            document=document,
        )

        return global_response_format(
            status_value=True,
            data={
                "document_id": processed_document.id,
                "filename": processed_document.filename,
                "file_size": processed_document.file_size,
                "status": processed_document.status,
            },
            status_code=status.HTTP_201_CREATED,
            status_message="Document uploaded and processed successfully",
        )

    except Exception as exc:
        db.rollback()
        logger.exception("Document upload failed: %s", exc)

        return global_response_format(
            status_value=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status_message="Document upload or processing failed",
        )

    finally:
        await file.close()



@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        documents = (
            db.query(Document)
            .filter(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc())
            .all()
        )

        document_data = [
            {
                "document_id": document.id,
                "filename": document.filename,
                "file_size": document.file_size,
                "content_type": document.content_type,
                "status": document.status,
                "created_at": document.created_at.isoformat(),
            }
            for document in documents
        ]

        return global_response_format(
            status_value=True,
            data=document_data,
            status_code=status.HTTP_200_OK,
            status_message="Documents retrieved successfully",
        )

    except Exception as exc:
        logger.exception("Failed to retrieve documents: %s", exc)

        return global_response_format(
            status_value=False,
            data=None,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            status_message="Failed to retrieve documents",
        )


@router.post("/ask")
def ask_document_question(
    request: DocumentQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        answer_service = DocumentAnswerService()

        answer = answer_service.generate_answer(
            db=db,
            query=request.query,
            user_id=current_user.id,
            top_k=request.top_k,
        )

        return global_response_format(
            status_value=True,
            data={
                "question": request.query,
                "answer": answer,
            },
            status_code=status.HTTP_200_OK,
            status_message="Answer generated successfully",
        )

    except ValueError as exc:
        logger.warning("Invalid document question: %s", exc)

        return global_response_format(
            status_value=False,
            data=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            status_message=str(exc),
        )

    except Exception as exc:
        logger.exception("Document question answering failed: %s", exc)

        return global_response_format(
            status_value=False,
            data=None,
            status_code=status.HTTP_502_BAD_GATEWAY,
            status_message="Failed to generate an answer",
        )
