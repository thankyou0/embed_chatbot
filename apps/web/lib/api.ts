const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiError {
  detail?: string
  error?: string
  message?: string
}

function getSafeErrorMessage(error: ApiError, status: number): string {
  const fallback = "Something went wrong. Please try again."

  if (status >= 500) {
    return error.error || fallback
  }

  return error.detail || error.error || error.message || fallback
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: 'An error occurred',
    }))
    const message = getSafeErrorMessage(error, response.status)
    throw new Error(message)
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T
  }

  return response.json()
}

export async function apiRequestWithAuth<T>(
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  return apiRequest<T>(endpoint, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })
}

