from fastapi import APIRouter
from app.api.v1.endpoints import(
health,
interviews,
ai_questions,
answer_evaluation,
auth,
documents
)  

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"],)
api_router.include_router(auth.router)
api_router.include_router(interviews.router, tags=["Interviews"],)
api_router.include_router(ai_questions.router, tags=["AI Questions"],)
api_router.include_router(answer_evaluation.router, tags=["Answer Evaluation"],)
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])