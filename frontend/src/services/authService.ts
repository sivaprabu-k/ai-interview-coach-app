import api from './api'

interface LoginRequest {
  email: string
  password: string
}

interface LoginResponse {
  access_token: string
  token_type: string
}

interface ApiResponse<T> {
  status: boolean
  data: T
  status_code: number
  message: string
}

export const loginUser = async (
  credentials: LoginRequest,
): Promise<LoginResponse> => {
  const response = await api.post<ApiResponse<LoginResponse>>(
    '/auth/login',
    credentials,
  )

  const token = response.data.data.access_token

  localStorage.setItem('access_token', token)

  return response.data.data
}
