
from typing import Literal
from pydantic import BaseModel, Field


class QuestionGenerationRequest(BaseModel):
    role: str = Field(min_length=2, max_length=100)
    experience_years: int = Field(ge=0, le=50)
    skills: list[str] = Field(min_length=1, max_length=20)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    number_of_questions: int = Field(default=5, ge=1, le=10)


class InterviewQuestion(BaseModel):
    question: str = Field(min_length=5)
    expected_answer_points: list[str] = Field(min_length=1)


class QuestionGenerationResponse(BaseModel):
    role: str
    questions: list[InterviewQuestion]
