import api from './api'
import type { ApiResponse } from '../types/evaluation'
import type { DashboardSummary } from '../types/dashboard'

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await api.get<ApiResponse<DashboardSummary>>(
    '/dashboard/summary'
  )

  return response.data.data
}