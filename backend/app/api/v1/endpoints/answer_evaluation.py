from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.answer_evaluation import (
    AnswerEvaluationHistoryItem,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
)
from app.services.ai.answer_evaluation_service import AnswerEvaluationService
from app.services.ai.answer_evaluation_history_service import  AnswerEvaluationHistoryService
from app.utils.response import global_response_format

router = APIRouter()


@router.post("/answer-evaluations")
def evaluate_answer_endpoint(
    request: AnswerEvaluationRequest,
    db: Session = Depends(get_db),
):
    try:
        service = AnswerEvaluationService()
        result = service.evaluate_answer(request, db)

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


@router.get("/answer-evaluations")
def get_answer_evaluation_history(
    db: Session = Depends(get_db),
):
    service = AnswerEvaluationHistoryService(db)
    evaluations = service.get_evaluation_history()

    data = [
        AnswerEvaluationHistoryItem.model_validate(
            evaluation
        ).model_dump(mode="json")
        for evaluation in evaluations
    ]

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Answer evaluation history retrieved successfully",
    )

