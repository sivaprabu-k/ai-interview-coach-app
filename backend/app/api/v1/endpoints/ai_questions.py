
from fastapi import APIRouter, status
from app.schemas.ai_questions import (
    QuestionGenerationRequest,
)
from app.services.ai.ai_question_service import AIQuestionService
from app.utils.response import global_response_format
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/ai-questions/generate",
    status_code=status.HTTP_200_OK,
)
def generate_questions(request: QuestionGenerationRequest):
    try:
        service = AIQuestionService()
        result = service.generate_questions(request)

        return global_response_format(
            status_value=True,
            data=result.model_dump(mode="json"),
            status_code=status.HTTP_200_OK,
            status_message="AI interview questions generated successfully",
        )

    except ValueError as exc:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            status_message=str(exc),
        )

    except Exception as exc:
        logger.exception("AI question generation failed")

        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_502_BAD_GATEWAY,
            status_message="AI question generation failed",
        )
