/**
 * Client-Side Authentication Utilities
 * Handles authentication operations on the client-side with respect to verification limits
 */

import { verifyAuthentication, getVerificationState, useVerificationStatus } from './verification';
import { authStateManager } from './state-manager';
import { authLogger, logAuthVerification } from './logging';
import { isDevMode, getMaxVerificationAttempts, getVerificationRetryDelay } from './config';
import { originTracker } from './origin-tracker';
import { depthTracker, trackVerificationDepth, getCurrentVerificationDepth, isVerificationDepthLimitExceeded } from './depth-tracker';
import { handleAuthError } from './error-handler';
import { addVerificationPattern, isVerificationFlowNormal } from './analyzer';
import { trackAuthRequest } from './request-tracker';

export interface ClientAuthOptions {
  forceRefresh?: boolean;
  includeUserDetails?: boolean;
  timeout?: number;
  maxRetries?: number;
  respectLimits?: boolean; // Whether to respect verification limits
}

export interface AuthResult {
  isAuthenticated: boolean;
  user?: any;
  error?: string;
  retryAfter?: number; // Time to wait before next attempt (in ms)
}

class ClientAuthService {
  private static instance: ClientAuthService;

  private constructor() {}

  static getInstance(): ClientAuthService {
    if (!ClientAuthService.instance) {
      ClientAuthService.instance = new ClientAuthService();
    }
    return ClientAuthService.instance;
  }

  /**
   * Authenticate the user with respect to verification limits
   */
  async authenticate(options: ClientAuthOptions = {}): Promise<AuthResult> {
    const {
      forceRefresh = false,
      includeUserDetails = true,
      timeout = 10000,
      maxRetries = 0,
      respectLimits = true
    } = options;

    // Log the authentication attempt
    const requestStart = Date.now();
    const requestId = trackAuthRequest(
      '/api/auth/verify',
      'GET',
      'Client-side authentication attempt',
      { context: 'client-auth-service' }
    );

    authLogger.info('Client authentication initiated', {
      forceRefresh,
      includeUserDetails,
      respectLimits,
      requestId
    });

    // Check depth limit first
    if (respectLimits && isVerificationDepthLimitExceeded()) {
      authLogger.error('Authentication blocked: Depth limit exceeded', {
        currentDepth: getCurrentVerificationDepth(),
        requestId
      });

      return {
        isAuthenticated: false,
        error: 'Authentication depth limit exceeded - possible infinite recursion',
        retryAfter: getVerificationRetryDelay() * 5 // Wait longer before retry
      };
    }

    // Check verification limits if respecting limits
    if (respectLimits) {
      const verificationStatus = authStateManager.getVerificationStatus();

      // Check if we're in verification cooldown
      if (authStateManager.isInVerificationCooldown()) {
        const timeUntilRetry = authStateManager.getTimeUntilCooldownEnd();
        authLogger.warn('Authentication blocked: In verification cooldown', {
          timeUntilRetry,
          requestId
        });

        return {
          isAuthenticated: authStateManager.isAuthenticated(),
          user: authStateManager.getUser(),
          error: 'Verification rate limited - in cooldown period',
          retryAfter: timeUntilRetry || getVerificationRetryDelay()
        };
      }

      // Check if we're approaching the verification limit
      if (authStateManager.isApproachingVerificationLimit()) {
        const remaining = authStateManager.getRemainingAttempts();
        authLogger.warn('Approaching verification limit', {
          remaining,
          requestId
        });

        if (remaining <= 0) {
          return {
            isAuthenticated: authStateManager.isAuthenticated(),
            user: authStateManager.getUser(),
            error: 'Maximum verification attempts reached',
            retryAfter: getVerificationRetryDelay()
          };
        }
      }
    }

    // Check for potential loops before proceeding
    if (originTracker.detectRecursiveLoops(5000, 3)) {
      authLogger.error('Potential authentication loop detected', { requestId });

      return {
        isAuthenticated: false,
        error: 'Potential authentication loop detected',
        retryAfter: getVerificationRetryDelay() * 3 // Wait longer before retry
      };
    }

    // Check if verification flow is normal
    if (!isVerificationFlowNormal()) {
      authLogger.warn('Authentication flow is not normal, proceeding with caution', { requestId });
    }

    try {
      // Track verification depth
      const depthInfo = trackVerificationDepth(
        '/api/auth/verify',
        'GET',
        'Client authentication verification',
        'client',
        requestId
      );

      if (depthInfo.exceeded) {
        authLogger.error('Depth limit exceeded during authentication', {
          depth: depthInfo.depth,
          requestId
        });

        return {
          isAuthenticated: false,
          error: 'Authentication depth limit exceeded',
          retryAfter: getVerificationRetryDelay() * 5
        };
      }

      // Record the verification attempt
      const verificationId = originTracker.recordVerification(
        'client',
        '/api/auth/verify',
        'GET',
        `Client authentication attempt (depth: ${depthInfo.depth})`,
        requestId
      );

      // Add to verification pattern analysis
      addVerificationPattern(
        'client',
        '/api/auth/verify',
        'GET',
        false, // Initially mark as not successful
        `Client auth attempt`,
        requestStart
      );

      // Perform the actual authentication verification
      const result = await verifyAuthentication({
        forceRefresh,
        timeout,
        maxRetries,
        includeUserDetails
      });

      // Update the verification pattern with success status
      // Note: In the actual implementation, we'd update this after the fact
      // For now, we'll add a new pattern with the result

      // Log the result
      if (result.error) {
        authLogger.warn('Client authentication failed', {
          error: result.error,
          requestId,
          depth: depthInfo.depth
        });

        // Add failed verification pattern
        addVerificationPattern(
          'client',
          '/api/auth/verify',
          'GET',
          false,
          `Client auth failed: ${result.error}`,
          requestStart
        );
      } else {
        authLogger.info('Client authentication successful', {
          userId: result.user?.id,
          requestId,
          depth: depthInfo.depth
        });

        // Add successful verification pattern
        addVerificationPattern(
          'client',
          '/api/auth/verify',
          'GET',
          true,
          `Client auth succeeded`,
          requestStart
        );
      }

      return {
        ...result,
        retryAfter: undefined // Successful auth doesn't require retry delay
      };

    } catch (error) {
      const authError = handleAuthError(error, 'client-authentication');

      authLogger.error('Client authentication error', {
        error: authError.message,
        code: authError.code,
        type: authError.type,
        requestId
      });

      // Add failed verification pattern
      addVerificationPattern(
        'client',
        '/api/auth/verify',
        'GET',
        false,
        `Client auth error: ${authError.message}`,
        requestStart
      );

      return {
        isAuthenticated: false,
        error: authError.message,
        retryAfter: getVerificationRetryDelay()
      };
    }
  }

