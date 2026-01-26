/**
 * Authentication State Manager
 * Manages authentication state to prevent recursive verification calls
 * and maintain consistent authentication status across the application
 */

interface AuthState {
  isAuthenticated: boolean;
  token?: string;
  user?: any;
  verificationInProgress: boolean;
  lastVerificationTime: number | null;
  verificationAttempts: number;
  lastError?: string;
  verificationQueue: Array<() => void>; // Queue for pending operations during verification
}

class AuthStateManager {
  private static instance: AuthStateManager;
  private state: AuthState;
  private readonly maxVerificationAttempts: number;
  private readonly verificationCooldownMs: number;
  private listeners: Array<(state: AuthState) => void> = [];

  private constructor() {
    this.state = {
      isAuthenticated: false,
      verificationInProgress: false,
      lastVerificationTime: null,
      verificationAttempts: 0,
      verificationQueue: []
    };

    // Get environment-specific settings
    this.maxVerificationAttempts = this.getMaxVerificationAttempts();
    this.verificationCooldownMs = this.getVerificationCooldownMs();
  }

  static getInstance(): AuthStateManager {
    if (!AuthStateManager.instance) {
      AuthStateManager.instance = new AuthStateManager();
    }
    return AuthStateManager.instance;
  }

  /**
   * Get max verification attempts based on environment
   */
  private getMaxVerificationAttempts(): number {
    return typeof process !== 'undefined' && process.env?.NODE_ENV === 'development' ? 3 : 5;
  }

  /**
   * Get verification cooldown time based on environment
   */
  private getVerificationCooldownMs(): number {
    return typeof process !== 'undefined' && process.env?.NODE_ENV === 'development' ? 500 : 1000;
  }

  /**
   * Get current authentication state
   */
  getState(): AuthState {
    return { ...this.state }; // Return a copy to prevent external mutations
  }

  /**
   * Set authentication token and update state
   */
  setToken(token: string): void {
    this.state.token = token;
    this.state.isAuthenticated = !!token;
    this.notifyListeners();
  }

  /**
   * Set user information
   */
  setUser(user: any): void {
    this.state.user = user;
    this.notifyListeners();
  }

  /**
   * Clear authentication state
   */
  clearAuth(): void {
    this.state.isAuthenticated = false;
    this.state.token = undefined;
    this.state.user = undefined;
    this.state.lastError = undefined;
    this.state.verificationAttempts = 0;
    this.notifyListeners();
  }

  /**
   * Check if verification is currently in progress
   */
  isVerificationInProgress(): boolean {
    return this.state.verificationInProgress;
  }

  /**
   * Start verification process
   */
  startVerification(): boolean {
    // Check if we've exceeded the maximum attempts
    if (this.state.verificationAttempts >= this.maxVerificationAttempts) {
      const timeSinceLastAttempt = this.state.lastVerificationTime
        ? Date.now() - this.state.lastVerificationTime
        : Infinity;

      // If enough time has passed, reset attempts
      if (timeSinceLastAttempt > this.verificationCooldownMs * 5) {
        this.resetVerificationAttempts();
      } else {
        console.warn(`[AuthStateManager] Maximum verification attempts (${this.maxVerificationAttempts}) reached`);
        return false;
      }
    }

    // Check if verification is already in progress
    if (this.state.verificationInProgress) {
      console.debug('[AuthStateManager] Verification already in progress, queuing request');
      return false;
    }

    this.state.verificationInProgress = true;
    this.state.verificationAttempts += 1;
    this.state.lastVerificationTime = Date.now();
    this.notifyListeners();

    return true;
  }

  /**
   * Complete verification process successfully
   */
  completeVerification(isAuthenticated: boolean, user?: any): void {
    this.state.verificationInProgress = false;
    this.state.isAuthenticated = isAuthenticated;

    if (user) {
      this.state.user = user;
    }

    // Process queued operations
    this.processQueue();

    this.notifyListeners();
  }

  /**
   * Fail verification process
   */
  failVerification(error?: string): void {
    this.state.verificationInProgress = false;
    this.state.lastError = error;

    // Process queued operations even on failure
    this.processQueue();

    this.notifyListeners();
  }

  /**
   * Reset verification attempts
   */
  resetVerificationAttempts(): void {
    this.state.verificationAttempts = 0;
    this.state.lastVerificationTime = null;
    this.state.lastError = undefined;
  }

  /**
   * Add an operation to the queue that will be executed after verification completes
   */
  queueOperation(operation: () => void): void {
    this.state.verificationQueue.push(operation);
  }

  /**
   * Process all queued operations
   */
  private processQueue(): void {
    const queue = [...this.state.verificationQueue];
    this.state.verificationQueue = [];

    queue.forEach(operation => {
      try {
        operation();
      } catch (error) {
        console.error('[AuthStateManager] Error executing queued operation:', error);
      }
    });
  }

