import pytest
from unittest.mock import patch
from app.models import (
    GeneratedQuestion,
    Interview,
    Interview,
    QuestionGeneration,
)
from app.services.interview_session_service import InterviewSessionService


def create_interview_with_generation(db_session, include_questions=True):
    interview = Interview(
        role="Python Developer",
        difficulty="Medium",
        is_deleted=False,
    )
    db_session.add(interview)
    db_session.flush()

    generation = QuestionGeneration(
        role="Python Developer",
        experience_years=3,
        skills=["Python", "FastAPI"],
        difficulty="Medium",
        interview_id=interview.id,
    )
    db_session.add(generation)
    db_session.flush()

    if include_questions:
        question = GeneratedQuestion(
            generation_id=generation.id,
            question="What is a Python decorator?",
            expected_answer_points=[
                "A function that modifies another function",
                "Uses the @ syntax",
            ],
        )
        db_session.add(question)
        db_session.flush()

    return interview, generation


def test_create_session_success(db_session):
    interview, generation = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    assert session.id is not None
    assert session.interview_id == interview.id
    assert session.generation_id == generation.id
    assert session.status == "in_progress"
    assert session.completed_at is None


def test_create_session_interview_not_found(db_session):
    with pytest.raises(ValueError, match="Interview not found"):
        InterviewSessionService.create_session(
            interview_id=999999,
            db=db_session,
        )


def test_create_session_without_questions(db_session):
    interview, _ = create_interview_with_generation(
        db_session,
        include_questions=False,
    )

    with pytest.raises(
        ValueError,
        match="No generated questions found",
    ):
        InterviewSessionService.create_session(
            interview_id=interview.id,
            db=db_session,
        )

def test_get_session_details_success(db_session):
    from app.services.interview_session_service import (
        InterviewSessionService,
    )

    interview, generation = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    result = InterviewSessionService.get_session_details(
        session_id=session.id,
        db=db_session,
    )

    assert result.id == session.id
    assert result.interview_id == interview.id
    assert result.generation_id == generation.id
    assert len(result.generation.questions) == 1
    assert result.answer_attempts == []


def test_get_session_details_not_found(db_session):
    import pytest

    from app.services.interview_session_service import (
        InterviewSessionService,
    )

    with pytest.raises(
        ValueError,
        match="Interview session not found",
    ):
        InterviewSessionService.get_session_details(
            session_id=999999,
            db=db_session,
        )


def test_get_interview_sessions_success(db_session):
    interview, _ = create_interview_with_generation(db_session)

    first_session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )
    second_session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    sessions = InterviewSessionService.get_interview_sessions(
        interview_id=interview.id,
        db=db_session,
    )

    assert len(sessions) == 2
    assert {session.id for session in sessions} == {
        first_session.id,
        second_session.id,
    }


def test_get_interview_sessions_interview_not_found(db_session):
    with pytest.raises(ValueError, match="Interview not found"):
        InterviewSessionService.get_interview_sessions(
            interview_id=999999,
            db=db_session,
        )


def test_complete_session_early_success(db_session):
    interview, generation = create_interview_with_generation(
        db_session,
        include_questions=True,
    )
    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )
    completed_session = InterviewSessionService.complete_session(
        session_id=session.id,
        db=db_session,
    )

    assert completed_session.id == session.id
    assert completed_session.status == "completed"
    assert completed_session.completed_at is not None

    db_session.refresh(completed_session)

    assert completed_session.status == "completed"
    assert completed_session.completed_at is not None


def test_complete_session_already_completed(db_session):
    interview, _ = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )
    first_result = InterviewSessionService.complete_session(
        session_id=session.id,
        db=db_session,
    )
    original_completed_at = first_result.completed_at

    second_result = InterviewSessionService.complete_session(
        session_id=session.id,
        db=db_session,
    )

    assert second_result.id == session.id
    assert second_result.status == "completed"
    assert second_result.completed_at == original_completed_at


def test_submit_answer_rejected_for_completed_session(db_session):
    interview, _ = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    question = session.generation.questions[0]

    InterviewSessionService.complete_session(
        session_id=session.id,
        db=db_session,
    )

    with pytest.raises(
        ValueError,
        match="This interview session is already completed.",
    ):
        InterviewSessionService.submit_answer(
            session_id=session.id,
            generated_question_id=question.id,
            user_answer="This answer should be rejected.",
            db=db_session,
        )


def test_retry_evaluation_rejected_for_completed_session(db_session):
    interview, _ = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    InterviewSessionService.complete_session(
        session_id=session.id,
        db=db_session,
    )

    with pytest.raises(
        ValueError,
        match="This interview session is already completed.",
    ):
        InterviewSessionService.retry_evaluation(
            session_id=session.id,
            attempt_id=999999,
            db=db_session,
        )


