export interface DashboardStats {
  total_interviews: number
  completed_interviews: number
  in_progress_interviews: number
  average_score: number | null
  total_evaluations: number
}

export interface DashboardRecentSession {
  session_id: number
  interview_id: number
  role: string
  difficulty: string
  status: 'in_progress' | 'completed'
  started_at: string
  completed_at: string | null
  average_score: number | null
}

export interface DashboardQuestionEvaluation {
  question: string
  user_answer: string
  score: number
  strengths: string[]
  areas_to_improve: string[]
  suggested_answer: string
  feedback: string
}

export interface DashboardLatestEvaluation {
  session_id: number
  role: string
  difficulty: string
  overall_score: number
  strengths: string[]
  improvements: string[]
  question_details: DashboardQuestionEvaluation[]
}

export interface DashboardSummary {
  stats: DashboardStats
  recent_sessions: DashboardRecentSession[]
  latest_evaluation: DashboardLatestEvaluation | null
}