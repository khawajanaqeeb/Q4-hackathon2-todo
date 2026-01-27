/**
 * Authentication Verification Flow with Circuit Breaker
 * Implements safe authentication verification with protections against infinite loops
 */

import { withAuthCircuitBreaker } from './circuit-breaker';
import { recordAuthVerification, isAuthVerificationLooping, getAuthVerificationLoopStatus } from './origin-tracker';
import { authStateManager, withAuthVerification } from './state-manager';
import { handleVerificationError } from './error-handler';
import { isDevMode, getMaxVerificationAttempts, getVerificationRetryDelay, getVerificationTimeout } from './config';
import { authLogger, logAuthVerification, detectPotentialLoop } from './logging';
import { logMemoryStats } from './memory-monitor';

export interface VerificationResult {
  isAuthenticated: boolean;
  user?: any;
  error?: string;
}

export interface VerificationOptions {
  forceRefresh?: boolean;
  timeout?: number;
  maxRetries?: number;
  includeUserDetails?: boolean;
}

class AuthVerificationService {
  private static instance: AuthVerificationService;

  private constructor() {}

  static getInstance(): AuthVerificationService {
    if (!AuthVerificationService.instance) {
      AuthVerificationService.instance = new AuthVerificationService();
    }
    return AuthVerificationService.instance;
  }

  /**
   * Perform authentication verification with circuit breaker protection
   */
  async verifyAuthentication(options: VerificationOptions = {}): Promise<VerificationResult> {
    const {
      forceRefresh = false,
      timeout = getVerificationTimeout(),
      maxRetries = 0,
      includeUserDetails = true
    } = options;

    // Check if verification is currently in progress
    if (!forceRefresh && authStateManager.isVerificationInProgress()) {
      authLogger.debug('Verification already in progress, skipping duplicate request');
      return {
        isAuthenticated: authStateManager.isAuthenticated(),
        user: authStateManager.getUser()
      };
    }

    // Check if we should allow verification based on state
    const verificationStatus = authStateManager.getVerificationStatus();

    // Don't apply rate limiting if the user is not authenticated (it's a normal state)
    const tokenExists = this.getAuthToken();
    if (!tokenExists && !forceRefresh) {
      authLogger.debug('No token exists, allowing verification attempt for login flow');
      // Continue with verification even if rate limits would normally apply
    } else if (!forceRefresh && !verificationStatus.canVerify) {
      authLogger.warn('Verification not allowed due to too many attempts or ongoing verification', {
        attemptsRemaining: verificationStatus.attemptsRemaining,
        timeUntilRetry: verificationStatus.timeUntilRetry
      });

      return {
        isAuthenticated: authStateManager.isAuthenticated(),
        error: 'Verification rate limited'
      };
    }

    // Check if we're in verification cooldown (only if token exists)
    if (tokenExists && authStateManager.isInVerificationCooldown()) {
      const timeUntilRetry = authStateManager.getTimeUntilCooldownEnd();
      authLogger.warn('Verification is in cooldown period', {
        attemptsRemaining: 0,
        timeUntilRetry: timeUntilRetry ? `${timeUntilRetry}ms` : 'unknown',
        isApproachingLimit: authStateManager.isApproachingVerificationLimit()
      });

      return {
        isAuthenticated: authStateManager.isAuthenticated(),
        error: 'Verification rate limited - in cooldown period'
      };
    }

    // Check if we're approaching the verification limit (only if token exists)
    if (tokenExists && authStateManager.isApproachingVerificationLimit()) {
      const remaining = authStateManager.getRemainingAttempts();
      authLogger.warn('Approaching verification attempt limit', {
        attemptsRemaining: remaining,
        totalAllowed: getMaxVerificationAttempts(),
        isAtRisk: remaining <= 1
      });
    }

    if (!tokenExists && !forceRefresh) {
      // If no token exists, allow verification to confirm unauthenticated state
      authLogger.debug('No token exists, proceeding with verification to confirm state');
    } else if (!forceRefresh && !verificationStatus.canVerify) {
      authLogger.warn('Verification not allowed due to too many attempts or ongoing verification', {
        attemptsRemaining: verificationStatus.attemptsRemaining,
        timeUntilRetry: verificationStatus.timeUntilRetry
      });

      return {
        isAuthenticated: authStateManager.isAuthenticated(),
        error: 'Verification rate limited'
      };
    }

    // Record this verification attempt with origin tracking
    const verificationId = recordAuthVerification(
      '/api/auth/verify',
      'POST',
      'Authentication verification request',
    );

    authLogger.info(`Starting authentication verification (ID: ${verificationId})`, {
      forceRefresh,
      timeout,
      maxRetries,
      verificationId
    });

    // Check for potential loops before proceeding
    if (detectPotentialLoop()) {
      authLogger.error('Potential authentication verification loop detected, aborting');
      return {
        isAuthenticated: false,
        error: 'Potential verification loop detected'
      };
    }

    // Check if there's a detected loop in the origin tracker
    const loopStatus = getAuthVerificationLoopStatus();
    if (loopStatus.isLooping && loopStatus.details) {
      authLogger.error('Authentication verification loop detected by origin tracker', loopStatus.details);
      return {
        isAuthenticated: false,
        error: 'Verification loop detected'
      };
    }

    try {
      // Execute verification with circuit breaker protection
      const result = await withAuthCircuitBreaker(async () => {
        // Log memory stats before verification
        if (isDevMode()) {
          logMemoryStats('Before Auth Verification');
        }

        // Perform the actual verification
        const verificationResult = await this.performVerification(includeUserDetails);

        // Log memory stats after verification
        if (isDevMode()) {
          logMemoryStats('After Auth Verification');
        }

        return verificationResult;
      });

      authLogger.info(`Authentication verification completed successfully (ID: ${verificationId})`, {
        isAuthenticated: result.isAuthenticated,
        userId: result.user?.id,
        verificationId
      });

      // Update auth state
      authStateManager.completeVerification(result.isAuthenticated, result.user);

      return result;
    } catch (error) {
      authLogger.error(`Authentication verification failed (ID: ${verificationId})`, {
        error: error instanceof Error ? error.message : String(error),
        verificationId
      });

      // Handle the error appropriately
      const authError = handleVerificationError(error, 'verification');

      // Update auth state with failure
      authStateManager.failVerification(authError.message);

      return {
        isAuthenticated: false,
        error: authError.message
      };
    }
  }

