/**
 * Circuit Breaker Pattern Implementation for Authentication Verification
 * Prevents repeated failures and potential infinite loops in authentication flows
 */

export enum CircuitState {
  CLOSED = 'CLOSED',    // Normal operation, requests pass through
  OPEN = 'OPEN',        // Tripped, requests fail fast
  HALF_OPEN = 'HALF_OPEN' // Testing if service recovered
}

interface CircuitBreakerOptions {
  failureThreshold: number;    // Number of failures before opening circuit
  timeoutMs: number;          // Time to wait before half-open state
  successThreshold: number;   // Success count needed to close circuit
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private lastFailureTime: number | null = null;
  private successCount: number = 0;

  private readonly failureThreshold: number;
  private readonly timeoutMs: number;
  private readonly successThreshold: number;

  private listeners: Array<(state: CircuitState) => void> = [];

  constructor(options: Partial<CircuitBreakerOptions> = {}) {
    this.failureThreshold = options.failureThreshold ?? 5;
    this.timeoutMs = options.timeoutMs ?? 60000; // 1 minute
    this.successThreshold = options.successThreshold ?? 3;
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check if circuit should transition from OPEN to HALF_OPEN
    this.checkTimeout();

    if (this.state === CircuitState.OPEN) {
      throw new Error('Circuit breaker is OPEN - request blocked');
    }

    try {
      const result = await fn();

      // Record success
      this.onSuccess();
      return result;
    } catch (error) {
      // Record failure
      this.onFailure();
      throw error;
    }
  }

  /**
   * Record a successful operation
   */
  private onSuccess(): void {
    this.successCount++;

    if (this.state === CircuitState.HALF_OPEN) {
      // If we're in half-open state and had enough successes, close the circuit
      if (this.successCount >= this.successThreshold) {
        this.close();
      }
    } else if (this.state === CircuitState.CLOSED) {
      // In closed state, just reset failure count
      this.failureCount = 0;
    }
  }

  /**
   * Record a failed operation
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    // If we've exceeded the failure threshold, open the circuit
    if (this.failureCount >= this.failureThreshold) {
      this.open();
    }
  }

  /**
   * Open the circuit (fail fast)
   */
  private open(): void {
    if (this.state !== CircuitState.OPEN) {
      this.state = CircuitState.OPEN;
      this.notifyListeners(CircuitState.OPEN);
    }
  }

  /**
   * Close the circuit (return to normal operation)
   */
  private close(): void {
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = null;
    this.notifyListeners(CircuitState.CLOSED);
  }

  /**
   * Transition to half-open state to test recovery
   */
  private halfOpen(): void {
    if (this.state !== CircuitState.HALF_OPEN) {
      this.state = CircuitState.HALF_OPEN;
      this.successCount = 0;
      this.notifyListeners(CircuitState.HALF_OPEN);
    }
  }

  /**
   * Check if enough time has passed to transition from OPEN to HALF_OPEN
   */
  private checkTimeout(): void {
    if (
      this.state === CircuitState.OPEN &&
      this.lastFailureTime !== null &&
      Date.now() - this.lastFailureTime >= this.timeoutMs
    ) {
      this.halfOpen();
    }
  }

  /**
   * Get current state of the circuit breaker
   */
  getState(): CircuitState {
    this.checkTimeout(); // Update state if needed
    return this.state;
  }

  /**
   * Get statistics about the circuit breaker
   */
  getStats(): {
    state: CircuitState;
    failureCount: number;
    successCount: number;
    lastFailureTime: number | null;
  } {
    return {
      state: this.getState(),
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime
    };
  }

  /**
   * Reset the circuit breaker to closed state
   */
  reset(): void {
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.lastFailureTime = null;
    this.notifyListeners(CircuitState.CLOSED);
  }

  /**
   * Add a listener for state changes
   */
  addListener(listener: (state: CircuitState) => void): void {
    this.listeners.push(listener);
  }

  /**
   * Remove a listener
   */
  removeListener(listener: (state: CircuitState) => void): void {
    this.listeners = this.listeners.filter(l => l !== listener);
  }

  /**
   * Notify all listeners of a state change
   */
  private notifyListeners(newState: CircuitState): void {
    this.listeners.forEach(listener => listener(newState));
  }
}

// Singleton instance for authentication circuit breaker
class AuthCircuitBreaker {
  private static instance: CircuitBreaker;

  static getInstance(): CircuitBreaker {
    if (!AuthCircuitBreaker.instance) {
      AuthCircuitBreaker.instance = new CircuitBreaker({
        failureThreshold: 3,    // Lower threshold for auth to catch loops quickly
        timeoutMs: 30000,       // 30 seconds before retrying
        successThreshold: 1     // Only need 1 success to close circuit
      });
    }
    return AuthCircuitBreaker.instance;
  }
}

// Convenience function to wrap authentication verification with circuit breaker
export async function withAuthCircuitBreaker<T>(fn: () => Promise<T>): Promise<T> {
  const circuitBreaker = AuthCircuitBreaker.getInstance();
  return circuitBreaker.execute(fn);
}

// Export the main classes and types
export { CircuitBreaker, AuthCircuitBreaker };