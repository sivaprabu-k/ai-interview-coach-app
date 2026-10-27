
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.interview import(
InterviewCreate,
InterviewResponse,
InterviewUpdate,
)
from app.services.interview_service import(
create_interview,
get_interviews,
get_interview_count,
get_interview_by_id,
update_interview,
delete_interview
)
from app.schemas.interview_session import (
    AnswerAttemptResponse,
    AnswerEvaluationResponse,
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    InterviewSessionStartResponse,
    InterviewSessionDetailResponse
)
from app.services.interview_session_service import InterviewSessionService
from app.utils.response import global_response_format
from fastapi import HTTPException

router = APIRouter()


@router.post(
    "/interviews",
    status_code=status.HTTP_201_CREATED,
)
def create_interview_endpoint(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
):
    interview = create_interview(db, interview_data)

    interview_data_response = InterviewResponse.model_validate(interview)

    return global_response_format(
        status_value=True,
        data={},
        status_code=status.HTTP_201_CREATED,
        status_message="Interview created successfully",
    )


@router.get("/interviews")
def list_interviews(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    interviews = get_interviews(
        db=db,
        skip=skip,
        limit=limit,
    )

    data = {
        "interviews": [
            InterviewResponse.model_validate(interview).model_dump(mode="json")
            for interview in interviews
        ],
        "total": get_interview_count(db),
        "skip": skip,
        "limit": limit,
    }

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Interviews retrieved successfully",
    )


@router.get("/interviews/{interview_id}")
def retrieve_interview(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = get_interview_by_id(
        db=db,
        interview_id=interview_id,
    )

    if interview is None:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message="Interview not found",
        )

    data = InterviewResponse.model_validate(interview).model_dump(
        mode="json"
    )

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Interview retrieved successfully",
    )


@router.put("/interviews/{interview_id}")
def update_interview_endpoint(
    interview_id: int,
    interview_data: InterviewUpdate,
    db: Session = Depends(get_db),
):
    interview = get_interview_by_id(
        db=db,
        interview_id=interview_id,
    )

    if interview is None:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message="Interview not found",
        )

    update_data = interview_data.model_dump(exclude_unset=True)

    if not update_data:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_400_BAD_REQUEST,
            status_message="At least one field must be provided",
        )

    if any(value is None for value in update_data.values()):
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            status_message="Fields cannot be null",
        )

    updated_interview = update_interview(
        db=db,
        interview=interview,
        interview_data=interview_data,
    )

    data = InterviewResponse.model_validate(updated_interview).model_dump(mode="json")

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Interview updated successfully",
    )


@router.delete("/interviews/{interview_id}")
def delete_interview_endpoint(
    interview_id: int,
    db: Session = Depends(get_db),
):
    interview = get_interview_by_id(db, interview_id)

    if interview is None:
        return global_response_format(
            status_value=False,
            data={},
            status_code=404,
            status_message="Interview not found",
        )

    delete_interview(db, interview)

    return global_response_format(
        status_value=True,
        data={},
        status_code=200,
        status_message="Interview deleted successfully",
    )


@router.post(
    "/interviews/{interview_id}/sessions",
    status_code=status.HTTP_201_CREATED,
)
def create_interview_session_endpoint(
    interview_id: int,
    db: Session = Depends(get_db),
):
    try:
        session = InterviewSessionService.create_session(
            interview_id=interview_id,
            db=db,
        )
    except ValueError as exc:
        message = str(exc)

        error_status = (
            status.HTTP_404_NOT_FOUND
            if message == "Interview not found."
            else status.HTTP_400_BAD_REQUEST
        )

        return global_response_format(
            status_value=False,
            data={},
            status_code=error_status,
            status_message=message,
        )

    session_data = InterviewSessionStartResponse(
        id=session.id,
        interview_id=session.interview_id,
        generation_id=session.generation_id,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        questions=[
            {
                "id": question.id,
                "question": question.question,
                "expected_answer_points": question.expected_answer_points,
            }
            for question in session.generation.questions
        ],
        total_questions=len(session.generation.questions),
    )

    return global_response_format(
        status_value=True,
        data=session_data.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
        status_message="Interview session created successfully",
    )


@router.get("/sessions/{session_id}")
def get_interview_session_details(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        session = InterviewSessionService.get_session_details(
            session_id=session_id,
            db=db,
        )
    except ValueError as exc:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message=str(exc),
        )

    questions = []
    completed_questions = 0
    unanswered_questions = 0
    failed_evaluations = 0

    attempts_by_question = {}

    for attempt in session.answer_attempts:
        attempts_by_question.setdefault(
            attempt.generated_question_id, []
        ).append(attempt)

        if attempt.evaluation_status == "failed":
            failed_evaluations += 1

    for question in session.generation.questions:
        attempts = attempts_by_question.get(question.id, [])

        successful_attempts = sum(
            1
            for attempt in attempts
            if attempt.evaluation_status == "succeeded"
        )

        if successful_attempts > 0:
            completed_questions += 1
        else:
            unanswered_questions += 1

        questions.append({
            "question_id": question.id,
            "attempts": [
                {
                    "id": attempt.id,
                    "generated_question_id": attempt.generated_question_id,
                    "attempt_number": attempt.attempt_number,
                    "user_answer": attempt.user_answer,
                    "evaluation_status": attempt.evaluation_status,
                    "submitted_at": attempt.submitted_at,
                }
                for attempt in sorted(
                    attempts,
                    key=lambda item: item.attempt_number,
                )
            ],
            "successful_attempts": successful_attempts,
            "total_attempts": len(attempts),
        })

    response_data = InterviewSessionDetailResponse(
        id=session.id,
        interview_id=session.interview_id,
        generation_id=session.generation_id,
        status=session.status,
        started_at=session.started_at,
        completed_at=session.completed_at,
        questions=questions,
        total_questions=len(session.generation.questions),
        completed_questions=completed_questions,
        unanswered_questions=unanswered_questions,
        failed_evaluations=failed_evaluations,
    )

    return global_response_format(
        status_value=True,
        data=response_data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
        status_message="Interview session details retrieved successfully",
    )


