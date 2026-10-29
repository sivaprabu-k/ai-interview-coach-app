from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        existing_user = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_user:
            raise ValueError("Email is already registered")

        user = User(
            name=user_data.name,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def login_user(db: Session, login_data: LoginRequest) -> User:
        user = (
            db.query(User)
            .filter(User.email == str(login_data.email))
            .first()
        )

        if not user or not verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is inactive")

        return user