  /**
   * Check if we should allow a new verification attempt
   */
  shouldAllowVerification(): boolean {
    if (this.state.verificationInProgress) {
      return false;
    }

    if (this.state.verificationAttempts >= this.maxVerificationAttempts) {
      const timeSinceLastAttempt = this.state.lastVerificationTime
        ? Date.now() - this.state.lastVerificationTime
        : Infinity;

      // Allow retry if cooldown period has passed
      return timeSinceLastAttempt > this.verificationCooldownMs;
    }

    return true;
  }

  /**
   * Check if we're at risk of hitting the verification limit
   */
  isApproachingVerificationLimit(buffer: number = 1): boolean {
    return (this.state.verificationAttempts + buffer) >= this.maxVerificationAttempts;
  }

  /**
   * Get the number of attempts remaining before hitting the limit
   */
  getRemainingAttempts(): number {
    return Math.max(0, this.maxVerificationAttempts - this.state.verificationAttempts);
  }

  /**
   * Check if we've exceeded the verification attempts and are in cooldown
   */
  isInVerificationCooldown(): boolean {
    if (this.state.verificationAttempts < this.maxVerificationAttempts) {
      return false;
    }

    if (!this.state.lastVerificationTime) {
      return false;
    }

    const timeSinceLastAttempt = Date.now() - this.state.lastVerificationTime;
    return timeSinceLastAttempt <= this.verificationCooldownMs;
  }

  /**
   * Get time remaining until cooldown ends (in milliseconds)
   */
  getTimeUntilCooldownEnd(): number | null {
    if (!this.isInVerificationCooldown()) {
      return null;
    }

    if (!this.state.lastVerificationTime) {
      return null;
    }

    const timeSinceLastAttempt = Date.now() - this.state.lastVerificationTime;
    return Math.max(0, this.verificationCooldownMs - timeSinceLastAttempt);
  }

  /**
   * Get verification status information
   */
  getVerificationStatus(): {
    canVerify: boolean;
    isProcessing: boolean;
    attemptsRemaining: number;
    timeUntilRetry: number | null;
  } {
    const canVerify = this.shouldAllowVerification();
    const isProcessing = this.state.verificationInProgress;
    const attemptsRemaining = Math.max(0, this.maxVerificationAttempts - this.state.verificationAttempts);

    let timeUntilRetry: number | null = null;
    if (!canVerify && !isProcessing && this.state.lastVerificationTime) {
      const timePassed = Date.now() - this.state.lastVerificationTime;
      timeUntilRetry = Math.max(0, this.verificationCooldownMs - timePassed);
    }

    return {
      canVerify,
      isProcessing,
      attemptsRemaining,
      timeUntilRetry
    };
  }

  /**
   * Add a listener for state changes
   */
  addListener(listener: (state: AuthState) => void): void {
    this.listeners.push(listener);
  }

  /**
   * Remove a listener
   */
  removeListener(listener: (state: AuthState) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  /**
   * Notify all listeners of a state change
   */
  private notifyListeners(): void {
    this.listeners.forEach(listener => {
      try {
        listener(this.getState());
      } catch (error) {
        console.error('[AuthStateManager] Error notifying listener:', error);
      }
    });
  }

  /**
   * Get authentication token
   */
  getToken(): string | undefined {
    return this.state.token;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return this.state.isAuthenticated;
  }

  /**
   * Get user information
   */
  getUser(): any | undefined {
    return this.state.user;
  }

  /**
   * Get last error
   */
  getLastError(): string | undefined {
    return this.state.lastError;
  }
}

export const authStateManager = AuthStateManager.getInstance();

/**
 * Hook-like function to get current auth state (for use in React components)
 */
export function useAuthState(): AuthState {
  return authStateManager.getState();
}

/**
 * Wrapper function to safely execute authentication verification
 */
export async function withAuthVerification<T>(
  verificationFn: () => Promise<{ isAuthenticated: boolean; user?: any }>,
  onError?: (error: any) => void
): Promise<{ success: boolean; data?: T; error?: any }> {
  if (!authStateManager.shouldAllowVerification()) {
    console.warn('[AuthStateManager] Verification not allowed, too many attempts or already in progress');

    // Add to queue if verification is in progress
    if (authStateManager.isVerificationInProgress()) {
      return new Promise(resolve => {
        authStateManager.queueOperation(async () => {
          try {
            const result = await verificationFn();
            authStateManager.completeVerification(result.isAuthenticated, result.user);
            resolve({ success: true, data: result as any });
          } catch (error) {
            authStateManager.failVerification(error?.message || 'Verification failed');
            if (onError) onError(error);
            resolve({ success: false, error });
          }
        });
      });
    }

    return { success: false, error: 'Verification not allowed' };
  }

  if (!authStateManager.startVerification()) {
    return { success: false, error: 'Failed to start verification' };
  }

  try {
    const result = await verificationFn();
    authStateManager.completeVerification(result.isAuthenticated, result.user);
    return { success: true, data: result as any };
  } catch (error) {
    authStateManager.failVerification(error?.message || 'Verification failed');
    if (onError) onError(error);
    return { success: false, error };
  }
}