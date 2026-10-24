from fastapi import APIRouter, HTTPException, status
from app.schemas.answer_evaluation import (
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
)
from app.services.ai.answer_evaluation_service import AnswerEvaluationService
from app.utils.response import global_response_format

router = APIRouter()


@router.post("/answer-evaluations")
def evaluate_answer_endpoint(
    request: AnswerEvaluationRequest,
):
    try:
        service = AnswerEvaluationService()
        result = service.evaluate_answer(request)

        return global_response_format(
            status_value=True,
            data=AnswerEvaluationResponse.model_validate(result).model_dump(),
            status_code=status.HTTP_200_OK,
            status_message="Answer evaluated successfully",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except RuntimeError:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            status_message="Answer evaluation service failed",
        )
