import api from './api'
import type {
  AnswerEvaluationRequest,
  AnswerEvaluation,
  ApiResponse,
} from '../types/evaluation'

export const evaluateAnswer = async (
  request: AnswerEvaluationRequest,
): Promise<AnswerEvaluation> => {
  const response = await api.post<ApiResponse<AnswerEvaluation>>(
    '/answer-evaluations',
    request,
  )

  return response.data.data
}
