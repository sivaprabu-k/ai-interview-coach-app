from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.database import get_db
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.utils.response import global_response_format


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        AuthService.register_user(db, user_data)

        return global_response_format(
            status_value=True,
            data={},
            status_code=status.HTTP_201_CREATED,
            status_message="User registered successfully",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except RuntimeError:
        return global_response_format(
            status_value=False,
            data={},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            status_message="User registration failed",
        )


@router.post("/login")
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        user = AuthService.login_user(db, login_data)

        access_token = create_access_token(
            subject=str(user.id)
        )

        return global_response_format(
            status_value=True,
            data={
                "access_token": access_token,
                "token_type": "bearer",
            },
            status_code=status.HTTP_200_OK,
            status_message="Login successful",
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
