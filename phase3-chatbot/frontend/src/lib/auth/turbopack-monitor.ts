/**
 * Turbopack-Specific Memory Monitoring for Authentication
 * Monitors memory usage patterns specific to Turbopack development environment
 */

import { authLogger } from './logging';
import { isDevMode } from './config';
import { memoryMonitor } from './memory-monitor';

export interface TurbopackMemorySnapshot {
  timestamp: number;
  heapUsed: number;
  heapTotal: number;
  external: number;
  rss: number;
  authRelatedMemory: number; // Estimated memory used by auth components
  turbopackReloadCount: number;
  gcRuns: number;
  isTurbopackActive: boolean;
}

export interface TurbopackMemoryAnalysis {
  snapshots: TurbopackMemorySnapshot[];
  avgHeapGrowthRate: number; // bytes per reload
  authMemoryPressure: 'low' | 'medium' | 'high';
  turbopackStability: 'stable' | 'unstable' | 'critical';
  recommendations: string[];
}

class TurbopackMemoryMonitor {
  private static instance: TurbopackMemoryMonitor;
  private snapshots: TurbopackMemorySnapshot[] = [];
  private maxSnapshots = 100; // Keep only recent snapshots
  private turbopackReloadCount = 0;
  private gcRuns = 0;
  private lastSnapshot: TurbopackMemorySnapshot | null = null;
  private monitoringInterval: NodeJS.Timeout | null = null;

  private constructor() {
    // Listen for garbage collection if available (Node.js)
    if (typeof global !== 'undefined' && (global as any).gc) {
      // Enable garbage collection monitoring
      this.setupGCListener();
    }
  }

  static getInstance(): TurbopackMemoryMonitor {
    if (!TurbopackMemoryMonitor.instance) {
      TurbopackMemoryMonitor.instance = new TurbopackMemoryMonitor();
    }
    return TurbopackMemoryMonitor.instance;
  }

  /**
   * Setup garbage collection listener
   */
  private setupGCListener(): void {
    if (typeof process !== 'undefined' && process.on) {
      process.on('beforeExit', () => {
        this.gcRuns++;
      });
    }
  }

  /**
   * Take a memory snapshot specific to Turbopack environment
   */
  takeSnapshot(context: string = 'turbopack-monitor'): TurbopackMemorySnapshot {
    // Get basic memory stats
    const memoryStats = memoryMonitor.getCurrentMemoryStats();

    if (!memoryStats) {
      // Browser environment - return minimal snapshot
      const snapshot: TurbopackMemorySnapshot = {
        timestamp: Date.now(),
        heapUsed: 0,
        heapTotal: 0,
        external: 0,
        rss: 0,
        authRelatedMemory: this.estimateAuthMemoryUsage(),
        turbopackReloadCount: this.turbopackReloadCount,
        gcRuns: this.gcRuns,
        isTurbopackActive: this.isTurbopackActive()
      };

      this.snapshots.push(snapshot);
      this.lastSnapshot = snapshot;

      // Keep only recent snapshots
      if (this.snapshots.length > this.maxSnapshots) {
        this.snapshots = this.snapshots.slice(-this.maxSnapshots);
      }

      return snapshot;
    }

    const snapshot: TurbopackMemorySnapshot = {
      timestamp: Date.now(),
      heapUsed: memoryStats.used,
      heapTotal: memoryStats.total,
      external: 0, // Would need Node.js specific code to get this
      rss: 0, // Would need Node.js specific code to get this
      authRelatedMemory: this.estimateAuthMemoryUsage(),
      turbopackReloadCount: this.turbopackReloadCount,
      gcRuns: this.gcRuns,
      isTurbopackActive: this.isTurbopackActive()
    };

    this.snapshots.push(snapshot);
    this.lastSnapshot = snapshot;

    // Keep only recent snapshots
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots = this.snapshots.slice(-this.maxSnapshots);
    }

    authLogger.debug(`[TURBOPACK-MONITOR] Memory snapshot taken`, {
      context,
      heapUsedMB: (snapshot.heapUsed / 1024 / 1024).toFixed(2),
      authMemoryMB: (snapshot.authRelatedMemory / 1024 / 1024).toFixed(2),
      reloadCount: snapshot.turbopackReloadCount,
      gcRuns: snapshot.gcRuns
    });

