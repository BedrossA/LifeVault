/**
 * Type definitions matching backend schemas
 */

export interface UserBase {
  email: string;
  username: string;
  full_name?: string | null;
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserResponse extends UserBase {
  id: number;
  uuid: string;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  created_at: string;
  last_login?: string | null;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenRefresh {
  refresh_token: string;
}

export interface LoginHistory {
  timestamp: string;
  ip_address: string;
  user_agent?: string;
  success: boolean;
}

export interface UserActivity {
  timestamp: string;
  action: string;
  category: string;
  ip_address?: string;
  metadata?: Record<string, unknown>;
}

export interface ApiError {
  detail: string;
  message?: string;
}

export interface AuthState {
  user: UserResponse | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

