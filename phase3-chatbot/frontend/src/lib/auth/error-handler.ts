/**
 * Error Handler for Authentication Flows
 * Provides centralized error handling for authentication-related operations
 * and prevents error cascades that could lead to infinite loops
 */

export interface AuthError {
  type: 'network' | 'validation' | 'authentication' | 'authorization' | 'timeout' | 'circuit_breaker' | 'unknown';
  message: string;
  code: string;
  timestamp: number;
  details?: any;
  originalError?: Error;
}

export interface ErrorHandlingOptions {
  retryAttempts?: number;
  retryDelay?: number;
  circuitBreakerEnabled?: boolean;
  logErrors?: boolean;
  suppressDuplicateErrors?: boolean;
}

class AuthErrorHandler {
  private static instance: AuthErrorHandler;
  private recentErrors: Map<string, AuthError> = new Map();
  private readonly maxRecentErrors: number = 100;
  private readonly errorSuppressionWindow: number = 5000; // 5 seconds

  private constructor() {}

  static getInstance(): AuthErrorHandler {
    if (!AuthErrorHandler.instance) {
      AuthErrorHandler.instance = new AuthErrorHandler();
    }
    return AuthErrorHandler.instance;
  }

  /**
   * Handle an authentication error with appropriate categorization and response
   */
  handleError(
    error: any,
    operation: string = 'unknown',
    options: ErrorHandlingOptions = {}
  ): AuthError {
    const defaultOptions: Required<ErrorHandlingOptions> = {
      retryAttempts: 0,
      retryDelay: 1000,
      circuitBreakerEnabled: true,
      logErrors: true,
      suppressDuplicateErrors: true
    };

    const opts = { ...defaultOptions, ...options };

    // Categorize the error
    const categorizedError = this.categorizeError(error, operation);

    // Log the error if enabled
    if (opts.logErrors) {
      this.logError(categorizedError);
    }

    // Suppress duplicate errors if enabled
    if (opts.suppressDuplicateErrors) {
      if (this.isDuplicateError(categorizedError)) {
        console.debug(`[AuthErrorHandler] Suppressing duplicate error: ${categorizedError.message}`);
        return categorizedError;
      }
    }

    // Store the error for duplicate checking
    this.storeError(categorizedError);

    return categorizedError;
  }

  /**
   * Categorize an error based on its characteristics
   */
  private categorizeError(error: any, operation: string): AuthError {
    let errorType: AuthError['type'] = 'unknown';
    let message = 'An unknown error occurred';
    let code = 'UNKNOWN_ERROR';

    // Handle different error types
    if (error instanceof Error) {
      message = error.message;

      // Check for specific error patterns
      if (error.message.includes('Network Error') || error.message.includes('Failed to fetch')) {
        errorType = 'network';
        code = 'NETWORK_ERROR';
      } else if (error.message.includes('401') || error.message.toLowerCase().includes('unauthorized')) {
        errorType = 'authorization';
        code = 'UNAUTHORIZED';
      } else if (error.message.includes('403') || error.message.toLowerCase().includes('forbidden')) {
        errorType = 'authorization';
        code = 'FORBIDDEN';
      } else if (error.message.includes('429') || error.message.toLowerCase().includes('too many requests')) {
        errorType = 'authentication';
        code = 'RATE_LIMITED';
      } else if (error.message.toLowerCase().includes('timeout') || error.message.includes('ECONNABORTED')) {
        errorType = 'timeout';
        code = 'REQUEST_TIMEOUT';
      } else if (error.message.toLowerCase().includes('circuit breaker') || error.message.toLowerCase().includes('open')) {
        errorType = 'circuit_breaker';
        code = 'CIRCUIT_BREAKER_OPEN';
      } else if (error.message.toLowerCase().includes('invalid') || error.message.toLowerCase().includes('malformed')) {
        errorType = 'validation';
        code = 'VALIDATION_ERROR';
      } else if (error.message.toLowerCase().includes('token') || error.message.toLowerCase().includes('auth')) {
        errorType = 'authentication';
        code = 'AUTH_ERROR';
      }
    } else if (typeof error === 'string') {
      message = error;
      if (error.toLowerCase().includes('network')) {
        errorType = 'network';
        code = 'NETWORK_ERROR';
      } else if (error.toLowerCase().includes('auth') || error.toLowerCase().includes('token')) {
        errorType = 'authentication';
        code = 'AUTH_ERROR';
      }
    } else if (error && typeof error === 'object') {
      // Handle response-like objects
      if (error.status) {
        if (error.status === 401) {
          errorType = 'authorization';
          code = 'UNAUTHORIZED';
          message = error.message || 'Unauthorized access';
        } else if (error.status === 403) {
          errorType = 'authorization';
          code = 'FORBIDDEN';
          message = error.message || 'Forbidden access';
        } else if (error.status === 429) {
          errorType = 'authentication';
          code = 'RATE_LIMITED';
          message = error.message || 'Rate limited';
        } else if (error.status >= 500) {
          errorType = 'network';
          code = 'SERVER_ERROR';
          message = error.message || `Server error: ${error.status}`;
        }
      }
    }

    // Create a hash for duplicate detection
    const errorHash = this.getErrorHash(message, errorType, operation);

    return {
      type: errorType,
      message,
      code,
      timestamp: Date.now(),
      details: error,
      originalError: error instanceof Error ? error : undefined
    };
  }

