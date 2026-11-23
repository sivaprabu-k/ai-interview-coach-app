from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


class DashboardStatsResponse(BaseModel):
    total_interviews: int
    completed_interviews: int
    in_progress_interviews: int
    average_score: float | None = None
    total_evaluations: int


class DashboardRecentSessionResponse(BaseModel):
    session_id: int
    interview_id: int
    role: str
    difficulty: str
    status: Literal["in_progress", "completed"]
    started_at: datetime
    completed_at: datetime | None = None
    average_score: float | None = None


class DashboardRecentEvaluationResponse(BaseModel):
    id: int
    question: str
    score: int
    created_at: datetime


class DashboardQuestionEvaluationResponse(BaseModel):
    question: str
    user_answer: str
    score: int
    strengths: list[str]
    areas_to_improve: list[str]
    suggested_answer: str
    feedback: str


class DashboardLatestEvaluationResponse(BaseModel):
    session_id: int | None = None
    role: str
    difficulty: str | None = None
    overall_score: float
    strengths: list[str]
    improvements: list[str]
    question_details: list[DashboardQuestionEvaluationResponse]


class DashboardSummaryResponse(BaseModel):
    stats: DashboardStatsResponse
    recent_sessions: list[DashboardRecentSessionResponse]
    recent_evaluations: list[DashboardRecentEvaluationResponse]
    latest_evaluation: DashboardLatestEvaluationResponse | None = None

    model_config = ConfigDict(from_attributes=True)
