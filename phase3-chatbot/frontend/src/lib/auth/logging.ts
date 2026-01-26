/**
 * Diagnostic logging infrastructure for authentication verification flow
 * Helps identify request origins and detect potential loops
 */

interface LogEntry {
  timestamp: Date;
  level: 'info' | 'warn' | 'error' | 'debug';
  message: string;
  context?: Record<string, any>;
}

class AuthLogger {
  private static instance: AuthLogger;
  private logs: LogEntry[] = [];
  private maxLogEntries = 1000;

  private constructor() {}

  static getInstance(): AuthLogger {
    if (!AuthLogger.instance) {
      AuthLogger.instance = new AuthLogger();
    }
    return AuthLogger.instance;
  }

  log(level: 'info' | 'warn' | 'error' | 'debug', message: string, context?: Record<string, any>): void {
    const logEntry: LogEntry = {
      timestamp: new Date(),
      level,
      message,
      context
    };

    this.logs.push(logEntry);

    // Keep only the most recent logs to prevent memory issues
    if (this.logs.length > this.maxLogEntries) {
      this.logs.shift();
    }

    // In development, also log to console
    if (process.env.NODE_ENV === 'development') {
      const consoleMessage = `[AUTH-${level.toUpperCase()}] ${message}`;
      switch (level) {
        case 'error':
          console.error(consoleMessage, context);
          break;
        case 'warn':
          console.warn(consoleMessage, context);
          break;
        case 'debug':
          console.debug(consoleMessage, context);
          break;
        default:
          console.log(consoleMessage, context);
      }
    }
  }

  info(message: string, context?: Record<string, any>): void {
    this.log('info', message, context);
  }

  warn(message: string, context?: Record<string, any>): void {
    this.log('warn', message, context);
  }

  error(message: string, context?: Record<string, any>): void {
    this.log('error', message, context);
  }

  debug(message: string, context?: Record<string, any>): void {
    this.log('debug', message, context);
  }

  getLogs(): LogEntry[] {
    return [...this.logs]; // Return a copy to prevent external mutations
  }

  clearLogs(): void {
    this.logs = [];
  }

  /**
   * Get recent authentication verification logs to detect potential loops
   */
  getRecentVerificationLogs(count: number = 10): LogEntry[] {
    return this.logs
      .filter(log => log.message.toLowerCase().includes('verify') || log.message.toLowerCase().includes('auth'))
      .slice(-count);
  }
}

export const authLogger = AuthLogger.getInstance();

// Helper function to log authentication verification attempts with context
export function logAuthVerification(
  message: string,
  context?: Record<string, any>,
  origin?: 'client' | 'server' | 'middleware' | 'proxy'
): void {
  const fullContext = {
    ...context,
    origin,
    timestamp: new Date().toISOString(),
    pid: typeof process !== 'undefined' ? process.pid : 'browser'
  };

  authLogger.info(`Auth Verification: ${message}`, fullContext);
}

// Helper function to detect potential loops in verification attempts
export function detectPotentialLoop(): boolean {
  const recentLogs = authLogger.getRecentVerificationLogs(20);
  const verifyAttempts = recentLogs.filter(log =>
    log.message.toLowerCase().includes('verify') &&
    log.level === 'info'
  );

  // If we have more than 5 verification attempts in the last 20 logs, it might indicate a loop
  if (verifyAttempts.length > 5) {
    const timeWindowMs = 5000; // 5 seconds
    const recentVerifyAttempts = verifyAttempts.filter(log =>
      new Date().getTime() - log.timestamp.getTime() < timeWindowMs
    );

    if (recentVerifyAttempts.length > 5) {
      authLogger.warn('Potential authentication verification loop detected', {
        recentAttemptCount: recentVerifyAttempts.length,
        timeWindowMs
      });
      return true;
    }
  }

  return false;
}