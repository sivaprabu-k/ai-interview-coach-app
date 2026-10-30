from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models import User
from app.schemas.answer_evaluation import (
    AnswerEvaluationHistoryItem,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
)
from app.services.ai.answer_evaluation_service import AnswerEvaluationService
from app.services.ai.answer_evaluation_history_service import (
    AnswerEvaluationHistoryService,
)
from app.utils.response import global_response_format

router = APIRouter()


@router.post("/answer-evaluations")
def evaluate_answer_endpoint(
    request: AnswerEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        service = AnswerEvaluationService()
        result = service.evaluate_answer(request, db, user_id=current_user.id)

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
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnswerEvaluationHistoryService(db)

    evaluations = service.get_evaluation_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )

    data = [
        AnswerEvaluationHistoryItem.model_validate(evaluation).model_dump(
            mode="json"
        )
        for evaluation in evaluations
    ]

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Answer evaluation history retrieved successfully",
    )


@router.get("/answer-evaluations/{evaluation_id}")
def get_answer_evaluation_by_id(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AnswerEvaluationHistoryService(db)

    evaluation = service.get_evaluation_by_id(evaluation_id, user_id=current_user.id)

    if evaluation is None:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message="Answer evaluation not found",
        )

    data = AnswerEvaluationHistoryItem.model_validate(evaluation).model_dump(
        mode="json"
    )

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Answer evaluation retrieved successfully",
    )
