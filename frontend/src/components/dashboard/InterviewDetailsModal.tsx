import {
  X,
  CalendarDays,
  BriefcaseBusiness,
  User,
  Award,
  LoaderCircle,
  CheckCircle2,
  Clock,
  AlertCircle,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import type { DashboardRecentSession } from '../../types/dashboard'
import {
  getSessionDetails,
  submitSessionAnswer,
  retrySessionEvaluation,
} from '../../services/interviewSessionService'
import type { InterviewSessionDetail } from '../../services/interviewSessionService'

interface InterviewDetailsModalProps {
  interview: DashboardRecentSession | null
  onClose: () => void
}

function InterviewDetailsModal({
  interview,
  onClose,
}: InterviewDetailsModalProps) {
  const [session, setSession] = useState<InterviewSessionDetail | null>(null)
  const [loading, setLoading] = useState(false)
  const [submittingQuestionId, setSubmittingQuestionId] =
    useState<number | null>(null)
  const [retryingAttemptId, setRetryingAttemptId] = useState<number | null>(
    null,
  )
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!interview) {
      setSession(null)
      return
    }

    let cancelled = false

    const fetchSession = async () => {
      setLoading(true)
      setError(null)
      setSession(null)
      setAnswers({})

      try {
        const data = await getSessionDetails(interview.session_id)

        if (!cancelled) {
          setSession(data)
        }
      } catch {
        if (!cancelled) {
          setError('Unable to load interview session details.')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchSession()

    return () => {
      cancelled = true
    }
  }, [interview])

  if (!interview) return null

  const formattedDate = new Date(interview.started_at).toLocaleString()

  const handleSubmitAnswer = async (questionId: number) => {
    const answer = answers[questionId]?.trim()

    if (!answer) {
      setError('Please enter your answer before submitting.')
      return
    }

    setSubmittingQuestionId(questionId)
    setError(null)

    try {
      await submitSessionAnswer(interview.session_id, {
        generated_question_id: questionId,
        user_answer: answer,
      })

      const updatedSession = await getSessionDetails(interview.session_id)
      setSession(updatedSession)

      setAnswers((previous) => ({
        ...previous,
        [questionId]: '',
      }))
    } catch {
      setError('Unable to submit your answer. Please try again.')
    } finally {
      setSubmittingQuestionId(null)
    }
  }

  const handleRetryEvaluation = async (attemptId: number) => {
    setRetryingAttemptId(attemptId)
    setError(null)

    try {
      await retrySessionEvaluation(interview.session_id, attemptId)

      const updatedSession = await getSessionDetails(interview.session_id)
      setSession(updatedSession)
    } catch {
      setError('Unable to retry evaluation. Please try again.')
    } finally {
      setRetryingAttemptId(null)
    }
  }

  const getQuestionStatus = (
    question: InterviewSessionDetail['questions'][number],
  ) => {
    if (question.successful_attempts > 0) {
      return 'answered'
    }

    const latestAttempt = [...question.attempts].sort(
      (a, b) => b.attempt_number - a.attempt_number,
    )[0]

    if (latestAttempt?.evaluation_status === 'failed') {
      return 'failed'
    }

    if (latestAttempt?.evaluation_status === 'pending') {
      return 'evaluating'
    }

    return 'pending'
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="interview-modal-title"
        className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-2xl bg-white p-6 shadow-xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h2
              id="interview-modal-title"
              className="text-xl font-bold text-gray-800"
            >
              Interview Details
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              View your questions and continue your interview
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close modal"
            className="rounded-lg p-2 text-gray-500 transition hover:bg-gray-100"
          >
            <X size={20} />
          </button>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="flex items-center gap-3 rounded-xl bg-purple-50 p-4">
            <User className="text-purple-600" size={22} />
            <div>
              <p className="text-xs text-gray-500">Interview Role</p>
              <p className="font-semibold text-gray-800">
                {interview.role}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-gray-100 p-4">
            <BriefcaseBusiness className="text-purple-600" size={22} />
            <div>
              <p className="text-xs text-gray-500">Difficulty</p>
              <p className="font-semibold capitalize text-gray-800">
                {interview.difficulty}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-gray-100 p-4">
            <CalendarDays className="text-purple-600" size={22} />
            <div>
              <p className="text-xs text-gray-500">Started At</p>
              <p className="text-sm font-medium text-gray-800">
                {formattedDate}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-xl border border-gray-100 p-4">
            <Award className="text-purple-600" size={22} />
            <div>
              <p className="text-xs text-gray-500">Average Score</p>
              <p className="font-semibold text-gray-800">
                {interview.average_score !== null
                  ? `${interview.average_score}%`
                  : '--'}
              </p>
            </div>
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center gap-2 py-10 text-sm text-gray-500">
            <LoaderCircle size={20} className="animate-spin" />
            Loading interview questions...
          </div>
        )}

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {session && !loading && (
          <>
            <div className="mb-6 rounded-xl border border-gray-100 p-4">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="font-semibold text-gray-800">
                  Session Progress
                </h3>

                <span className="text-sm font-semibold text-purple-600">
                  {session.completed_questions}/{session.total_questions} Answered
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full rounded-full bg-purple-600 transition-all"
                  style={{
                    width: `${
                      session.total_questions > 0
                        ? (session.completed_questions /
                            session.total_questions) *
                          100
                        : 0
                    }%`,
                  }}
                />
              </div>

              <p className="mt-3 text-sm text-gray-500">
                {session.status === 'completed'
                  ? 'All questions have been successfully evaluated.'
                  : `${session.unanswered_questions} questions remaining`}
              </p>
            </div>

            <h3 className="mb-4 text-lg font-bold text-gray-800">
              Interview Questions
            </h3>

            <div className="space-y-5">
              {session.questions.map((question, index) => {
                const status = getQuestionStatus(question)

                const latestAttempt = [...question.attempts].sort(
                  (a, b) => b.attempt_number - a.attempt_number,
                )[0]

                return (
                  <div
                    key={question.question_id}
                    className="rounded-xl border border-gray-200 p-5"
                  >
                    <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                      <span className="text-sm font-semibold text-gray-500">
                        Question {index + 1}
                      </span>

                      {status === 'answered' && (
                        <span className="flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">
                          <CheckCircle2 size={14} />
                          Answered
                        </span>
                      )}

                      {status === 'pending' && (
                        <span className="flex items-center gap-1 rounded-full bg-yellow-100 px-3 py-1 text-xs font-semibold text-yellow-700">
                          <Clock size={14} />
                          Pending
                        </span>
                      )}

                      {status === 'failed' && (
                        <span className="flex items-center gap-1 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
                          <AlertCircle size={14} />
                          Evaluation Failed
                        </span>
                      )}

                      {status === 'evaluating' && (
                        <span className="flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                          <LoaderCircle size={14} />
                          Evaluating
                        </span>
                      )}
                    </div>

                    <p className="font-semibold leading-relaxed text-gray-800">
                      {question.question}
                    </p>

                    {question.expected_answer_points.length > 0 && (
                      <details className="mt-3 text-sm">
                        <summary className="cursor-pointer font-medium text-purple-600">
                          View expected answer points
                        </summary>

                        <ul className="mt-2 list-disc space-y-1 pl-5 text-gray-600">
                          {question.expected_answer_points.map((point, i) => (
                            <li key={i}>{point}</li>
                          ))}
                        </ul>
                      </details>
                    )}

                    {latestAttempt && (
                      <div className="mt-4 rounded-lg bg-gray-50 p-3">
                        <p className="mb-1 text-xs font-semibold text-gray-500">
                          Previous Answer
                        </p>
                        <p className="whitespace-pre-wrap text-sm text-gray-700">
                          {latestAttempt.user_answer}
                        </p>
                      </div>
                    )}

                    {status === 'pending' &&
                      session.status === 'in_progress' && (
                        <div className="mt-4">
                          <textarea
                            rows={4}
                            value={answers[question.question_id] ?? ''}
                            onChange={(event) =>
                              setAnswers((previous) => ({
                                ...previous,
                                [question.question_id]: event.target.value,
                              }))
                            }
                            placeholder="Enter your answer here..."
                            className="w-full rounded-lg border border-gray-200 p-3 text-sm outline-none transition focus:border-purple-500 focus:ring-2 focus:ring-purple-100"
                          />

                          <button
                            type="button"
                            disabled={submittingQuestionId !== null}
                            onClick={() =>
                              handleSubmitAnswer(question.question_id)
                            }
                            className="mt-3 inline-flex cursor-pointer items-center gap-2 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            {submittingQuestionId === question.question_id && (
                              <LoaderCircle
                                size={16}
                                className="animate-spin"
                              />
                            )}
                            Submit Answer
                          </button>
                        </div>
                      )}

                    {status === 'failed' && latestAttempt && (
                      <div className="mt-4">
                        <p className="mb-3 text-sm text-red-600">
                          Your answer was saved, but evaluation failed.
                        </p>

                        <button
                          type="button"
                          disabled={retryingAttemptId !== null}
                          onClick={() =>
                            handleRetryEvaluation(latestAttempt.id)
                          }
                          className="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                          {retryingAttemptId === latestAttempt.id && (
                            <LoaderCircle
                              size={16}
                              className="animate-spin"
                            />
                          )}
                          Retry Evaluation
                        </button>
                      </div>
                    )}

                    {status === 'evaluating' && (
                      <p className="mt-3 text-sm text-blue-600">
                        Your answer is awaiting evaluation.
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </>
        )}

        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full cursor-pointer rounded-lg bg-gray-100 py-3 font-medium text-gray-700 transition hover:bg-gray-200"
        >
          Close
        </button>
      </div>
    </div>
  )
}

export default InterviewDetailsModal
