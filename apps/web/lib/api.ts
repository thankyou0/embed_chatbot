const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ApiError {
  detail?: string;
  error?: string;
  message?: string;
}

/** Error class that carries the HTTP status code */
export class ApiHttpError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiHttpError";
    this.status = status;
  }
}

function getSafeErrorMessage(error: ApiError, status: number): string {
  const fallback = "Something went wrong. Please try again.";

  if (status >= 500) {
    return error.error || fallback;
  }

  return error.detail || error.error || error.message || fallback;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      detail: "An error occurred",
    }));
    const message = getSafeErrorMessage(error, response.status);
    // Log 5xx errors to console (Sentry can be re-added later)
    if (response.status >= 500) {
      console.error(`[API ${response.status}] ${endpoint}:`, message);
    }
    throw new ApiHttpError(message, response.status);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export async function apiRequestWithAuth<T>(
  endpoint: string,
  token: string,
  options: RequestInit = {},
): Promise<T> {
  try {
    return await apiRequest<T>(endpoint, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...options.headers,
      },
    });
  } catch (error) {
    // On 401, try refreshing the access token and retry once
    if (error instanceof ApiHttpError && error.status === 401) {
      try {
        // Dynamic import to avoid circular dependency (auth.ts imports from api.ts)
        const { refreshAccessToken } = await import("./auth");
        const newToken = await refreshAccessToken();
        return await apiRequest<T>(endpoint, {
          ...options,
          headers: {
            Authorization: `Bearer ${newToken}`,
            ...options.headers,
          },
        });
      } catch {
        // Refresh failed — throw the original 401 error
        throw error;
      }
    }
    throw error;
  }
}
