/**
 * Authentication Verification Origin Tracker
 * Helps identify where authentication verification requests originate
 * to detect and prevent recursive loops
 */

interface VerificationRecord {
  id: string;
  timestamp: number;
  origin: 'client' | 'server' | 'middleware' | 'proxy' | 'unknown';
  path: string;
  method: string;
  context: string;
  stackTrace?: string;
  parentId?: string; // For tracking call chains
}

class OriginTracker {
  private static instance: OriginTracker;
  private records: VerificationRecord[] = [];
  private maxRecords = 1000; // Keep only the most recent records
  private callChainDepth = 0;
  private maxCallChainDepth = 10; // Prevent extremely deep chains

  private constructor() {}

  static getInstance(): OriginTracker {
    if (!OriginTracker.instance) {
      OriginTracker.instance = new OriginTracker();
    }
    return OriginTracker.instance;
  }

  /**
   * Record an authentication verification attempt with its origin
   */
  recordVerification(
    origin: 'client' | 'server' | 'middleware' | 'proxy' | 'unknown',
    path: string = '',
    method: string = 'UNKNOWN',
    context: string = '',
    parentId?: string
  ): string {
    const id = this.generateId();

    // Capture stack trace for debugging
    const stackTrace = this.captureStackTrace();

    const record: VerificationRecord = {
      id,
      timestamp: Date.now(),
      origin,
      path,
      method,
      context,
      stackTrace,
      parentId
    };

    this.records.push(record);

    // Keep only the most recent records to prevent memory issues
    if (this.records.length > this.maxRecords) {
      this.records = this.records.slice(-this.maxRecords);
    }

    return id;
  }

  /**
   * Generate a unique ID for tracking
   */
  private generateId(): string {
    return `auth-verify-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Capture stack trace for debugging
   */
  private captureStackTrace(): string | undefined {
    if (process.env.NODE_ENV === 'development') {
      try {
        // Create an error to capture the stack trace
        const obj: any = {};
        Error.captureStackTrace(obj, this.captureStackTrace);
        return obj.stack;
      } catch (e) {
        return undefined;
      }
    }
    return undefined;
  }

  /**
   * Get recent verification records
   */
  getRecentRecords(limit: number = 50): VerificationRecord[] {
    return [...this.records].slice(-limit).reverse(); // Most recent first
  }

  /**
   * Get records by origin
   */
  getRecordsByOrigin(origin: string, limit: number = 50): VerificationRecord[] {
    return this.records
      .filter(record => record.origin === origin)
      .slice(-limit)
      .reverse();
  }

  /**
   * Get records by path
   */
  getRecordsByPath(path: string, limit: number = 50): VerificationRecord[] {
    return this.records
      .filter(record => record.path.includes(path))
      .slice(-limit)
      .reverse();
  }

  /**
   * Detect potential recursive authentication verification loops
   */
  detectRecursiveLoops(timeWindowMs: number = 5000, minOccurrences: number = 3): boolean {
    const now = Date.now();
    const recentRecords = this.records.filter(record => now - record.timestamp <= timeWindowMs);

    // Group by origin and path to detect patterns
    const grouped = recentRecords.reduce((acc, record) => {
      const key = `${record.origin}:${record.path}`;
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(record);
      return acc;
    }, {} as Record<string, VerificationRecord[]>);

    // Check if any group has more than minOccurrences records
    for (const [key, records] of Object.entries(grouped)) {
      if (records.length >= minOccurrences) {
        // Check if they occurred in rapid succession (indicating a loop)
        const timeDiff = records[records.length - 1].timestamp - records[0].timestamp;
        if (timeDiff < timeWindowMs && records.length >= minOccurrences) {
          console.warn(`[OriginTracker] Potential authentication verification loop detected: ${key}`, {
            occurrences: records.length,
            timeWindowMs,
            timeDiff,
            records: records.map(r => ({
              timestamp: new Date(r.timestamp).toISOString(),
              context: r.context
            }))
          });
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Get verification call chain (parent-child relationships)
   */
  getCallChain(startId: string): VerificationRecord[] {
    const chain: VerificationRecord[] = [];
    let currentId: string | undefined = startId;

    while (currentId) {
      const record = this.records.find(r => r.id === currentId);
      if (record) {
        chain.push(record);
        currentId = record.parentId;

        // Prevent infinite loops in case of circular references
        if (chain.length > this.maxCallChainDepth) {
          console.warn(`[OriginTracker] Call chain too deep, stopping at ${this.maxCallChainDepth} levels`);
          break;
        }
      } else {
        break;
      }
    }

    return chain.reverse(); // Oldest first
  }

  /**
   * Clear all records (useful for testing or memory management)
   */
  clearRecords(): void {
    this.records = [];
  }

  /**
   * Get statistics about verification origins
   */
  getOriginStats(): Record<string, number> {
    return this.records.reduce((acc, record) => {
      acc[record.origin] = (acc[record.origin] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  }

  /**
   * Check if we're in a verification loop and get details
   */
  checkLoopStatus(): {
    isLooping: boolean;
    details?: {
      origin: string;
      path: string;
      count: number;
      timeWindowMs: number;
    };
  } {
    const now = Date.now();
    const timeWindowMs = 5000; // 5 seconds
    const minOccurrences = 3;

    const recentRecords = this.records.filter(record => now - record.timestamp <= timeWindowMs);

    // Group by origin and path
    const grouped = recentRecords.reduce((acc, record) => {
      const key = `${record.origin}:${record.path}`;
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(record);
      return acc;
    }, {} as Record<string, VerificationRecord[]>);

    // Find groups with suspicious activity
    for (const [key, records] of Object.entries(grouped)) {
      if (records.length >= minOccurrences) {
        const [origin, path] = key.split(':');
        return {
          isLooping: true,
          details: {
            origin,
            path,
            count: records.length,
            timeWindowMs
          }
        };
      }
    }

    return { isLooping: false };
  }
}

export const originTracker = OriginTracker.getInstance();

/**
 * Convenience function to record verification with automatic origin detection
 */
export function recordAuthVerification(
  path: string = '',
  method: string = 'UNKNOWN',
  context: string = '',
  parentId?: string
): string {
  // Try to detect origin based on execution context
  let origin: 'client' | 'server' | 'middleware' | 'proxy' | 'unknown' = 'unknown';

  if (typeof window !== 'undefined') {
    // Running in browser/client
    origin = 'client';
  } else if (typeof process !== 'undefined') {
    // Running in Node.js server environment
    origin = 'server';
  } else {
    // Unknown environment
    origin = 'unknown';
  }

  return originTracker.recordVerification(origin, path, method, context, parentId);
}

/**
 * Check if there's a potential recursive loop in authentication verification
 */
export function isAuthVerificationLooping(): boolean {
  return originTracker.detectRecursiveLoops();
}

/**
 * Get loop status with details
 */
export function getAuthVerificationLoopStatus() {
  return originTracker.checkLoopStatus();
}