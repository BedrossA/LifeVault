/**
 * Unified Zustand store for authentication state management
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '../services/api';
import type { UserCreate, UserLogin, UserResponse, Token } from '../types';

interface AuthState {
  // State
  user: UserResponse | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Primary Actions
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserCreate) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;

  // Utility Actions
  setUser: (user: UserResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // --- Initial State ---
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // --- Primary Actions ---
      login: async (credentials: UserLogin) => {
        const { isLoading } = get();
        if (isLoading) {
          throw new Error('Login already in progress');
          }
  
        set({ isLoading: true, error: null });
        try {
          // 1. Get Tokens from login endpoint
          const tokenData: Token = await apiClient.login(credentials);
          
          // Validate that we received both tokens
          if (!tokenData.access_token) {
            throw new Error('No access token received from server');
          }
          if (!tokenData.refresh_token) {
            throw new Error('No refresh token received from server');
          }
          
          // 2. Store tokens in localStorage FIRST (before making any other API calls)
          // This ensures the interceptor can use them immediately
          // If rememberMe is true, tokens persist longer (handled by backend token expiry)
          localStorage.setItem('access_token', tokenData.access_token);
          localStorage.setItem('refresh_token', tokenData.refresh_token);
          
          // Store rememberMe preference
          if (credentials.rememberMe) {
            localStorage.setItem('remember_me', 'true');
          } else {
            localStorage.removeItem('remember_me');
          }

          // 3. Update Zustand state with tokens
          set({
            accessToken: tokenData.access_token,
            refreshToken: tokenData.refresh_token,
            isAuthenticated: true,
          });

          // 4. Get User Profile (now that tokens are stored, interceptor will add them)
          // If this fails, we still have valid tokens, so don't fail the entire login
          try {
            const user = await apiClient.getCurrentUser();
            // 5. Update state with user info
            set({
              user,
              isLoading: false,
              error: null,
            });
          } catch (userError: any) {
            // If getting user fails, log it but don't fail login
            // The user is still authenticated with valid tokens
            console.warn('Failed to fetch user profile after login:', userError);
            set({
              isLoading: false,
              error: null,
              // Keep tokens and authenticated state
            });
          }
        } catch (error: any) {
          // Clear tokens on error
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
            accessToken: null,
            refreshToken: null,
            user: null,
          });
          throw error;
        }
      },

      register: async (userData: UserCreate) => {
        set({ isLoading: true, error: null });
        try {
          await apiClient.register(userData);
          // Auto-login using the credentials provided during registration
          await get().login({
            username: userData.username,
            password: userData.password,
          });
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        set({ isLoading: true });
        try {
          // Backend logout endpoint requires authentication via Bearer token
          // The access token in the header is automatically added by interceptor
          await apiClient.logout();
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Always clear local storage and state regardless of API success
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          set({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },

      refreshAuth: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().logout();
          return;
        }

        try {
          const tokenData = await apiClient.refreshToken({ refresh_token: refreshToken });
          
          localStorage.setItem('access_token', tokenData.access_token);
          localStorage.setItem('refresh_token', tokenData.refresh_token);

          set({
            accessToken: tokenData.access_token,
            refreshToken: tokenData.refresh_token,
            isAuthenticated: true,
          });
        } catch (error) {
          // If refresh fails (e.g., refresh token expired), force logout
          get().logout();
        }
      },

      // --- Utility Actions ---
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        // Essential state to persist across page reloads
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);