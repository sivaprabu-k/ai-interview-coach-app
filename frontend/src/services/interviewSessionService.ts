import api from './api'

export interface InterviewCreateRequest {
  role: string
  difficulty: string
}

export interface InterviewCreateResponse {
  id: number
  role: string
  difficulty: string
  created_at: string
}

export const createInterview = async (
  request: InterviewCreateRequest,
): Promise<InterviewCreateResponse> => {
  const response = await api.post('/interviews', request)
  return response.data.data
}

export interface InterviewSessionResponse {
  id: number
  interview_id: number
  generation_id: number
  status: string
  questions: {
    id: number
    question: string
    expected_answer_points: string[]
  }[]
  total_questions: number
}

export const createInterviewSession = async (
  interviewId: number,
): Promise<InterviewSessionResponse> => {
  const response = await api.post(
    `/interviews/${interviewId}/sessions`,
  )

  return response.data.data
}

export interface SessionAnswerRequest {
  generated_question_id: number
  user_answer: string
}

export interface SessionAnswerResponse {
  attempt: Record<string, unknown>
  evaluation: {
    score: number
    strengths: string[]
    areas_to_improve: string[]
    suggested_answer: string
    feedback: string
  } | null
}

export const submitSessionAnswer = async (
  sessionId: number,
  request: SessionAnswerRequest,
): Promise<SessionAnswerResponse> => {
  const response = await api.post(
    `/sessions/${sessionId}/answers`,
    request,
  )

  return response.data.data
}

export interface SessionAttempt {
  id: number
  generated_question_id: number
  attempt_number: number
  user_answer: string
  evaluation_status: 'pending' | 'succeeded' | 'failed'
  submitted_at: string
}

export interface SessionQuestionProgress {
  question_id: number
  question: string
  expected_answer_points: string[]
  attempts: SessionAttempt[]
  successful_attempts: number
  total_attempts: number
}

export interface InterviewSessionDetail {
  id: number
  interview_id: number
  generation_id: number
  status: 'in_progress' | 'completed'
  started_at: string
  completed_at: string | null
  questions: SessionQuestionProgress[]
  total_questions: number
  completed_questions: number
  unanswered_questions: number
  failed_evaluations: number
}

export const getSessionDetails = async (
  sessionId: number,
): Promise<InterviewSessionDetail> => {
  const response = await api.get(`/sessions/${sessionId}`)
  return response.data.data
}

export const retrySessionEvaluation = async (
  sessionId: number,
  attemptId: number,
): Promise<void> => {
  await api.post(
    `/sessions/${sessionId}/answers/${attemptId}/retry-evaluation`,
  )
}
