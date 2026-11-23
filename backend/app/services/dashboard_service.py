from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session
from app.models import (
    AnswerAttempt,
    AnswerEvaluation,
    Interview,
    InterviewSession,
)


class DashboardService:

    @staticmethod
    def get_dashboard_summary(
        db: Session,
        user_id: int,
    ) -> dict:

        total_interviews = db.scalar(
            select(func.count(Interview.id)).where(
                Interview.user_id == user_id,
                Interview.is_deleted.is_(False),
            )
        ) or 0

        session_stats = db.execute(
            select(
                InterviewSession.status,
                func.count(InterviewSession.id),
            )
            .join(
                Interview,
                Interview.id == InterviewSession.interview_id,
            )
            .where(
                Interview.user_id == user_id,
                Interview.is_deleted.is_(False),
            )
            .group_by(InterviewSession.status)
        ).all()

        status_counts = {
            status: count for status, count in session_stats
        }

        completed_interviews = status_counts.get("completed", 0)
        in_progress_interviews = status_counts.get("in_progress", 0)

        evaluation_stats = db.execute(
            select(
                func.count(AnswerEvaluation.id),
                func.avg(AnswerEvaluation.score),
            ).where(
                AnswerEvaluation.user_id == user_id,
            )
        ).one()

        total_evaluations = evaluation_stats[0] or 0

        average_score = (
            round(float(evaluation_stats[1]), 2)
            if evaluation_stats[1] is not None
            else None
        )

        recent_session_rows = db.execute(
            select(
                InterviewSession.id,
                InterviewSession.interview_id,
                Interview.role,
                Interview.difficulty,
                InterviewSession.status,
                InterviewSession.started_at,
                InterviewSession.completed_at,
                func.avg(AnswerEvaluation.score),
            )
            .join(
                Interview,
                Interview.id == InterviewSession.interview_id,
            )
            .outerjoin(
                AnswerAttempt,
                and_(
                    AnswerAttempt.session_id == InterviewSession.id,
                    AnswerAttempt.evaluation_status == "succeeded",
                ),
            )
            .outerjoin(
                AnswerEvaluation,
                AnswerEvaluation.answer_attempt_id == AnswerAttempt.id,
            )
            .where(
                Interview.user_id == user_id,
                Interview.is_deleted.is_(False),
            )
            .group_by(
                InterviewSession.id,
                InterviewSession.interview_id,
                Interview.role,
                Interview.difficulty,
                InterviewSession.status,
                InterviewSession.started_at,
                InterviewSession.completed_at,
            )
            .order_by(
                desc(InterviewSession.started_at),
                desc(InterviewSession.id),
            )
            .limit(10)
        ).all()

        recent_sessions = [
            {
                "session_id": row[0],
                "interview_id": row[1],
                "role": row[2],
                "difficulty": row[3],
                "status": row[4],
                "started_at": row[5],
                "completed_at": row[6],
                "average_score": (
                    round(float(row[7]), 2)
                    if row[7] is not None
                    else None
                ),
            }
            for row in recent_session_rows
        ]

        recent_evaluation_rows = db.execute(
            select(
                AnswerEvaluation.id,
                AnswerEvaluation.question,
                AnswerEvaluation.score,
                AnswerEvaluation.created_at,
            )
            .where(
                AnswerEvaluation.user_id == user_id,
            )
            .order_by(
                desc(AnswerEvaluation.created_at),
                desc(AnswerEvaluation.id),
            )
            .limit(10)
        ).all()

        recent_evaluations = [
            {
                "id": row[0],
                "question": row[1],
                "score": row[2],
                "created_at": row[3],
            }
            for row in recent_evaluation_rows
        ]

        # Latest evaluation details
        latest_record = db.scalar(
            select(AnswerEvaluation)
            .where(
                AnswerEvaluation.user_id == user_id,
            )
            .order_by(
                desc(AnswerEvaluation.created_at),
                desc(AnswerEvaluation.id),
            )
            .limit(1)
        )

        latest_evaluation = None

        if latest_record is not None:
            latest_evaluation = {
                "session_id": None,
                "role": "Individual Answer Evaluation",
                "difficulty": None,
                "overall_score": float(latest_record.score),
                "strengths": latest_record.strengths or [],
                "improvements": latest_record.areas_to_improve or [],
                "question_details": [
                    {
                        "question": latest_record.question,
                        "user_answer": latest_record.user_answer,
                        "score": latest_record.score,
                        "strengths": latest_record.strengths or [],
                        "areas_to_improve": (
                            latest_record.areas_to_improve or []
                        ),
                        "suggested_answer": latest_record.suggested_answer,
                        "feedback": latest_record.feedback,
                    }
                ],
            }

        return {
            "stats": {
                "total_interviews": total_interviews,
                "completed_interviews": completed_interviews,
                "in_progress_interviews": in_progress_interviews,
                "average_score": average_score,
                "total_evaluations": total_evaluations,
            },
            "recent_sessions": recent_sessions,
            "recent_evaluations": recent_evaluations,
            "latest_evaluation": latest_evaluation,
        }
