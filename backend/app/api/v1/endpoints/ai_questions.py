import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import GeneratedQuestion, QuestionGeneration
from app.schemas.ai_questions import(
QuestionGenerationRequest,
QuestionGenerationHistoryResponse,
QuestionGenerationRequest,
) 
from app.services.ai.question_history_service import QuestionHistoryService
from app.services.ai.ai_question_service import AIQuestionService
from app.utils.response import global_response_format

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/ai-questions/generate",
    status_code=status.HTTP_200_OK,
)
def generate_questions(
    request: QuestionGenerationRequest,
    db: Session = Depends(get_db),
):
    try:
        service = AIQuestionService()
        result = service.generate_questions(request)

        generation = QuestionGeneration(
            role=request.role,
            experience_years=request.experience_years,
            skills=request.skills,
            difficulty=request.difficulty,
        )

        generation.questions = [
            GeneratedQuestion(
                question=question.question,
                expected_answer_points=question.expected_answer_points,
            )
            for question in result.questions
        ]

        db.add(generation)
        db.commit()
        db.refresh(generation)

        return global_response_format(
            status_value=True,
            data=result.model_dump(mode="json"),
            status_code=status.HTTP_200_OK,
            status_message="AI interview questions generated successfully",
        )

    except ValueError as exc:
        db.rollback()
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            status_message=str(exc),
        )

    except Exception:
        db.rollback()
        logger.exception("AI question generation failed")

        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_502_BAD_GATEWAY,
            status_message="AI question generation failed",
        )


@router.get(
    "/ai-questions/history/{generation_id}",
    status_code=status.HTTP_200_OK,
)
def get_question_generation_history(
    generation_id: int,
    db: Session = Depends(get_db),
):
    service = QuestionHistoryService(db)
    generation = service.get_generation_history(generation_id)

    if generation is None:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message="Question generation history not found",
        )

    data = {
        "id": generation.id,
        "role": generation.role,
        "experience_years": generation.experience_years,
        "skills": generation.skills,
        "difficulty": generation.difficulty,
        "created_at": generation.created_at.isoformat()
        if generation.created_at
        else None,
        "questions": [
            {
                "id": question.id,
                "question": question.question,
                "expected_answer_points": question.expected_answer_points,
            }
            for question in generation.questions
        ],
    }

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Question generation history retrieved successfully",
    )