    return snapshot;
  }

  /**
   * Estimate memory usage by auth components
   */
  private estimateAuthMemoryUsage(): number {
    // This is a rough estimation based on typical JavaScript object sizes
    let estimatedSize = 0;

    // Estimate size of auth state
    const authState = this.estimateAuthStateSize();
    estimatedSize += authState;

    // Estimate size of recent verification records
    const verificationRecordsSize = this.estimateVerificationRecordsSize();
    estimatedSize += verificationRecordsSize;

    // Estimate size of request tracking data
    const requestTrackingSize = this.estimateRequestTrackingSize();
    estimatedSize += requestTrackingSize;

    return estimatedSize;
  }

  /**
   * Estimate auth state size
   */
  private estimateAuthStateSize(): number {
    // Rough estimation: assume 1KB for basic auth state
    return 1024;
  }

  /**
   * Estimate verification records size
   */
  private estimateVerificationRecordsSize(): number {
    // Rough estimation: assume 500 bytes per verification record
    // and we typically store ~50 recent records
    return 500 * 50;
  }

  /**
   * Estimate request tracking size
   */
  private estimateRequestTrackingSize(): number {
    // Rough estimation: assume 300 bytes per request record
    // and we typically store ~100 recent requests
    return 300 * 100;
  }

  /**
   * Check if Turbopack is likely active
   */
  private isTurbopackActive(): boolean {
    // Check for Turbopack-specific indicators
    if (typeof process !== 'undefined') {
      // Turbopack typically sets specific environment variables
      const isTurbopack = process.env.NEXT_RUNTIME === 'edge' ||
                         process.env.__NEXT_TURBOPACK_BUILD ||
                         process.env.TURBOPACK;

      // Check if we're in development mode with hot reloading
      const isDevAndHotReloading = isDevMode() &&
                                   typeof window !== 'undefined' &&
                                   (module as any)?.hot?.status() === 'idle';

      return !!(isTurbopack || isDevAndHotReloading);
    }

    return false;
  }

  /**
   * Increment reload counter (call this when hot reload happens)
   */
  incrementReloadCounter(): void {
    this.turbopackReloadCount++;
    authLogger.debug(`[TURBOPACK-MONITOR] Reload count incremented`, {
      newCount: this.turbopackReloadCount
    });
  }

  /**
   * Get all snapshots
   */
  getSnapshots(): TurbopackMemorySnapshot[] {
    return [...this.snapshots];
  }

  /**
   * Get the most recent snapshot
   */
  getLastSnapshot(): TurbopackMemorySnapshot | null {
    return this.lastSnapshot;
  }

  /**
   * Analyze memory patterns in Turbopack environment
   */
  analyze(): TurbopackMemoryAnalysis {
    if (this.snapshots.length < 2) {
      return {
        snapshots: [...this.snapshots],
        avgHeapGrowthRate: 0,
        authMemoryPressure: 'low',
        turbopackStability: 'stable',
        recommendations: ['Need more memory snapshots to perform analysis']
      };
    }

    // Calculate average heap growth rate
    let totalGrowth = 0;
    let snapshotPairs = 0;

    for (let i = 1; i < this.snapshots.length; i++) {
      const prev = this.snapshots[i - 1];
      const curr = this.snapshots[i];

      // Only calculate growth between snapshots that are reasonably close in time
      // (to avoid measuring long-term trends vs. immediate usage)
      if (curr.timestamp - prev.timestamp < 30000) { // 30 seconds
        totalGrowth += (curr.heapUsed - prev.heapUsed);
        snapshotPairs++;
      }
    }

    const avgHeapGrowthRate = snapshotPairs > 0 ? totalGrowth / snapshotPairs : 0;

    // Determine auth memory pressure
    const latestSnapshot = this.snapshots[this.snapshots.length - 1];
    const authMemoryPercentage = latestSnapshot.authRelatedMemory / latestSnapshot.heapUsed;

    let authMemoryPressure: 'low' | 'medium' | 'high' = 'low';
    if (authMemoryPercentage > 0.3) {
      authMemoryPressure = 'high';
    } else if (authMemoryPercentage > 0.1) {
      authMemoryPressure = 'medium';
    }

    // Determine Turbopack stability
    let turbopackStability: 'stable' | 'unstable' | 'critical' = 'stable';

    // If we have rapid heap growth, mark as unstable
    if (avgHeapGrowthRate > 10 * 1024 * 1024) { // More than 10MB per snapshot
      turbopackStability = 'critical';
    } else if (avgHeapGrowthRate > 1 * 1024 * 1024) { // More than 1MB per snapshot
      turbopackStability = 'unstable';
    }

    // Formulate recommendations
    const recommendations: string[] = [];

    if (turbopackStability === 'critical') {
      recommendations.push('Critical memory growth detected - investigate immediate memory leaks');
    } else if (turbopackStability === 'unstable') {
      recommendations.push('Unstable memory growth - monitor closely for potential leaks');
    }

    if (authMemoryPressure === 'high') {
      recommendations.push('High authentication-related memory usage - optimize auth state management');
    }

    if (this.turbopackReloadCount > 50) {
      recommendations.push('High reload count detected - consider clearing caches or restarting dev server');
    }

    recommendations.push('Continue monitoring memory patterns during development');

    return {
      snapshots: [...this.snapshots],
      avgHeapGrowthRate,
      authMemoryPressure,
      turbopackStability,
      recommendations
    };
  }

  /**
   * Start periodic monitoring
   */
  startMonitoring(intervalMs: number = 5000): void {
    if (this.monitoringInterval) {
      this.stopMonitoring();
    }

    this.monitoringInterval = setInterval(() => {
      if (isDevMode()) {
        this.takeSnapshot('periodic-monitoring');
      }
    }, intervalMs);

    authLogger.info(`[TURBOPACK-MONITOR] Started monitoring with ${intervalMs}ms interval`);
  }

  /**
   * Stop monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
      authLogger.info(`[TURBOPACK-MONITOR] Stopped monitoring`);
    }
  }

  /**
   * Get current memory statistics
   */
  getCurrentStats(): {
    currentHeapUsed: number;
    currentAuthMemory: number;
    reloadCount: number;
    stability: TurbopackMemoryAnalysis['turbopackStability'];
  } {
    const latest = this.getLastSnapshot();
    const analysis = this.analyze();

    return {
      currentHeapUsed: latest?.heapUsed || 0,
      currentAuthMemory: latest?.authRelatedMemory || 0,
      reloadCount: latest?.turbopackReloadCount || 0,
      stability: analysis.turbopackStability
    };
  }

  /**
   * Check if memory usage is concerning in Turbopack context
   */
  isMemoryUsageConcerning(): boolean {
    const analysis = this.analyze();

    return analysis.turbopackStability === 'critical' ||
           analysis.authMemoryPressure === 'high';
  }

  /**
   * Reset monitoring state
   */
  reset(): void {
    this.snapshots = [];
    this.turbopackReloadCount = 0;
    this.gcRuns = 0;
    this.lastSnapshot = null;

    authLogger.info(`[TURBOPACK-MONITOR] Monitoring state reset`);
  }

  /**
   * Generate a memory report
   */
  generateReport(): string {
    const analysis = this.analyze();
    const stats = this.getCurrentStats();

    let report = `=== TURBOPACK MEMORY MONITORING REPORT ===\n`;
    report += `Timestamp: ${new Date().toISOString()}\n`;
    report += `Snapshots Collected: ${this.snapshots.length}\n`;
    report += `Reload Count: ${stats.reloadCount}\n`;
    report += `Current Heap Used: ${(stats.currentHeapUsed / 1024 / 1024).toFixed(2)} MB\n`;
    report += `Auth Memory Est.: ${(stats.currentAuthMemory / 1024 / 1024).toFixed(2)} MB\n`;
    report += `Avg Growth Rate: ${(analysis.avgHeapGrowthRate / 1024 / 1024).toFixed(2)} MB/snapshot\n`;
    report += `Auth Pressure: ${analysis.authMemoryPressure}\n`;
    report += `Turbopack Stability: ${analysis.turbopackStability}\n`;

    if (analysis.recommendations.length > 0) {
      report += `\nRECOMMENDATIONS:\n`;
      analysis.recommendations.forEach(rec => {
        report += `• ${rec}\n`;
      });
    }

    report += `\n=========================================\n`;

    return report;
  }
}