@router.get("/interviews/{interview_id}/sessions")
def get_interview_sessions_endpoint(
    interview_id: int,
    db: Session = Depends(get_db),
):
    try:
        sessions = InterviewSessionService.get_interview_sessions(
            interview_id=interview_id,
            db=db,
        )
    except ValueError as exc:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_404_NOT_FOUND,
            status_message=str(exc),
        )

    session_data = [
        {
            "id": session.id,
            "interview_id": session.interview_id,
            "generation_id": session.generation_id,
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
        }
        for session in sessions
    ]

    return global_response_format(
        status_value=True,
        data=session_data,
        status_code=status.HTTP_200_OK,
        status_message="Interview sessions retrieved successfully",
    )


@router.post(
    "/sessions/{session_id}/answers",
    status_code=status.HTTP_201_CREATED,
)
def submit_interview_answer_endpoint(
    session_id: int,
    answer_data: AnswerSubmissionRequest,
    db: Session = Depends(get_db),
):
    try:
        attempt, evaluation = InterviewSessionService.submit_answer(
            session_id=session_id,
            generated_question_id=answer_data.generated_question_id,
            user_answer=answer_data.user_answer,
            db=db,
        )
    except ValueError as exc:
        message = str(exc)

        error_status = (
            status.HTTP_404_NOT_FOUND
            if message == "Interview session not found."
            else status.HTTP_400_BAD_REQUEST
        )

        return global_response_format(
            status_value=False,
            data={},
            status_code=error_status,
            status_message=message,
        )

    evaluation_data = None

    if evaluation is not None:
        evaluation_data = AnswerEvaluationResponse(
            score=evaluation.score,
            strengths=evaluation.strengths,
            areas_to_improve=evaluation.areas_to_improve,
            suggested_answer=evaluation.suggested_answer,
            feedback=evaluation.feedback,
        )

    response_data = AnswerSubmissionResponse(
        attempt=AnswerAttemptResponse.model_validate(attempt),
        evaluation=evaluation_data,
    )

    return global_response_format(
        status_value=True,
        data=response_data.model_dump(mode="json"),
        status_code=status.HTTP_201_CREATED,
        status_message=(
            "Answer submitted and evaluated successfully"
            if evaluation is not None
            else "Answer saved, but evaluation failed. You can retry evaluation."
        ),
    )


@router.post(
    "/sessions/{session_id}/answers/{attempt_id}/retry-evaluation",
    status_code=status.HTTP_200_OK,
)
def retry_answer_evaluation_endpoint(
    session_id: int,
    attempt_id: int,
    db: Session = Depends(get_db),
):
    try:
        attempt, evaluation = InterviewSessionService.retry_evaluation(
            session_id=session_id,
            attempt_id=attempt_id,
            db=db,
        )
    except ValueError as exc:
        message = str(exc)

        error_status = (
            status.HTTP_404_NOT_FOUND
            if message in {
                "Interview session not found.",
                "Answer attempt not found in this session.",
            }
            else status.HTTP_400_BAD_REQUEST
        )

        return global_response_format(
            status_value=False,
            data={},
            status_code=error_status,
            status_message=message,
        )

    evaluation_data = None

    if evaluation is not None:
        evaluation_data = AnswerEvaluationResponse(
            score=evaluation.score,
            strengths=evaluation.strengths,
            areas_to_improve=evaluation.areas_to_improve,
            suggested_answer=evaluation.suggested_answer,
            feedback=evaluation.feedback,
        )

    response_data = AnswerSubmissionResponse(
        attempt=AnswerAttemptResponse.model_validate(attempt),
        evaluation=evaluation_data,
    )

    return global_response_format(
        status_value=True,
        data=response_data.model_dump(mode="json"),
        status_code=status.HTTP_200_OK,
        status_message=(
            "Answer evaluation retried successfully"
            if evaluation is not None
            else "Evaluation retry failed. The saved answer is preserved."
        ),
    )




@router.post(
    "/sessions/{session_id}/complete",
    status_code=status.HTTP_200_OK,
)
def complete_interview_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        session = InterviewSessionService.complete_session(
            session_id=session_id,
            db=db,
        )
    except ValueError as exc:
        message = str(exc)

        error_status = (
            status.HTTP_404_NOT_FOUND
            if message == "Interview session not found."
            else status.HTTP_400_BAD_REQUEST
        )

        return global_response_format(
            status_value=False,
            data={},
            status_code=error_status,
            status_message=message,
        )

    response_data = {
        "id": session.id,
        "interview_id": session.interview_id,
        "generation_id": session.generation_id,
        "status": session.status,
        "started_at": (
            session.started_at.isoformat()
            if session.started_at
            else None
        ),
        "completed_at": (
            session.completed_at.isoformat()
            if session.completed_at
            else None
        ),
    }


    return global_response_format(
        status_value=True,
        data=response_data,
        status_code=status.HTTP_200_OK,
        status_message="Interview session completed successfully.",
    )
