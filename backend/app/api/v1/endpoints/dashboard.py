
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService
from app.utils.response import global_response_format

router = APIRouter()


@router.get("/dashboard/summary")
def get_dashboard_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = DashboardService.get_dashboard_summary(
        db=db,
        user_id=current_user.id,
    )

    data = DashboardSummaryResponse.model_validate(result).model_dump(
        mode="json"
    )

    return global_response_format(
        status_value=True,
        data=data,
        status_code=status.HTTP_200_OK,
        status_message="Dashboard summary retrieved successfully",
    )
