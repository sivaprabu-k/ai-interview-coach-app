export interface AnswerEvaluationRequest {
  question: string
  expected_answer_points: string[]
  user_answer: string
}

export interface AnswerEvaluation {
  score: number
  strengths: string[]
  areas_to_improve: string[]
  suggested_answer: string
  feedback: string
}

export interface ApiResponse<T> {
  status: boolean
  data: T
  status_code: number
  message: string
}

export interface InterviewQuestion {
  question: string
  expected_answer_points: string[]
}

export interface InterviewEvaluation {
  candidate: string
  role: string
  overallScore: number
  skills: {
    name: string
    score: number
  }[]
  strengths: string[]
  improvements: string[]
  questionDetails: QuestionEvaluation[]
}

export interface QuestionEvaluation {
  question: string
  user_answer: string
  score: number
  strengths: string[]
  areas_to_improve: string[]
  suggested_answer: string
  feedback: string
}