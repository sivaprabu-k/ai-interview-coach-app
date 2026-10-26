
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.interview import(
InterviewCreate,
InterviewResponse,
InterviewUpdate,
InterviewDetailsResponse
)
from app.services.interview_service import(
create_interview,
get_interviews,
get_interview_count,
get_interview_by_id,
update_interview,
delete_interview
)
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

    data = InterviewDetailsResponse(
        **InterviewResponse.model_validate(interview).model_dump(),
        question_generations=[
            generation
            for generation in interview.question_generations
        ],
    ).model_dump(mode="json")

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