def test_submit_answer_auto_completes_session(
    db_session,
):
    interview, generation = create_interview_with_generation(
        db_session,
        include_questions=True,
    )

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    question = generation.questions[0]

    with patch(
        "app.services.interview_session_service.AnswerEvaluationService"
    ) as mock_evaluator:
        mock_evaluator.return_value.evaluate_answer.return_value = (
            None
        )

        attempt, evaluation = InterviewSessionService.submit_answer(
            session_id=session.id,
            generated_question_id=question.id,
            user_answer="A decorator modifies or extends a function.",
            db=db_session,
        )

    db_session.refresh(session)

    assert attempt.evaluation_status == "succeeded"
    assert session.status == "completed"
    assert session.completed_at is not None
    mock_evaluator.return_value.evaluate_answer.assert_called_once()


def test_submit_answer_keeps_session_in_progress_when_questions_remain(db_session):
    interview, generation = create_interview_with_generation(db_session)

    second_question = GeneratedQuestion(
        generation_id=generation.id,
        question="What is FastAPI?",
        expected_answer_points=["A Python web framework", "Supports API development"],
    )
    db_session.add(second_question)
    db_session.flush()

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    first_question = generation.questions[0]

    with patch(
        "app.services.interview_session_service.AnswerEvaluationService"
    ) as mock_evaluator:
        mock_evaluator.return_value.evaluate_answer.return_value = None

        attempt, evaluation = InterviewSessionService.submit_answer(
            session_id=session.id,
            generated_question_id=first_question.id,
            user_answer="A decorator modifies another function.",
            db=db_session,
        )

    db_session.refresh(session)

    assert attempt.evaluation_status == "succeeded"
    assert session.status == "in_progress"
    assert session.completed_at is None


def test_submit_answer_does_not_complete_session_when_evaluation_fails(db_session):
    interview, generation = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    question = generation.questions[0]

    with patch(
        "app.services.interview_session_service.AnswerEvaluationService"
    ) as mock_evaluator:
        mock_evaluator.return_value.evaluate_answer.side_effect = Exception(
            "AI evaluation failed"
        )

        attempt, evaluation = InterviewSessionService.submit_answer(
            session_id=session.id,
            generated_question_id=question.id,
            user_answer="A decorator modifies another function.",
            db=db_session,
        )

    db_session.refresh(session)
    db_session.refresh(attempt)

    assert attempt.evaluation_status == "failed"
    assert session.status == "in_progress"
    assert session.completed_at is None
    assert evaluation is None

    mock_evaluator.return_value.evaluate_answer.assert_called_once()


def test_retry_evaluation_succeeds_after_failed_attempt(db_session):
    interview, generation = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )
    question = generation.questions[0]

    with patch(
        "app.services.interview_session_service.AnswerEvaluationService"
    ) as mock_evaluator:
        mock_evaluator.return_value.evaluate_answer.side_effect = Exception(
            "AI evaluation failed"
        )

        attempt, evaluation = InterviewSessionService.submit_answer(
            session_id=session.id,
            generated_question_id=question.id,
            user_answer="A decorator modifies another function.",
            db=db_session,
        )

    assert attempt.evaluation_status == "failed"
    assert evaluation is None

    original_attempt_id = attempt.id
    original_attempt_number = attempt.attempt_number

    with patch(
        "app.services.interview_session_service.AnswerEvaluationService"
    ) as mock_evaluator:
        mock_evaluator.return_value.evaluate_answer.return_value = None

        retried_attempt, evaluation = InterviewSessionService.retry_evaluation(
            session_id=session.id,
            attempt_id=original_attempt_id,
            db=db_session,
        )

    db_session.refresh(session)

    assert retried_attempt.id == original_attempt_id
    assert retried_attempt.attempt_number == original_attempt_number
    assert retried_attempt.evaluation_status == "succeeded"
    assert session.status == "completed"
    assert session.completed_at is not None
    assert evaluation is None


def test_get_session_results_with_unanswered_questions(db_session):
    interview, generation = create_interview_with_generation(db_session)

    session = InterviewSessionService.create_session(
        interview_id=interview.id,
        db=db_session,
    )

    result = InterviewSessionService.get_session_results(
        session_id=session.id,
        db=db_session,
    )

    assert result["id"] == session.id
    assert result["status"] == "in_progress"
    assert result["total_questions"] == 1
    assert result["answered_questions"] == 0
    assert result["unanswered_questions"] == 1
    assert result["failed_evaluations"] == 0
    assert result["average_score"] is None

    question_result = result["questions"][0]
    assert question_result["question"] == "What is a Python decorator?"
    assert question_result["attempts"] == []
    assert question_result["successful_attempts"] == 0
    assert question_result["total_attempts"] == 0


def test_get_session_results_not_found(db_session):
    with pytest.raises(
        ValueError,
        match="Interview session not found",
    ):
        InterviewSessionService.get_session_results(
            session_id=999999,
            db=db_session,
        )
