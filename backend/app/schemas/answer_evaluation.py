from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class AnswerEvaluationRequest(BaseModel):
    question: str = Field(min_length=1)
    expected_answer_points: list[str] = Field(min_length=1)
    user_answer: str = Field(min_length=1)


class AnswerEvaluationResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    strengths: list[str]
    areas_to_improve: list[str]
    suggested_answer: str
    feedback: str

class AnswerEvaluationHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    generated_question_id: int | None
    question: str
    expected_answer_points: list[str]
    user_answer: str
    score: int
    strengths: list[str]
    areas_to_improve: list[str]
    suggested_answer: str
    feedback: str
    created_at: datetime
