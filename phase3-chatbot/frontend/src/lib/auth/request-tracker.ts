/**
 * Authentication Request Origin Tracker
 * Tracks the origin of authentication requests to identify patterns and potential issues
 */

export interface RequestOrigin {
  id: string;
  url: string;
  method: string;
  timestamp: number;
  origin: 'client' | 'server' | 'middleware' | 'proxy' | 'unknown';
  referrer?: string;
  userAgent?: string;
  stackTrace?: string;
  isRecursive?: boolean;
  parentRequestId?: string;
  context: string;
  headers?: Record<string, string>;
}

class RequestTracker {
  private static instance: RequestTracker;
  private requests: RequestOrigin[] = [];
  private maxRequests = 500; // Keep only recent requests
  private recursiveRequestThreshold = 1000; // ms between similar requests to consider recursive

  private constructor() {}

  static getInstance(): RequestTracker {
    if (!RequestTracker.instance) {
      RequestTracker.instance = new RequestTracker();
    }
    return RequestTracker.instance;
  }

  /**
   * Track a request with its origin
   */
  trackRequest(
    url: string,
    method: string,
    context: string,
    options: {
      referrer?: string;
      userAgent?: string;
      headers?: Record<string, string>;
      parentRequestId?: string;
    } = {}
  ): string {
    const id = this.generateId();
    const now = Date.now();

    // Determine origin based on execution context
    const origin = this.determineOrigin();

    // Capture stack trace in development
    const stackTrace = this.captureStackTrace();

    // Check if this request might be recursive
    const isRecursive = this.isPotentiallyRecursive(url, method, now);

    const request: RequestOrigin = {
      id,
      url,
      method,
      timestamp: now,
      origin,
      referrer: options.referrer,
      userAgent: options.userAgent,
      stackTrace,
      isRecursive,
      parentRequestId: options.parentRequestId,
      context,
      headers: options.headers
    };

    this.requests.push(request);

    // Keep only the most recent requests
    if (this.requests.length > this.maxRequests) {
      this.requests = this.requests.slice(-this.maxRequests);
    }

    return id;
  }

  /**
   * Generate a unique ID for tracking
   */
  private generateId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Determine the origin of the request based on execution context
   */
  private determineOrigin(): 'client' | 'server' | 'middleware' | 'proxy' | 'unknown' {
    if (typeof window !== 'undefined') {
      // Client-side
      return 'client';
    } else if (typeof process !== 'undefined') {
      // Server-side
      // Check if we're in a Next.js middleware context
      if (this.isMiddlewareContext()) {
        return 'middleware';
      } else if (this.isProxyContext()) {
        return 'proxy';
      } else {
        return 'server';
      }
    }

    return 'unknown';
  }

  /**
   * Check if we're in a middleware context
   */
  private isMiddlewareContext(): boolean {
    // This is a simplified check - in practice, you'd have more specific detection
    try {
      // Check for NextRequest-like objects in call stack
      const stack = this.captureStackTrace();
      return stack?.includes('next/dist/server') && stack?.includes('middleware') ? true : false;
    } catch {
      return false;
    }
  }

  /**
   * Check if we're in a proxy context
   */
  private isProxyContext(): boolean {
    try {
      const stack = this.captureStackTrace();
      return stack?.includes('api/auth') && stack?.includes('route') ? true : false;
    } catch {
      return false;
    }
  }

  /**
   * Capture stack trace for debugging
   */
  private captureStackTrace(): string | undefined {
    if (typeof process !== 'undefined' && process.env?.NODE_ENV === 'development') {
      try {
        const obj: any = {};
        Error.captureStackTrace?.(obj, this.captureStackTrace);
        return obj.stack;
      } catch (e) {
        return undefined;
      }
    }
    return undefined;
  }

  /**
   * Check if a request is potentially recursive
   */
  private isPotentiallyRecursive(url: string, method: string, timestamp: number): boolean {
    // Look for similar requests in the recent past
    const recentThreshold = this.recursiveRequestThreshold;
    const recentRequests = this.requests.filter(req =>
      timestamp - req.timestamp <= recentThreshold &&
      req.url === url &&
      req.method === method
    );

    // If we have more than 2 similar requests in the threshold time, consider it potentially recursive
    return recentRequests.length > 2;
  }

  /**
   * Get all tracked requests
   */
  getAllRequests(): RequestOrigin[] {
    return [...this.requests];
  }

  /**
   * Get requests by origin
   */
  getRequestsByOrigin(origin: string): RequestOrigin[] {
    return this.requests.filter(req => req.origin === origin);
  }

  /**
   * Get requests by URL pattern
   */
  getRequestsByUrl(urlPattern: string): RequestOrigin[] {
    return this.requests.filter(req => req.url.includes(urlPattern));
  }

  /**
   * Get requests by method
   */
  getRequestsByMethod(method: string): RequestOrigin[] {
    return this.requests.filter(req => req.method === method);
  }

  /**
   * Get recent requests
   */
  getRecentRequests(limit: number = 50): RequestOrigin[] {
    return this.requests.slice(-limit).reverse();
  }

  /**
   * Get requests within a time range
   */
  getRequestsInTimeRange(start: number, end: number): RequestOrigin[] {
    return this.requests.filter(req => req.timestamp >= start && req.timestamp <= end);
  }

