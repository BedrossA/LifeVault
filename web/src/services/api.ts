/**
 * API Client Service - Unified Version
 * Handles all HTTP requests to the LifeVault backend API.
 * * Logic:
 * - Automatically attaches 'access_token' to every request.
 * - Automatically handles 401 Unauthorized by attempting to refresh the token.
 * - Uses URLSearchParams for FastAPI OAuth2 compatibility during login.
 */
import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type { 
  UserCreate, 
  UserLogin, 
  UserResponse, 
  Token, 
  TokenRefresh,
  LoginHistory,
  UserActivity,
  ApiError 
} from '../types';

// Base URL configuration (Vite Proxy for dev, Env variable for production)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    /**
     * Request Interceptor
     * Injects the Bearer token from localStorage into every outgoing request.
     */
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('access_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    /**
     * Response Interceptor
     * Detects 401 errors to trigger an automatic token refresh.
     */
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError<ApiError>) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        // If 401 (Unauthorized) and we haven't tried refreshing yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) throw new Error('No refresh token available');

            // Attempt to get a new access token
            // Use the client instance to ensure proxy and interceptors are used
            const response = await this.client.post<Token>(
              '/auth/refresh',
              { refresh_token: refreshToken }
            );

            const { access_token, refresh_token } = response.data;
            
            // Save new tokens
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Update original request header and retry
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
            }
            return this.client(originalRequest);

          } catch (refreshError) {
            // If refresh fails, clear storage and force login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // --- Auth Endpoints ---

  async register(userData: UserCreate): Promise<UserResponse> {
    const response = await this.client.post<UserResponse>('/auth/register', userData);
    return response.data;
  }

  async login(credentials: UserLogin): Promise<Token> {
    /**
     * NOTE: FastAPI's OAuth2PasswordRequestForm requires 
     * application/x-www-form-urlencoded (FormData), not JSON.
     */
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await this.client.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  }

  async refreshToken(tokenData: TokenRefresh): Promise<Token> {
    const response = await this.client.post<Token>('/auth/refresh', tokenData);
    return response.data;
  }

  async logout(): Promise<void> {
    // Backend logout endpoint requires authentication via Bearer token in header
    // The access token is automatically added by the request interceptor
    await this.client.post('/auth/logout');
  }

  async getCurrentUser(): Promise<UserResponse> {
    const response = await this.client.get<UserResponse>('/auth/me');
    return response.data;
  }

  // --- Analytics & History Endpoints ---

  async getLoginHistory(limit: number = 10): Promise<LoginHistory[]> {
    const response = await this.client.get<LoginHistory[]>(`/auth/history?limit=${limit}`);
    return response.data;
  }

  async getUserActivity(limit: number = 20): Promise<UserActivity[]> {
    const response = await this.client.get<UserActivity[]>(`/auth/activity?limit=${limit}`);
    return response.data;
  }
}

export const apiClient = new ApiClient();