from pydantic import BaseModel, Field


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