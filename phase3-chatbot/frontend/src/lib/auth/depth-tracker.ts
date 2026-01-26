/**
 * Authentication Verification Depth Tracker
 * Tracks the depth of authentication verification calls to prevent infinite recursion
 */

export interface DepthFrame {
  id: string;
  url: string;
  method: string;
  timestamp: number;
  depth: number;
  origin: string;
  context: string;
  parentFrameId?: string;
  depthLimitExceeded: boolean;
}

class DepthTracker {
  private static instance: DepthTracker;
  private frames: DepthFrame[] = [];
  private maxFrames = 100; // Keep only recent frames
  private maxDepth = 10; // Maximum allowed depth to prevent infinite recursion
  private depthWarningThreshold = 7; // When to warn about high depth

  private constructor() {}

  static getInstance(): DepthTracker {
    if (!DepthTracker.instance) {
      DepthTracker.instance = new DepthTracker();
    }
    return DepthTracker.instance;
  }

  /**
   * Track a new frame in the verification call stack
   */
  trackFrame(
    url: string,
    method: string,
    context: string,
    origin: string,
    parentFrameId?: string
  ): {
    id: string;
    depth: number;
    exceeded: boolean;
  } {
    const id = this.generateId();
    const now = Date.now();

    // Calculate the depth based on the parent frame
    const parentFrame = parentFrameId ? this.getFrameById(parentFrameId) : null;
    const depth = parentFrame ? parentFrame.depth + 1 : 0;

    // Check if depth limit is exceeded
    const depthLimitExceeded = depth > this.maxDepth;

    // Create the new frame
    const frame: DepthFrame = {
      id,
      url,
      method,
      timestamp: now,
      depth,
      origin,
      context,
      parentFrameId,
      depthLimitExceeded
    };

    // Log a warning if we're approaching the depth limit
    if (depth > this.depthWarningThreshold && depth <= this.maxDepth) {
      console.warn(`[DEPTH-TRACKER] Authentication verification depth approaching limit: ${depth}/${this.maxDepth}`, {
        url,
        method,
        context,
        origin
      });
    }

    // Log an error if depth limit is exceeded
    if (depthLimitExceeded) {
      console.error(`[DEPTH-TRACKER] Authentication verification depth limit exceeded: ${depth}/${this.maxDepth}`, {
        url,
        method,
        context,
        origin,
        stack: this.getCallStack()
      });
    }

    this.frames.push(frame);

    // Keep only the most recent frames
    if (this.frames.length > this.maxFrames) {
      this.frames = this.frames.slice(-this.maxFrames);
    }

    return {
      id,
      depth,
      exceeded: depthLimitExceeded
    };
  }