  /**
   * Get recursive request candidates
   */
  getRecursiveCandidates(): RequestOrigin[] {
    return this.requests.filter(req => req.isRecursive);
  }

  /**
   * Get request statistics
   */
  getStats(): {
    totalRequests: number;
    byOrigin: Record<string, number>;
    byMethod: Record<string, number>;
    recursiveCount: number;
    byContext: Record<string, number>;
  } {
    const byOrigin: Record<string, number> = {};
    const byMethod: Record<string, number> = {};
    const byContext: Record<string, number> = {};

    let recursiveCount = 0;

    this.requests.forEach(req => {
      byOrigin[req.origin] = (byOrigin[req.origin] || 0) + 1;
      byMethod[req.method] = (byMethod[req.method] || 0) + 1;
      byContext[req.context] = (byContext[req.context] || 0) + 1;

      if (req.isRecursive) {
        recursiveCount++;
      }
    });

    return {
      totalRequests: this.requests.length,
      byOrigin,
      byMethod,
      recursiveCount,
      byContext
    };
  }

  /**
   * Check if there are potential recursive patterns
   */
  hasRecursivePatterns(): boolean {
    return this.getRecursiveCandidates().length > 0;
  }

  /**
   * Get request chain starting from a specific request ID
   */
  getRequestChain(startId: string): RequestOrigin[] {
    const chain: RequestOrigin[] = [];
    let currentId: string | undefined = startId;

    while (currentId) {
      const request = this.requests.find(req => req.id === currentId);
      if (request) {
        chain.unshift(request); // Add to beginning to maintain chronological order
        currentId = request.parentRequestId;
      } else {
        break;
      }
    }

    return chain;
  }

  /**
   * Find request cycles (recursive chains)
   */
  findCycles(): RequestOrigin[][] {
    const cycles: RequestOrigin[][] = [];
    const visited = new Set<string>();

    for (const request of this.requests) {
      if (visited.has(request.id)) continue;

      const chain = this.getRequestChain(request.id);
      const chainIds = new Set(chain.map(r => r.id));

      // Check if there's a cycle in this chain
      if (chain.length > 1) {
        // Look for repeated URLs/methods in the chain
        const urlMethodPairs = new Set<string>();
        let cycleFound = false;

        for (const req of chain) {
          const pair = `${req.url}-${req.method}`;
          if (urlMethodPairs.has(pair)) {
            cycleFound = true;
            break;
          }
          urlMethodPairs.add(pair);
        }

        if (cycleFound) {
          cycles.push(chain);
        }
      }

      // Mark all requests in this chain as visited
      chain.forEach(req => visited.add(req.id));
    }

    return cycles;
  }

  /**
   * Clear all tracked requests (useful for testing or memory management)
   */
  clearRequests(): void {
    this.requests = [];
  }

  /**
   * Get a specific request by ID
   */
  getRequestById(id: string): RequestOrigin | undefined {
    return this.requests.find(req => req.id === id);
  }

  /**
   * Get requests by context
   */
  getRequestsByContext(context: string): RequestOrigin[] {
    return this.requests.filter(req => req.context.includes(context));
  }

  /**
   * Find suspicious request patterns
   */
  getSuspiciousPatterns(): {
    recursiveChains: RequestOrigin[][];
    highFrequencyEndpoints: Array<{ url: string; count: number; timeWindow: number }>;
    unusualOrigins: string[];
  } {
    // Find recursive chains
    const recursiveChains = this.findCycles();

    // Find high-frequency endpoints (more than 5 requests in 2 seconds)
    const now = Date.now();
    const twoSecondsAgo = now - 2000;
    const recentRequests = this.requests.filter(req => req.timestamp >= twoSecondsAgo);

    const endpointCounts = recentRequests.reduce((acc, req) => {
      acc[req.url] = (acc[req.url] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const highFrequencyEndpoints = Object.entries(endpointCounts)
      .filter(([_, count]) => count > 5)
      .map(([url, count]) => ({ url, count, timeWindow: 2000 }));

    // Find unusual origins (those that appear infrequently but atypically)
    const originCounts = this.getStats().byOrigin;
    const totalRequests = this.requests.length;
    const unusualOrigins = Object.entries(originCounts)
      .filter(([_, count]) => count / totalRequests < 0.05) // Less than 5% of requests
      .map(([origin, _]) => origin);

    return {
      recursiveChains,
      highFrequencyEndpoints,
      unusualOrigins
    };
  }
}

export const requestTracker = RequestTracker.getInstance();

/**
 * Convenience function to track a request
 */
export function trackAuthRequest(
  url: string,
  method: string,
  context: string,
  options: {
    referrer?: string;
    userAgent?: string;
    headers?: Record<string, string>;
    parentRequestId?: string;
  } = {}
): string {
  return requestTracker.trackRequest(url, method, context, options);
}

/**
 * Get suspicious request patterns
 */
export function getSuspiciousRequestPatterns() {
  return requestTracker.getSuspiciousPatterns();
}

/**
 * Check if there are recursive request patterns
 */
export function hasRecursiveRequestPatterns(): boolean {
  return requestTracker.hasRecursivePatterns();
}

/**
 * Get request statistics
 */
export function getRequestStats() {
  return requestTracker.getStats();
}