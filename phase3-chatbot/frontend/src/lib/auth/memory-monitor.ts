/**
 * Memory monitoring utilities for authentication-related operations
 * Helps track memory usage during authentication verification flows
 */

interface MemoryStats {
  used: number;
  total: number;
  limit: number;
  timestamp: Date;
}

class MemoryMonitor {
  private static instance: MemoryMonitor;
  private memoryHistory: MemoryStats[] = [];
  private maxHistorySize = 1000;
  private monitoringInterval: NodeJS.Timeout | null = null;

  private constructor() {}

  static getInstance(): MemoryMonitor {
    if (!MemoryMonitor.instance) {
      MemoryMonitor.instance = new MemoryMonitor();
    }
    return MemoryMonitor.instance;
  }

  /**
   * Get current memory usage stats
   */
  getCurrentMemoryStats(): MemoryStats | null {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      const memoryUsage = process.memoryUsage();
      const stats: MemoryStats = {
        used: memoryUsage.heapUsed,
        total: memoryUsage.heapTotal,
        limit: this.getMemoryLimit(),
        timestamp: new Date()
      };

      // Add to history
      this.memoryHistory.push(stats);

      // Keep only the most recent entries to prevent memory issues
      if (this.memoryHistory.length > this.maxHistorySize) {
        this.memoryHistory.shift();
      }

      return stats;
    }

    return null;
  }

  /**
   * Get memory limit if available
   */
  private getMemoryLimit(): number {
    if (typeof process !== 'undefined' && process.memoryUsage) {
      // For Node.js, return approximate limit
      return 2 * 1024 * 1024 * 1024; // 2GB default assumption
    }
    return 0;
  }

  /**
   * Start periodic memory monitoring
   */
  startMonitoring(intervalMs: number = 1000): void {
    if (this.monitoringInterval) {
      this.stopMonitoring();
    }

    this.monitoringInterval = setInterval(() => {
      this.getCurrentMemoryStats();
    }, intervalMs);
  }

  /**
   * Stop memory monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * Get memory history
   */
  getMemoryHistory(): MemoryStats[] {
    return [...this.memoryHistory];
  }

  /**
   * Check if memory usage is approaching dangerous levels
   */
  isMemoryUsageHigh(thresholdRatio: number = 0.8): boolean {
    const currentStats = this.getCurrentMemoryStats();
    if (!currentStats) return false;

    const ratio = currentStats.used / currentStats.limit;
    return ratio > thresholdRatio;
  }

  /**
   * Get memory trend analysis
   */
  getMemoryTrend(windowMinutes: number = 5): {
    isGrowing: boolean;
    averageGrowthRate: number; // bytes per minute
    samples: number;
  } {
    const now = new Date();
    const startTime = new Date(now.getTime() - (windowMinutes * 60 * 1000));

    const recentStats = this.memoryHistory.filter(stat =>
      stat.timestamp >= startTime
    );

    if (recentStats.length < 2) {
      return {
        isGrowing: false,
        averageGrowthRate: 0,
        samples: recentStats.length
      };
    }

    const firstStat = recentStats[0];
    const lastStat = recentStats[recentStats.length - 1];

    const timeDiffMinutes = (lastStat.timestamp.getTime() - firstStat.timestamp.getTime()) / (1000 * 60);
    const memoryDiff = lastStat.used - firstStat.used;
    const averageGrowthRate = timeDiffMinutes > 0 ? memoryDiff / timeDiffMinutes : 0;

    return {
      isGrowing: averageGrowthRate > 0,
      averageGrowthRate,
      samples: recentStats.length
    };
  }

  /**
   * Reset memory history
   */
  resetHistory(): void {
    this.memoryHistory = [];
  }

  /**
   * Check if there's concerning memory growth
   */
  isMemoryGrowthConcerning(): boolean {
    const trend = this.getMemoryTrend(5); // Check last 5 minutes

    // Flag if growth rate is more than 10MB per minute
    const concerningGrowthRate = 10 * 1024 * 1024; // 10MB

    return trend.isGrowing && trend.averageGrowthRate > concerningGrowthRate;
  }
}

export const memoryMonitor = MemoryMonitor.getInstance();

// Utility function to log memory stats
export function logMemoryStats(context: string = 'Auth Operation'): void {
  const stats = memoryMonitor.getCurrentMemoryStats();
  if (stats) {
    console.log(`[${context}] Memory - Used: ${(stats.used / 1024 / 1024).toFixed(2)}MB, Total: ${(stats.total / 1024 / 1024).toFixed(2)}MB`);
  }
}

// Start monitoring when this module is imported in development
if (typeof window === 'undefined' && process.env.NODE_ENV === 'development') {
  memoryMonitor.startMonitoring(2000); // Monitor every 2 seconds in development
}