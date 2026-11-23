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