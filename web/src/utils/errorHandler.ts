/**
 * Error Handling Utilities
 * Centralized error handling and formatting
 */
import axios, { AxiosError } from 'axios';

export interface ApiErrorResponse {
  detail?: string;
  message?: string;
  errors?: Record<string, string[]>;
  status_code?: number;
}

/**
 * Extract a user-friendly error message from various error types
 */
export function extractErrorMessage(error: unknown): string {
  // Axios errors
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiErrorResponse>;
    
    // Try to get error from response data
    if (axiosError.response?.data) {
      const data = axiosError.response.data;
      
      // Check for detail field (FastAPI default)
      if (data.detail) {
        return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
      
      // Check for message field
      if (data.message) {
        return data.message;
      }
      
      // Check for validation errors
      if (data.errors) {
        const errorMessages = Object.entries(data.errors)
          .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
          .join('; ');
        return errorMessages || 'Validation error occurred';
      }
    }
    
    // Network errors
    if (axiosError.code === 'ERR_NETWORK') {
      return 'Network error. Please check your internet connection.';
    }
    
    if (axiosError.code === 'ECONNABORTED') {
      return 'Request timeout. Please try again.';
    }
    
    // Status-based messages
    if (axiosError.response?.status) {
      const status = axiosError.response.status;
      const statusMessages: Record<number, string> = {
        400: 'Bad request. Please check your input.',
        401: 'Unauthorized. Please log in again.',
        403: 'Access denied. You do not have permission to perform this action.',
        404: 'Resource not found.',
        409: 'Conflict. The resource already exists or is in use.',
        422: 'Validation error. Please check your input.',
        429: 'Too many requests. Please slow down and try again later.',
        500: 'Server error. Please try again later.',
        502: 'Bad gateway. The server is temporarily unavailable.',
        503: 'Service unavailable. Please try again later.',
      };
      
      if (statusMessages[status]) {
        return statusMessages[status];
      }
    }
    
    // Fallback to error message
    return axiosError.message || 'An error occurred';
  }
  
  // Standard Error objects
  if (error instanceof Error) {
    return error.message;
  }
  
  // String errors
  if (typeof error === 'string') {
    return error;
  }
  
  // Unknown error types
  return 'An unexpected error occurred';
}

/**
 * Log error to console (in development) and error reporting service (in production)
 */
export function logError(error: unknown, context?: string) {
  const message = extractErrorMessage(error);
  const errorContext = context ? `[${context}]` : '';
  
  console.error(`${errorContext} Error:`, error);
  
  // In production, send to error reporting service
  if (import.meta.env.PROD) {
    // Example: Sentry, LogRocket, etc.
    // Sentry.captureException(error, { tags: { context } });
  }
  
  return message;
}

/**
 * Check if error is a specific type
 */
export function isNetworkError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.code === 'ERR_NETWORK' || !error.response;
  }
  return false;
}

export function isAuthenticationError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 401;
  }
  return false;
}

export function isValidationError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 422 || error.response?.status === 400;
  }
  return false;
}

export function isServerError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    return status ? status >= 500 : false;
  }
  return false;
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
    backoffFactor?: number;
    shouldRetry?: (error: unknown) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    shouldRetry = (error) => isNetworkError(error) || isServerError(error),
  } = options;

  let lastError: unknown;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry if it's the last attempt or if we shouldn't retry this error
      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }
      
      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, delay));
      
      // Increase delay for next attempt
      delay = Math.min(delay * backoffFactor, maxDelay);
    }
  }

  throw lastError;
}

/**
 * Create a safe async handler that catches and handles errors
 */
export function createSafeHandler<T extends any[], R>(
  handler: (...args: T) => Promise<R>,
  options: {
    onError?: (error: unknown) => void;
    context?: string;
    showNotification?: boolean;
  } = {}
) {
  return async (...args: T): Promise<R | undefined> => {
    try {
      return await handler(...args);
    } catch (error) {
      const message = logError(error, options.context);
      
      if (options.showNotification) {
        // Show error notification to user
        // This would integrate with your notification system
        console.error('Show notification:', message);
      }
      
      options.onError?.(error);
      
      return undefined;
    }
  };
}

/**
 * Validation helpers
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export function validateEmail(email: string): void {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    throw new ValidationError('Invalid email format', 'email');
  }
}

export function validatePassword(password: string): void {
  if (password.length < 8) {
    throw new ValidationError('Password must be at least 8 characters long', 'password');
  }
  
  if (!/[A-Z]/.test(password)) {
    throw new ValidationError('Password must contain at least one uppercase letter', 'password');
  }
  
  if (!/[a-z]/.test(password)) {
    throw new ValidationError('Password must contain at least one lowercase letter', 'password');
  }
  
  if (!/[0-9]/.test(password)) {
    throw new ValidationError('Password must contain at least one number', 'password');
  }
  
  if (!/[^A-Za-z0-9]/.test(password)) {
    throw new ValidationError('Password must contain at least one special character', 'password');
  }
}

export function validateUsername(username: string): void {
  if (username.length < 3) {
    throw new ValidationError('Username must be at least 3 characters long', 'username');
  }
  
  if (username.length > 50) {
    throw new ValidationError('Username must be less than 50 characters', 'username');
  }
  
  if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
    throw new ValidationError(
      'Username can only contain letters, numbers, underscores, and hyphens',
      'username'
    );
  }
}

/**
 * Format error for display in UI
 */
export interface FormattedError {
  title: string;
  message: string;
  type: 'error' | 'warning' | 'info';
  canRetry: boolean;
}

export function formatErrorForDisplay(error: unknown): FormattedError {
  if (isNetworkError(error)) {
    return {
      title: 'Connection Error',
      message: 'Unable to connect to the server. Please check your internet connection.',
      type: 'error',
      canRetry: true,
    };
  }
  
  if (isAuthenticationError(error)) {
    return {
      title: 'Authentication Required',
      message: 'Your session has expired. Please log in again.',
      type: 'warning',
      canRetry: false,
    };
  }
  
  if (isValidationError(error)) {
    return {
      title: 'Validation Error',
      message: extractErrorMessage(error),
      type: 'warning',
      canRetry: false,
    };
  }
  
  if (isServerError(error)) {
    return {
      title: 'Server Error',
      message: 'The server encountered an error. Please try again later.',
      type: 'error',
      canRetry: true,
    };
  }
  
  return {
    title: 'Error',
    message: extractErrorMessage(error),
    type: 'error',
    canRetry: false,
  };
}