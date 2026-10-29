from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    AnswerAttempt,
    AnswerEvaluation,
    GeneratedQuestion,
    Interview,
    InterviewSession,
    QuestionGeneration,
)
from app.schemas.answer_evaluation import AnswerEvaluationRequest
from app.services.ai.answer_evaluation_service import AnswerEvaluationService
import logging

logger = logging.getLogger(__name__)

class InterviewSessionService:

    @staticmethod
    def create_session(
        interview_id: int,
        db: Session,
    ) -> InterviewSession:
        interview = db.scalar(
            select(Interview).where(
                Interview.id == interview_id,
                Interview.is_deleted.is_(False),
            )
        )

        if interview is None:
            raise ValueError("Interview not found.")

        generation = db.scalar(
            select(QuestionGeneration)
            .options(selectinload(QuestionGeneration.questions))
            .where(QuestionGeneration.interview_id == interview_id)
            .order_by(
                desc(QuestionGeneration.created_at),
                desc(QuestionGeneration.id),
            )
            .limit(1)
        )

        if generation is None or not generation.questions:
            raise ValueError(
                "No generated questions found for this interview."
            )

        session = InterviewSession(
            interview_id=interview_id,
            generation_id=generation.id,
            status="in_progress",
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    @staticmethod
    def get_session_details(
        session_id: int,
        db: Session,
    ) -> InterviewSession:
        session = db.scalar(
            select(InterviewSession)
            .options(
                selectinload(
                    InterviewSession.generation
                ).selectinload(
                    QuestionGeneration.questions
                ),
                selectinload(
                    InterviewSession.answer_attempts
                ).selectinload(
                    AnswerAttempt.evaluation
                ),
            )
            .where(InterviewSession.id == session_id)
        )

        if session is None:
            raise ValueError("Interview session not found.")

        return session

    
    @staticmethod
    def get_session_results(
        session_id: int,
        db: Session,
    ) -> dict:
        session = db.scalar(
            select(InterviewSession)
            .options(
                selectinload(
                    InterviewSession.generation
                ).selectinload(
                    QuestionGeneration.questions
                ),
                selectinload(
                    InterviewSession.answer_attempts
                ).selectinload(
                    AnswerAttempt.evaluation
                ),
                selectinload(
                    InterviewSession.answer_attempts
                ).selectinload(
                    AnswerAttempt.generated_question
                ),
            )
            .where(InterviewSession.id == session_id)
        )

        if session is None:
            raise ValueError("Interview session not found.")

        questions = sorted(
            session.generation.questions,
            key=lambda question: question.id,
        )

        attempts_by_question: dict[int, list[AnswerAttempt]] = {}
        for attempt in session.answer_attempts:
            attempts_by_question.setdefault(
                attempt.generated_question_id, []
            ).append(attempt)

        question_results = []
        successful_scores = []
        answered_questions = 0
        failed_evaluations = 0

        for question in questions:
            attempts = sorted(
                attempts_by_question.get(question.id, []),
                key=lambda attempt: attempt.attempt_number,
            )

            successful_attempts = [
                attempt
                for attempt in attempts
                if attempt.evaluation_status == "succeeded"
            ]

            if successful_attempts:
                answered_questions += 1

            failed_evaluations += sum(
                attempt.evaluation_status == "failed"
                for attempt in attempts
            )

            attempt_results = []
            for attempt in attempts:
                evaluation = attempt.evaluation

                if (
                    attempt.evaluation_status == "succeeded"
                    and evaluation is not None
                ):
                    successful_scores.append(evaluation.score)

                attempt_results.append(
                    {
                        "id": attempt.id,
                        "generated_question_id": (
                            attempt.generated_question_id
                        ),
                        "attempt_number": attempt.attempt_number,
                        "user_answer": attempt.user_answer,
                        "evaluation_status": (
                            attempt.evaluation_status
                        ),
                        "submitted_at": attempt.submitted_at,
                        "evaluation": (
                            {
                                "id": evaluation.id,
                                "score": evaluation.score,
                                "strengths": evaluation.strengths,
                                "areas_to_improve": (
                                    evaluation.areas_to_improve
                                ),
                                "suggested_answer": (
                                    evaluation.suggested_answer
                                ),
                                "feedback": evaluation.feedback,
                                "created_at": evaluation.created_at,
                            }
                            if (
                                attempt.evaluation_status == "succeeded"
                                and evaluation is not None
                            )
                            else None
                        ),
                    }
                )

            question_results.append(
                {
                    "question_id": question.id,
                    "question": question.question,
                    "expected_answer_points": (
                        question.expected_answer_points
                    ),
                    "attempts": attempt_results,
                    "successful_attempts": len(successful_attempts),
                    "total_attempts": len(attempts),
                }
            )

        average_score = (
            round(sum(successful_scores) / len(successful_scores), 2)
            if successful_scores
            else None
        )

        return {
            "id": session.id,
            "interview_id": session.interview_id,
            "generation_id": session.generation_id,
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "questions": question_results,
            "total_questions": len(questions),
            "answered_questions": answered_questions,
            "unanswered_questions": len(questions) - answered_questions,
            "failed_evaluations": failed_evaluations,
            "average_score": average_score,
        }


    @staticmethod
    def get_interview_sessions(
        interview_id: int,
        db: Session,
    ) -> list[InterviewSession]:
        interview = db.scalar(
            select(Interview).where(
                Interview.id == interview_id,
                Interview.is_deleted.is_(False),
            )
        )

        if interview is None:
            raise ValueError("Interview not found.")

        sessions = db.scalars(
            select(InterviewSession)
            .where(InterviewSession.interview_id == interview_id)
            .order_by(
                desc(InterviewSession.started_at),
                desc(InterviewSession.id),
            )
        ).all()

        return list(sessions)

    @staticmethod
    def submit_answer(
        session_id: int,
        generated_question_id: int,
        user_answer: str,
        db: Session,
    ) -> tuple[AnswerAttempt, AnswerEvaluation | None]:
        session = db.scalar(
            select(InterviewSession)
            .options(
                selectinload(
                    InterviewSession.generation
                ).selectinload(
                    QuestionGeneration.questions
                )
            )
            .where(InterviewSession.id == session_id)
        )

        if session is None:
            raise ValueError("Interview session not found.")

        if session.status != "in_progress":
            raise ValueError("This interview session is already completed.")

        if not user_answer.strip():
            raise ValueError("Answer cannot be empty.")

        question = db.scalar(
            select(GeneratedQuestion).where(
                GeneratedQuestion.id == generated_question_id,
                GeneratedQuestion.generation_id == session.generation_id,
            )
        )

        if question is None:
            raise ValueError(
                "Question does not belong to this interview session."
            )

        latest_attempt_number = db.scalar(
            select(func.max(AnswerAttempt.attempt_number)).where(
                AnswerAttempt.session_id == session_id,
                AnswerAttempt.generated_question_id == generated_question_id,
            )
        )

        attempt = AnswerAttempt(
            session_id=session_id,
            generated_question_id=generated_question_id,
            attempt_number=(latest_attempt_number or 0) + 1,
            user_answer=user_answer,
            evaluation_status="pending",
        )

        db.add(attempt)
        db.commit()
        db.refresh(attempt)

        request = AnswerEvaluationRequest(
            question=question.question,
            expected_answer_points=question.expected_answer_points,
            user_answer=user_answer,
        )

        attempt_id = attempt.id

        try:
            evaluator = AnswerEvaluationService()
            evaluator.evaluate_answer(
                request=request,
                db=db,
                generated_question_id=generated_question_id,
                answer_attempt_id=attempt_id,
            )

            attempt.evaluation_status = "succeeded"
            db.commit()
            db.refresh(attempt)

            evaluation = db.scalar(
                select(AnswerEvaluation).where(
                    AnswerEvaluation.answer_attempt_id == attempt.id
                )
            )

            question_ids = {
                item.id for item in session.generation.questions
            }

            successful_question_ids = set(
                db.scalars(
                    select(AnswerAttempt.generated_question_id)
                    .where(
                        AnswerAttempt.session_id == session_id,
                        AnswerAttempt.evaluation_status == "succeeded",
                    )
                    .distinct()
                ).all()
            )

            if question_ids.issubset(successful_question_ids):
                session.status = "completed"
                session.completed_at = func.now()
                db.commit()
                db.refresh(attempt)

            return attempt, evaluation

        except Exception:
            logger.exception("Answer evaluation failed")

            db.rollback()

            saved_attempt = db.get(AnswerAttempt, attempt_id)

            if saved_attempt is not None:
                saved_attempt.evaluation_status = "failed"
                db.commit()
                db.refresh(saved_attempt)
                return saved_attempt, None

            raise

    
    @staticmethod
    def retry_evaluation(
        session_id: int,
        attempt_id: int,
        db: Session,
    ) -> tuple[AnswerAttempt, AnswerEvaluation | None]:
        session = db.scalar(
            select(InterviewSession).where(
                InterviewSession.id == session_id
            )
        )

        if session is None:
            raise ValueError("Interview session not found.")

        if session.status != "in_progress":
            raise ValueError("This interview session is already completed.")

        attempt = db.scalar(
            select(AnswerAttempt).where(
                AnswerAttempt.id == attempt_id,
                AnswerAttempt.session_id == session_id,
            )
        )

        if attempt is None:
            raise ValueError("Answer attempt not found in this session.")

        question = db.scalar(
            select(GeneratedQuestion).where(
                GeneratedQuestion.id == attempt.generated_question_id,
                GeneratedQuestion.generation_id == session.generation_id,
            )
        )

        if question is None:
            raise ValueError("Question does not belong to this interview session.")

        request = AnswerEvaluationRequest(
            question=question.question,
            expected_answer_points=question.expected_answer_points,
            user_answer=attempt.user_answer,
        )

        try:
            evaluator = AnswerEvaluationService()
            evaluator.evaluate_answer(
                request=request,
                db=db,
                generated_question_id=question.id,
                answer_attempt_id=attempt.id,
            )

            attempt.evaluation_status = "succeeded"
            db.commit()
            db.refresh(attempt)

            evaluation = db.scalar(
                select(AnswerEvaluation).where(
                    AnswerEvaluation.answer_attempt_id == attempt.id
                )
            )

            question_ids = {
                item.id
                for item in db.scalars(
                    select(GeneratedQuestion).where(
                        GeneratedQuestion.generation_id == session.generation_id)
                ).all()
            }

            successful_question_ids = set(
                db.scalars(
                    select(AnswerAttempt.generated_question_id)
                    .where(
                        AnswerAttempt.session_id == session_id,
                        AnswerAttempt.evaluation_status == "succeeded",
                    )
                    .distinct()
                ).all()
            )

            if question_ids.issubset(successful_question_ids):
                session.status = "completed"
                session.completed_at = func.now()
                db.commit()
                db.refresh(attempt)

            return attempt, evaluation

        except Exception:
            db.rollback()
            logger("Unexpected error while attempting retry evaluation")

            saved_attempt = db.get(AnswerAttempt, attempt_id)

            if saved_attempt is not None:
                saved_attempt.evaluation_status = "failed"
                db.commit()
                db.refresh(saved_attempt)
                return saved_attempt, None

            raise

    
    @staticmethod
    def complete_session(session_id: int, db: Session) -> InterviewSession:
        session = db.scalar(
            select(InterviewSession).where(
                InterviewSession.id == session_id
            )
        )

        if session is None:
            raise ValueError("Interview session not found.")

        if session.status == "completed":
           return session

        session.status = "completed"
        session.completed_at = func.now()

        try:
            db.commit()
            db.refresh(session)
        except Exception:
            db.rollback()
            raise

        return session
