
from fastapi import APIRouter

from app.api.v1.endpoints import health, interviews, ai_questions

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"],)
api_router.include_router(interviews.router, tags=["Interviews"],)
api_router.include_router(ai_questions.router, tags=["AI Questions"],)