export const turbopackMemoryMonitor = TurbopackMemoryMonitor.getInstance();

/**
 * Convenience function to take a memory snapshot
 */
export function takeTurbopackMemorySnapshot(context: string = 'external-call'): TurbopackMemorySnapshot {
  return turbopackMemoryMonitor.takeSnapshot(context);
}

/**
 * Increment reload counter (useful when hot reloading occurs)
 */
export function incrementTurbopackReloadCounter(): void {
  turbopackMemoryMonitor.incrementReloadCounter();
}

/**
 * Get Turbopack memory analysis
 */
export function getTurbopackMemoryAnalysis(): TurbopackMemoryAnalysis {
  return turbopackMemoryMonitor.analyze();
}

/**
 * Check if memory usage is concerning in Turbopack context
 */
export function isTurbopackMemoryUsageConcerning(): boolean {
  return turbopackMemoryMonitor.isMemoryUsageConcerning();
}

/**
 * Start Turbopack-specific monitoring
 */
export function startTurbopackMemoryMonitoring(intervalMs: number = 5000): void {
  turbopackMemoryMonitor.startMonitoring(intervalMs);
}

/**
 * Stop Turbopack-specific monitoring
 */
export function stopTurbopackMemoryMonitoring(): void {
  turbopackMemoryMonitor.stopMonitoring();
}

/**
 * Generate and log a memory report
 */
export function generateTurbopackMemoryReport(): void {
  const report = turbopackMemoryMonitor.generateReport();
  console.log(report);

  if (isDevMode()) {
    authLogger.info(`[TURBOPACK-MONITOR] Memory report generated`, {
      reportLength: report.length
    });
  }
}

/**
 * Get current memory statistics
 */
export function getTurbopackMemoryStats() {
  return turbopackMemoryMonitor.getCurrentStats();
}