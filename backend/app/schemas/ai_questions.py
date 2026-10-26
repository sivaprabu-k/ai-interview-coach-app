from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class QuestionGenerationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    role: str = Field(min_length=2, max_length=100)
    experience_years: int = Field(ge=0, le=50)
    skills: list[str] = Field(min_length=1, max_length=20)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    interview_id: int | None = Field(default=None, ge=1)
    number_of_questions: int = Field(default=5, ge=1, le=10)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, skills: list[str]) -> list[str]:
        cleaned_skills = [skill.strip() for skill in skills]

        if any(not skill for skill in cleaned_skills):
            raise ValueError("Skills cannot be empty or contain only whitespace")

        return cleaned_skills


class InterviewQuestion(BaseModel):
    question: str = Field(min_length=5)
    expected_answer_points: list[str] = Field(min_length=1)


class QuestionGenerationResponse(BaseModel):
    role: str
    questions: list[InterviewQuestion]


class GeneratedQuestionHistory(BaseModel):
    id: int
    question: str
    expected_answer_points: list[str]

    model_config = ConfigDict(from_attributes=True)



class QuestionGenerationHistoryResponse(BaseModel):
    id: int
    interview_id: int | None = None
    role: str
    experience_years: int
    skills: list[str]
    difficulty: str
    created_at: datetime
    questions: list[GeneratedQuestionHistory]

    model_config = ConfigDict(from_attributes=True)

