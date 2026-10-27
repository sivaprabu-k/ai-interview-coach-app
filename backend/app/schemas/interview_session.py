from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


class InterviewSessionCreateResponse(BaseModel):
    id: int
    interview_id: int
    generation_id: int
    status: Literal["in_progress", "completed"]
    started_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class SessionQuestionResponse(BaseModel):
    id: int
    question: str
    expected_answer_points: list[str]

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionStartResponse(InterviewSessionCreateResponse):
    questions: list[SessionQuestionResponse]
    total_questions: int



class AnswerAttemptResponse(BaseModel):
    id: int
    generated_question_id: int
    attempt_number: int
    user_answer: str
    evaluation_status: Literal["pending", "succeeded", "failed"]
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionQuestionProgressResponse(BaseModel):
    question_id: int
    attempts: list[AnswerAttemptResponse]
    successful_attempts: int
    total_attempts: int


class InterviewSessionDetailResponse(InterviewSessionCreateResponse):
    questions: list[SessionQuestionProgressResponse]
    total_questions: int
    completed_questions: int
    unanswered_questions: int
    failed_evaluations: int


class AnswerSubmissionRequest(BaseModel):
    generated_question_id: int
    user_answer: str


class AnswerEvaluationResponse(BaseModel):
    score: float
    strengths: list[str]
    areas_to_improve: list[str]
    suggested_answer: str
    feedback: str


class AnswerSubmissionResponse(BaseModel):
    attempt: AnswerAttemptResponse
    evaluation: AnswerEvaluationResponse | None = None