  /**
   * Perform the actual verification by calling the backend
   */
  private async performVerification(includeUserDetails: boolean): Promise<VerificationResult> {
    // Get the authentication token
    const token = this.getAuthToken();
    if (!token) {
      authLogger.info('No authentication token found, user is not authenticated');
      return { isAuthenticated: false };
    }

    try {
      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), getVerificationTimeout());

      // Prepare request options
      const requestOptions: RequestInit = {
        method: 'GET', // Use GET for the verify endpoint
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        signal: controller.signal
      };

      // Make the verification request to the backend via the proxy
      const response = await fetch('/api/auth/verify', requestOptions);

      clearTimeout(timeoutId);

      if (response.ok) {
        const userData = await response.json();

        authLogger.info('Authentication verification successful', {
          userId: userData.id || userData.user_id,
          includeUserDetails
        });

        return {
          isAuthenticated: true,
          user: includeUserDetails ? userData : undefined
        };
      } else if (response.status === 401) {
        authLogger.warn('Authentication token is invalid or expired');
        return { isAuthenticated: false };
      } else {
        authLogger.error('Authentication verification failed with unexpected status', {
          status: response.status,
          statusText: response.statusText
        });
        return { isAuthenticated: false };
      }
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof Error && error.name === 'AbortError') {
        authLogger.error('Authentication verification timed out');
        throw new Error('Verification timeout');
      }

      authLogger.error('Network error during authentication verification', {
        error: error instanceof Error ? error.message : String(error)
      });

      throw error;
    }
  }

  /**
   * Get authentication token from storage
   */
  private getAuthToken(): string | null {
    if (typeof window === 'undefined') {
      return null; // Server-side, no token available
    }

    // Try to get token from various sources
    const tokenFromLocalStorage = localStorage.getItem('auth_token');
    const tokenFromCookie = this.getTokenFromCookie();

    return tokenFromLocalStorage || tokenFromCookie;
  }

  /**
   * Get token from cookie (client-side only)
   */
  private getTokenFromCookie(): string | null {
    if (typeof document === 'undefined') {
      return null;
    }

    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'auth_token') {
        return value;
      }
    }
    return null;
  }

  /**
   * Check if a token exists in storage
   */
  private tokenExists(): boolean {
    return this.getAuthToken() !== null;
  }

  /**
   * Verify authentication and handle potential loops
   */
  async verifyWithLoopProtection(options: VerificationOptions = {}): Promise<VerificationResult> {
    // First, check if there's a potential loop
    if (isAuthVerificationLooping()) {
      authLogger.error('Potential loop detected, refusing to perform verification');
      return {
        isAuthenticated: false,
        error: 'Potential verification loop detected'
      };
    }

    return this.verifyAuthentication(options);
  }

  /**
   * Get current verification status
   */
  getStatus(): {
    isAuthenticated: boolean;
    isVerifying: boolean;
    canVerify: boolean;
    attemptsRemaining: number;
    lastError?: string;
  } {
    const state = authStateManager.getState();
    const verificationStatus = authStateManager.getVerificationStatus();

    return {
      isAuthenticated: state.isAuthenticated,
      isVerifying: state.verificationInProgress,
      canVerify: verificationStatus.canVerify,
      attemptsRemaining: verificationStatus.attemptsRemaining,
      lastError: state.lastError
    };
  }

  /**
   * Reset verification state (useful for testing or after logout)
   */
  reset(): void {
    authStateManager.clearAuth();
    authLogger.info('Authentication verification state reset');
  }
}

export const authVerificationService = AuthVerificationService.getInstance();

/**
 * Convenience function to verify authentication with circuit breaker protection
 */
export async function verifyAuthentication(options?: VerificationOptions): Promise<VerificationResult> {
  return authVerificationService.verifyWithLoopProtection(options);
}

/**
 * Hook-like function to get verification status
 */
export function useVerificationStatus() {
  return authVerificationService.getStatus();
}

/**
 * Function to check if verification is in progress
 */
export function isVerificationInProgress(): boolean {
  return authStateManager.isVerificationInProgress();
}

/**
 * Function to get current verification state
 */
export function getVerificationState() {
  return authStateManager.getState();
}