  /**
   * Check if authentication is allowed based on limits
   */
  canAuthenticate(): boolean {
    if (!authStateManager.shouldAllowVerification()) {
      return false;
    }

    if (isVerificationDepthLimitExceeded()) {
      return false;
    }

    return true;
  }

  /**
   * Get the time until authentication can be attempted again
   */
  getTimeUntilAuthAllowed(): number | null {
    if (authStateManager.isInVerificationCooldown()) {
      return authStateManager.getTimeUntilCooldownEnd();
    }

    return null;
  }

  /**
   * Get authentication status with limit information
   */
  getAuthStatus() {
    const verificationStatus = authStateManager.getVerificationStatus();
    const depthStatus = depthTracker.getSummary();
    const originStats = originTracker.getOriginStats();

    return {
      isAuthenticated: authStateManager.isAuthenticated(),
      isVerifying: authStateManager.isVerificationInProgress(),
      canAuthenticate: this.canAuthenticate(),
      verificationStatus,
      depthStatus,
      originStats,
      limits: {
        maxAttempts: getMaxVerificationAttempts(),
        currentAttempts: verificationStatus.attemptsRemaining,
        isApproachingLimit: authStateManager.isApproachingVerificationLimit(),
        isDepthLimited: depthStatus.isOverLimit,
        isApproachingDepthLimit: depthStatus.approachingLimit
      }
    };
  }

  /**
   * Refresh authentication token if needed
   */
  async refreshTokenIfNeeded(): Promise<AuthResult> {
    const status = this.getAuthStatus();

    // If we're not authenticated, we can't refresh
    if (!status.isAuthenticated) {
      return {
        isAuthenticated: false,
        error: 'Not authenticated, cannot refresh token'
      };
    }

    // Check if we should refresh based on token expiration logic
    // For simplicity, we'll just verify the current authentication
    return this.authenticate({ forceRefresh: true });
  }

  /**
   * Logout and clear authentication state
   */
  logout(): void {
    authLogger.info('Client logout initiated');

    // Clear auth state
    authStateManager.clearAuth();

    // Clear token from localStorage if present
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }

    // Reset depth tracker
    depthTracker.reset();

    // Clear origin tracker records
    originTracker.clearRecords();

    authLogger.info('Client logout completed');
  }

  /**
   * Get the current user information
   */
  getCurrentUser() {
    return authStateManager.getUser();
  }

  /**
   * Check if the user is authenticated
   */
  isAuthenticated(): boolean {
    return authStateManager.isAuthenticated();
  }

  /**
   * Wait for authentication to be allowed if currently rate-limited
   */
  async waitForAuthAllowed(): Promise<void> {
    return new Promise((resolve) => {
      const checkAuthAllowed = () => {
        if (this.canAuthenticate()) {
          resolve();
          return;
        }

        const timeUntilAllowed = this.getTimeUntilAuthAllowed();
        const delay = timeUntilAllowed ? Math.min(timeUntilAllowed, 1000) : 1000;

        setTimeout(checkAuthAllowed, delay);
      };

      checkAuthAllowed();
    });
  }
}

export const clientAuthService = ClientAuthService.getInstance();

/**
 * Convenience function to authenticate with respect to limits
 */
export async function authenticateClient(options?: ClientAuthOptions): Promise<AuthResult> {
  return clientAuthService.authenticate(options);
}

/**
 * Check if authentication is allowed
 */
export function canAuthenticate(): boolean {
  return clientAuthService.canAuthenticate();
}

/**
 * Get authentication status with limit information
 */
export function getAuthStatus() {
  return clientAuthService.getAuthStatus();
}

/**
 * Get the time until authentication can be attempted again
 */
export function getTimeUntilAuthAllowed(): number | null {
  return clientAuthService.getTimeUntilAuthAllowed();
}

/**
 * Wait for authentication to be allowed
 */
export async function waitForAuthAllowed(): Promise<void> {
  return clientAuthService.waitForAuthAllowed();
}

/**
 * Refresh token if needed
 */
export async function refreshTokenIfNeeded(): Promise<AuthResult> {
  return clientAuthService.refreshTokenIfNeeded();
}

/**
 * Check if the user is authenticated
 */
export function isAuthenticated(): boolean {
  return clientAuthService.isAuthenticated();
}

/**
 * Get current user
 */
export function getCurrentUser() {
  return clientAuthService.getCurrentUser();
}

/**
 * Perform logout
 */
export function logout(): void {
  return clientAuthService.logout();
}