  /**
   * Log error to console and any error tracking service
   */
  private logError(authError: AuthError): void {
    const errorLevel = this.getErrorLogLevel(authError.type);

    switch (errorLevel) {
      case 'error':
        console.error(`[AUTH-${authError.code}] ${authError.message}`, {
          type: authError.type,
          timestamp: new Date(authError.timestamp).toISOString(),
          stack: authError.originalError?.stack
        });
        break;
      case 'warn':
        console.warn(`[AUTH-${authError.code}] ${authError.message}`, {
          type: authError.type,
          timestamp: new Date(authError.timestamp).toISOString()
        });
        break;
      case 'info':
        console.info(`[AUTH-${authError.code}] ${authError.message}`, {
          type: authError.type,
          timestamp: new Date(authError.timestamp).toISOString()
        });
        break;
    }
  }

  /**
   * Get appropriate log level for error type
   */
  private getErrorLogLevel(errorType: AuthError['type']): 'error' | 'warn' | 'info' {
    switch (errorType) {
      case 'network':
      case 'circuit_breaker':
        return 'error';
      case 'authentication':
      case 'authorization':
        return 'warn'; // These are often expected in auth flows
      case 'timeout':
      case 'validation':
        return 'info';
      case 'unknown':
      default:
        return 'error';
    }
  }

  /**
   * Check if this error is a duplicate of a recent error
   */
  private isDuplicateError(authError: AuthError): boolean {
    const errorHash = this.getErrorHash(authError.message, authError.type, 'unknown');
    const recentError = this.recentErrors.get(errorHash);

    if (recentError) {
      const timeDiff = Date.now() - recentError.timestamp;
      return timeDiff < this.errorSuppressionWindow;
    }

    return false;
  }

  /**
   * Generate a hash for the error to identify duplicates
   */
  private getErrorHash(message: string, type: string, operation: string): string {
    // Simple hash function to identify similar errors
    const combined = `${message.toLowerCase().trim()}|${type}|${operation}`;
    let hash = 0;

    for (let i = 0; i < combined.length; i++) {
      const char = combined.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash |= 0; // Convert to 32-bit integer
    }

    return hash.toString();
  }

  /**
   * Store error for duplicate checking
   */
  private storeError(authError: AuthError): void {
    const errorHash = this.getErrorHash(authError.message, authError.type, 'unknown');
    this.recentErrors.set(errorHash, authError);

    // Clean up old errors to prevent memory leaks
    if (this.recentErrors.size > this.maxRecentErrors) {
      // Remove the oldest entries
      const entries = Array.from(this.recentErrors.entries());
      const toRemove = entries.slice(0, Math.floor(this.maxRecentErrors / 2));

      toRemove.forEach(([key]) => {
        this.recentErrors.delete(key);
      });
    }
  }

  /**
   * Handle authentication verification errors specifically
   */
  handleVerificationError(error: any, context: string = 'verification'): AuthError {
    const authError = this.handleError(error, `auth_${context}`, {
      logErrors: true,
      suppressDuplicateErrors: true
    });

    // Special handling for verification-specific errors
    if (authError.type === 'circuit_breaker') {
      console.warn('[AuthErrorHandler] Circuit breaker triggered during authentication verification');
    } else if (authError.type === 'authorization' && authError.code === 'UNAUTHORIZED') {
      console.debug('[AuthErrorHandler] Unauthorized during verification, may be expected');
    }

    return authError;
  }

  /**
   * Handle network errors with retry logic
   */
  async handleNetworkError(
    operation: () => Promise<any>,
    options: ErrorHandlingOptions = {}
  ): Promise<any> {
    const opts = {
      retryAttempts: 2,
      retryDelay: 1000,
      ...options
    };

    let lastError: any;

    for (let attempt = 0; attempt <= opts.retryAttempts; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;

        // If this is a network error and we have retries left
        if (this.categorizeError(error, 'network').type === 'network' && attempt < opts.retryAttempts) {
          console.debug(`[AuthErrorHandler] Network error, retrying in ${opts.retryDelay}ms (attempt ${attempt + 1}/${opts.retryAttempts + 1})`);

          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, opts.retryDelay));

          // Exponential backoff for subsequent retries
          opts.retryDelay *= 2;
        } else {
          // Not a network error or no more retries, break out
          break;
        }
      }
    }

    // If we exhausted all retries, throw the last error
    throw lastError;
  }

  /**
   * Get statistics about recent errors
   */
  getErrorStats(): {
    totalErrors: number;
    errorTypes: Record<string, number>;
    recentErrors: AuthError[];
  } {
    const errorTypes: Record<string, number> = {};
    const recentErrors = Array.from(this.recentErrors.values()).sort((a, b) => b.timestamp - a.timestamp);

    recentErrors.forEach(error => {
      errorTypes[error.type] = (errorTypes[error.type] || 0) + 1;
    });

    return {
      totalErrors: this.recentErrors.size,
      errorTypes,
      recentErrors: recentErrors.slice(0, 10) // Last 10 errors
    };
  }

  /**
   * Clear recent errors (for testing or memory management)
   */
  clearErrors(): void {
    this.recentErrors.clear();
  }
}

export const authErrorHandler = AuthErrorHandler.getInstance();

/**
 * Convenience function to handle authentication errors with default options
 */
export function handleAuthError(error: any, operation: string = 'unknown'): AuthError {
  return authErrorHandler.handleError(error, operation);
}

/**
 * Convenience function to handle authentication verification errors
 */
export function handleVerificationError(error: any, context: string = 'verification'): AuthError {
  return authErrorHandler.handleVerificationError(error, context);
}

/**
 * Execute an operation with network error handling and retry logic
 */
export async function withNetworkRetry<T>(
  operation: () => Promise<T>,
  options: ErrorHandlingOptions = {}
): Promise<T> {
  return authErrorHandler.handleNetworkError(operation, options) as Promise<T>;
}