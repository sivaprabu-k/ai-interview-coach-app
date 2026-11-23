import api from './api'

export interface AIQuestion {
  id: number
  question: string
  expected_answer_points: string[]
}

export interface QuestionGenerationRequest {
  role?: string
  experience_years?: number
  skills?: string[]
  difficulty?: 'easy' | 'medium' | 'hard'
  interview_id?: number
  number_of_questions: number
}

export interface QuestionGenerationResponse {
  id: number
  role: string
  questions: AIQuestion[]
}

export const generateAIQuestions = async (
  request: QuestionGenerationRequest,
): Promise<QuestionGenerationResponse> => {
  const response = await api.post('/ai-questions/generate', request)

  return response.data.data
}
