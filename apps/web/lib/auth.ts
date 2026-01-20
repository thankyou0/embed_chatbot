import Cookies from "js-cookie";
import { apiRequest, apiRequestWithAuth } from "./api";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";

export interface User {
  id: number;
  tenant_id: number;
  email: string;
  username: string;
  name?: string;
  role: "admin" | "user";
  is_active: boolean;
  must_change_password: boolean;
  password_expires_at: string | null;
  created_at: string;
}

export interface Tenant {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  tenant: Tenant;
}

export interface MeResponse {
  user: User;
  tenant: Tenant;
}

export interface SignupData {
  tenant_name: string;
  email: string;
  username: string;
  password: string;
  name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
}

export interface ChangePasswordResponse {
  message: string;
  user: User;
  tenant: Tenant | null;
}

export interface ForgotPasswordData {
  email: string;
}

export interface ForgotPasswordResponse {
  message: string;
}

export interface ResetPasswordData {
  token: string;
  new_password: string;
}

export interface ResetPasswordResponse {
  message: string;
}

export function setTokens(accessToken: string, refreshToken: string) {
  Cookies.set(ACCESS_TOKEN_KEY, accessToken, { expires: 1 / 96 }); // 15 minutes
  Cookies.set(REFRESH_TOKEN_KEY, refreshToken, { expires: 7 });
}

export function getAccessToken(): string | undefined {
  return Cookies.get(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(REFRESH_TOKEN_KEY);
}

export function clearTokens() {
  Cookies.remove(ACCESS_TOKEN_KEY);
  Cookies.remove(REFRESH_TOKEN_KEY);
}

export async function signup(data: SignupData): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify(data),
  });
  setTokens(response.access_token, response.refresh_token);
  return response;
}

export async function login(data: LoginData): Promise<AuthResponse> {
  const response = await apiRequest<AuthResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
  setTokens(response.access_token, response.refresh_token);
  return response;
}

export async function refreshAccessToken(): Promise<string> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }

  const response = await apiRequest<{ access_token: string }>(
    "/api/v1/auth/refresh",
    {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    },
  );

  Cookies.set(ACCESS_TOKEN_KEY, response.access_token, { expires: 1 / 96 });
  return response.access_token;
}

export async function getMe(): Promise<MeResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("No access token available");
  }

  try {
    return await apiRequestWithAuth<MeResponse>("/api/v1/auth/me", token);
  } catch (error) {
    // Try to refresh token if access token expired
    if (error instanceof Error && error.message.includes("401")) {
      const newToken = await refreshAccessToken();
      return await apiRequestWithAuth<MeResponse>("/api/v1/auth/me", newToken);
    }
    throw error;
  }
}

export async function changePassword(
  data: ChangePasswordData,
): Promise<ChangePasswordResponse> {
  const token = getAccessToken();
  if (!token) {
    throw new Error("No access token available");
  }

  const response = await apiRequestWithAuth<ChangePasswordResponse>(
    "/api/v1/auth/change-password",
    token,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
  return response;
}

export async function forgotPassword(
  data: ForgotPasswordData,
): Promise<ForgotPasswordResponse> {
  const response = await apiRequest<ForgotPasswordResponse>(
    "/api/v1/auth/forgot-password",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
  return response;
}

export async function resetPassword(
  data: ResetPasswordData,
): Promise<ResetPasswordResponse> {
  const response = await apiRequest<ResetPasswordResponse>(
    "/api/v1/auth/reset-password",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
  );
  return response;
}

export function logout() {
  clearTokens();
}