  /**
   * Generate a unique ID for tracking
   */
  private generateId(): string {
    return `depth-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get the current call stack for debugging
   */
  private getCallStack(): string[] {
    const stack: string[] = [];
    const recentFrames = [...this.frames].reverse().slice(0, 20); // Get most recent frames

    for (const frame of recentFrames) {
      stack.push(`${frame.origin}:${frame.url}[${frame.depth}]`);
    }

    return stack;
  }

  /**
   * Get all tracked frames
   */
  getAllFrames(): DepthFrame[] {
    return [...this.frames];
  }

  /**
   * Get frames by depth
   */
  getFramesByDepth(depth: number): DepthFrame[] {
    return this.frames.filter(frame => frame.depth === depth);
  }

  /**
   * Get frames by origin
   */
  getFramesByOrigin(origin: string): DepthFrame[] {
    return this.frames.filter(frame => frame.origin === origin);
  }

  /**
   * Get frames by URL pattern
   */
  getFramesByUrl(urlPattern: string): DepthFrame[] {
    return this.frames.filter(frame => frame.url.includes(urlPattern));
  }

  /**
   * Get frames by context
   */
  getFramesByContext(context: string): DepthFrame[] {
    return this.frames.filter(frame => frame.context.includes(context));
  }

  /**
   * Get the deepest frame in the current stack
   */
  getDeepestFrame(): DepthFrame | undefined {
    return this.frames.length > 0
      ? [...this.frames].sort((a, b) => b.depth - a.depth)[0]
      : undefined;
  }

  /**
   * Get the maximum depth reached
   */
  getMaxDepthReached(): number {
    return this.frames.length > 0
      ? Math.max(...this.frames.map(frame => frame.depth))
      : 0;
  }

  /**
   * Get the current depth of the verification stack
   */
  getCurrentDepth(): number {
    return this.getMaxDepthReached();
  }

  /**
   * Get a specific frame by ID
   */
  getFrameById(id: string): DepthFrame | undefined {
    return this.frames.find(frame => frame.id === id);
  }

  /**
   * Get frames that exceed the depth limit
   */
  getExceededFrames(): DepthFrame[] {
    return this.frames.filter(frame => frame.depthLimitExceeded);
  }

  /**
   * Get frames within a specific depth range
   */
  getFramesByDepthRange(minDepth: number, maxDepth: number): DepthFrame[] {
    return this.frames.filter(frame => frame.depth >= minDepth && frame.depth <= maxDepth);
  }

  /**
   * Get the call chain starting from a specific frame ID
   */
  getCallChain(startFrameId: string): DepthFrame[] {
    const chain: DepthFrame[] = [];
    let currentId: string | undefined = startFrameId;

    while (currentId) {
      const frame = this.frames.find(f => f.id === currentId);
      if (frame) {
        chain.unshift(frame); // Add to beginning to maintain order
        currentId = frame.parentFrameId;
      } else {
        break;
      }
    }

    return chain;
  }

  /**
   * Get all call chains (groups of related frames)
   */
  getAllCallChains(): DepthFrame[][] {
    const chains: DepthFrame[][] = [];
    const processedIds = new Set<string>();

    for (const frame of this.frames) {
      if (processedIds.has(frame.id)) continue;

      const chain = this.getCallChain(frame.id);
      if (chain.length > 0) {
        chains.push(chain);
        chain.forEach(f => processedIds.add(f.id));
      }
    }

    return chains;
  }

  /**
   * Get statistics about the depth tracking
   */
  getStats(): {
    totalFrames: number;
    maxDepthReached: number;
    exceededFramesCount: number;
    averageDepth: number;
    deepestChainLength: number;
    callChainsCount: number;
  } {
    const depths = this.frames.map(f => f.depth);
    const chains = this.getAllCallChains();

    return {
      totalFrames: this.frames.length,
      maxDepthReached: this.getMaxDepthReached(),
      exceededFramesCount: this.getExceededFrames().length,
      averageDepth: depths.length > 0 ? depths.reduce((sum, d) => sum + d, 0) / depths.length : 0,
      deepestChainLength: chains.length > 0 ? Math.max(...chains.map(c => c.length)) : 0,
      callChainsCount: chains.length
    };
  }

  /**
   * Check if the depth limit has been exceeded anywhere
   */
  isDepthLimitExceeded(): boolean {
    return this.getExceededFrames().length > 0;
  }

  /**
   * Check if we're approaching the depth limit
   */
  isApproachingDepthLimit(buffer: number = 2): boolean {
    return (this.getCurrentDepth() + buffer) >= this.maxDepth;
  }

  /**
   * Get frames that are approaching the depth limit
   */
  getApproachingFrames(): DepthFrame[] {
    return this.frames.filter(frame =>
      frame.depth >= (this.maxDepth - 2) && !frame.depthLimitExceeded
    );
  }

  /**
   * Clear all tracked frames (useful for testing or memory management)
   */
  clearFrames(): void {
    this.frames = [];
  }

  /**
   * Reset the depth tracker to initial state
   */
  reset(): void {
    this.clearFrames();
  }

  /**
   * Get a summary of the current state
   */
  getSummary(): {
    currentDepth: number;
    isOverLimit: boolean;
    approachingLimit: boolean;
    exceededCount: number;
    totalTracked: number;
    warningThreshold: number;
    limit: number;
  } {
    return {
      currentDepth: this.getCurrentDepth(),
      isOverLimit: this.isDepthLimitExceeded(),
      approachingLimit: this.isApproachingDepthLimit(),
      exceededCount: this.getExceededFrames().length,
      totalTracked: this.frames.length,
      warningThreshold: this.depthWarningThreshold,
      limit: this.maxDepth
    };
  }

  /**
   * Validate if a new frame would exceed the depth limit
   */
  wouldExceedDepthLimit(parentFrameId?: string): boolean {
    const parentFrame = parentFrameId ? this.getFrameById(parentFrameId) : null;
    const newDepth = parentFrame ? parentFrame.depth + 1 : 0;
    return newDepth > this.maxDepth;
  }
}

export const depthTracker = DepthTracker.getInstance();

/**
 * Convenience function to track a verification frame
 */
export function trackVerificationDepth(
  url: string,
  method: string,
  context: string,
  origin: string,
  parentFrameId?: string
): {
  id: string;
  depth: number;
  exceeded: boolean;
} {
  return depthTracker.trackFrame(url, method, context, origin, parentFrameId);
}

/**
 * Check if the depth limit would be exceeded by a new call
 */
export function wouldDepthLimitBeExceeded(parentFrameId?: string): boolean {
  return depthTracker.wouldExceedDepthLimit(parentFrameId);
}

/**
 * Get the current depth of the verification stack
 */
export function getCurrentVerificationDepth(): number {
  return depthTracker.getCurrentDepth();
}

/**
 * Check if the depth limit has been exceeded
 */
export function isVerificationDepthLimitExceeded(): boolean {
  return depthTracker.isDepthLimitExceeded();
}

/**
 * Check if we're approaching the depth limit
 */
export function isApproachingVerificationDepthLimit(): boolean {
  return depthTracker.isApproachingDepthLimit();
}

/**
 * Get depth tracking statistics
 */
export function getDepthTrackingStats() {
  return depthTracker.getStats();
}

/**
 * Get depth tracking summary
 */
export function getDepthTrackingSummary() {
  return depthTracker.getSummary();
}

/**
 * Get frames that are approaching the depth limit
 */
export function getApproachingDepthFrames() {
  return depthTracker.getApproachingFrames();
}