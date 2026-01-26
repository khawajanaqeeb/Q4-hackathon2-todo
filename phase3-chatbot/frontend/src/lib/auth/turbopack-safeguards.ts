/**
 * Turbopack-Specific Development Safeguards for Authentication
 * Additional protections and monitoring specifically for Turbopack development environment
 */

import { authLogger } from './logging';
import { isDevMode } from './config';
import { authStateManager } from './state-manager';
import { originTracker } from './origin-tracker';
import { turbopackMemoryMonitor, isTurbopackMemoryUsageConcerning, getTurbopackMemoryStats } from './turbopack-monitor';
import { turbopackAuthCache, getAuthCacheStats } from './turbopack-cache';
import { hotReloadHandler, getHotReloadStats, isHandlingHotReload } from './hot-reload-handler';
import { handleAuthError } from './error-handler';

export interface TurbopackSafeguardStatus {
  isInitialized: boolean;
  memoryMonitoringActive: boolean;
  cacheMonitoringActive: boolean;
  hotReloadHandlingActive: boolean;
  memoryPressure: 'normal' | 'warning' | 'critical';
  cacheEfficiency: 'high' | 'medium' | 'low';
  hotReloadFrequency: 'normal' | 'high' | 'excessive';
}

class TurbopackSafeguards {
  private static instance: TurbopackSafeguards;
  private isInitialized = false;
  private memoryMonitoringInterval: NodeJS.Timeout | null = null;
  private cacheMonitoringInterval: NodeJS.Timeout | null = null;
  private healthCheckInterval: NodeJS.Timeout | null = null;
  private maxHotReloadsPerMinute = 20; // Maximum acceptable hot reloads per minute

  private constructor() {}

  static getInstance(): TurbopackSafeguards {
    if (!TurbopackSafeguards.instance) {
      TurbopackSafeguards.instance = new TurbopackSafeguards();
    }
    return TurbopackSafeguards.instance;
  }

  /**
   * Initialize Turbopack-specific safeguards
   */
  initialize(): void {
    if (!isDevMode() || this.isInitialized) {
      return;
    }

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Initializing Turbopack-specific safeguards`);

    // Start memory monitoring
    this.startMemoryMonitoring();

    // Start cache monitoring
    this.startCacheMonitoring();

    // Start health checks
    this.startHealthChecks();

    // Setup hot reload handling
    this.setupHotReloadHandling();

    // Setup error handling for Turbopack-specific issues
    this.setupErrorHandling();

    this.isInitialized = true;

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Turbopack safeguards initialized`);
  }

  /**
   * Start memory monitoring specific to Turbopack
   */
  private startMemoryMonitoring(): void {
    // Take initial memory snapshot
    turbopackMemoryMonitor.takeSnapshot('initial');

    // Start periodic monitoring
    turbopackMemoryMonitor.startMonitoring(10000); // Every 10 seconds in development

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Memory monitoring started`);
  }

  /**
   * Start cache monitoring specific to Turbopack
   */
  private startCacheMonitoring(): void {
    this.cacheMonitoringInterval = setInterval(() => {
      if (isDevMode()) {
        const stats = getAuthCacheStats();

        authLogger.debug(`[TURBOPACK-SAFEGUARDS] Cache stats`, {
          hits: stats.hits,
          misses: stats.misses,
          evictions: stats.evictions,
          currentSize: `${(stats.currentSize / 1024 / 1024).toFixed(2)} MB`,
          entriesCount: stats.entriesCount
        });

        // Check for cache inefficiency
        if (stats.misses > 0) {
          const missRate = stats.misses / (stats.hits + stats.misses);
          if (missRate > 0.8) { // More than 80% misses
            authLogger.warn(`[TURBOPACK-SAFEGUARDS] High cache miss rate detected`, {
              missRate: (missRate * 100).toFixed(2) + '%',
              hits: stats.hits,
              misses: stats.misses
            });
          }
        }
      }
    }, 15000); // Every 15 seconds

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Cache monitoring started`);
  }

  /**
   * Start health checks for Turbopack environment
   */
  private startHealthChecks(): void {
    this.healthCheckInterval = setInterval(() => {
      if (isDevMode()) {
        this.performHealthCheck();
      }
    }, 30000); // Every 30 seconds

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Health checks scheduled`);
  }

  /**
   * Perform comprehensive health check
   */
  private performHealthCheck(): void {
    const memoryStats = getTurbopackMemoryStats();
    const cacheStats = getAuthCacheStats();
    const hotReloadStats = getHotReloadStats();

    authLogger.debug(`[TURBOPACK-SAFEGUARDS] Performing health check`, {
      memory: {
        currentHeapUsed: `${(memoryStats.currentHeapUsed / 1024 / 1024).toFixed(2)} MB`,
        authMemory: `${(memoryStats.currentAuthMemory / 1024 / 1024).toFixed(2)} MB`,
        stability: memoryStats.stability
      },
      cache: {
        hits: cacheStats.hits,
        misses: cacheStats.misses,
        currentSize: `${(cacheStats.currentSize / 1024 / 1024).toFixed(2)} MB`,
        entriesCount: cacheStats.entriesCount
      },
      hotReload: {
        totalReloads: hotReloadStats.totalReloads,
        recentReloads: hotReloadStats.recentReloads,
        averageInterval: hotReloadStats.averageInterval ? `${Math.round(hotReloadStats.averageInterval)}ms` : 'N/A'
      }
    });

    // Check for concerning patterns
    this.checkForConcerningPatterns(memoryStats, cacheStats, hotReloadStats);
  }

  /**
   * Check for concerning patterns in the system
   */
  private checkForConcerningPatterns(
    memoryStats: ReturnType<typeof getTurbopackMemoryStats>,
    cacheStats: ReturnType<typeof getAuthCacheStats>,
    hotReloadStats: ReturnType<typeof getHotReloadStats>
  ): void {
    // Check memory usage
    if (isTurbopackMemoryUsageConcerning()) {
      authLogger.error(`[TURBOPACK-SAFEGUARDS] Concerning memory usage detected`, {
        stability: memoryStats.stability,
        currentHeapUsed: `${(memoryStats.currentHeapUsed / 1024 / 1024).toFixed(2)} MB`
      });
    }

    // Check hot reload frequency
    if (hotReloadStats.averageInterval && hotReloadStats.averageInterval < 3000) { // Less than 3 seconds apart
      const reloadsPerMinute = hotReloadStats.averageInterval > 0 ? 60000 / hotReloadStats.averageInterval : 0;
      if (reloadsPerMinute > this.maxHotReloadsPerMinute) {
        authLogger.warn(`[TURBOPACK-SAFEGUARDS] Excessive hot reload frequency detected`, {
          reloadsPerMinute: reloadsPerMinute.toFixed(2),
          maxAllowed: this.maxHotReloadsPerMinute,
          averageInterval: `${Math.round(hotReloadStats.averageInterval)}ms`
        });
      }
    }

    // Check for potential loops after hot reloads
    if (hotReloadStats.recentReloads > 5) {
      const loopDetected = originTracker.detectRecursiveLoops(10000, 3); // Check for loops in last 10 seconds
      if (loopDetected) {
        authLogger.warn(`[TURBOPACK-SAFEGUARDS] Potential authentication loop detected after hot reloads`);
      }
    }
  }

  /**
   * Setup hot reload handling
   */
  private setupHotReloadHandling(): void {
    // The hot reload handler is already set up in its own module
    // Here we just make sure it's working properly

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Hot reload handling configured`);
  }

  /**
   * Setup error handling for Turbopack-specific issues
   */
  private setupErrorHandling(): void {
    // Listen for unhandled rejections that might be Turbopack-specific
    if (typeof process !== 'undefined' && process.on) {
      process.on('unhandledRejection', (reason, promise) => {
        if (reason && typeof reason === 'object' && (reason as any).message) {
          const message = (reason as any).message as string;
          if (message.toLowerCase().includes('turbopack') || message.toLowerCase().includes('reload')) {
            authLogger.error(`[TURBOPACK-SAFEGUARDS] Turbopack-related unhandled rejection`, {
              message,
              stack: (reason as any).stack
            });
          }
        }
      });

      process.on('uncaughtException', (error) => {
        if (error.message.toLowerCase().includes('turbopack') || error.message.toLowerCase().includes('reload')) {
          authLogger.error(`[TURBOPACK-SAFEGUARDS] Turbopack-related uncaught exception`, {
            message: error.message,
            stack: error.stack
          });
        }
      });
    }

    authLogger.info(`[TURBOPACK-SAFEGUARDS] Error handling configured`);
  }

  /**
   * Get current safeguard status
   */
  getStatus(): TurbopackSafeguardStatus {
    const memoryStats = getTurbopackMemoryStats();
    const cacheStats = getAuthCacheStats();
    const hotReloadStats = getHotReloadStats();

    // Determine memory pressure
    let memoryPressure: 'normal' | 'warning' | 'critical' = 'normal';
    if (isTurbopackMemoryUsageConcerning()) {
      memoryPressure = memoryStats.stability === 'critical' ? 'critical' : 'warning';
    }

    // Determine cache efficiency
    let cacheEfficiency: 'high' | 'medium' | 'low' = 'high';
    if (cacheStats.misses > 0) {
      const hitRate = cacheStats.hits / (cacheStats.hits + cacheStats.misses);
      if (hitRate < 0.3) {
        cacheEfficiency = 'low';
      } else if (hitRate < 0.7) {
        cacheEfficiency = 'medium';
      }
    }

    // Determine hot reload frequency
    let hotReloadFrequency: 'normal' | 'high' | 'excessive' = 'normal';
    if (hotReloadStats.averageInterval && hotReloadStats.averageInterval > 0) {
      const reloadsPerMinute = 60000 / hotReloadStats.averageInterval;
      if (reloadsPerMinute > this.maxHotReloadsPerMinute * 1.5) {
        hotReloadFrequency = 'excessive';
      } else if (reloadsPerMinute > this.maxHotReloadsPerMinute) {
        hotReloadFrequency = 'high';
      }
    }

    return {
      isInitialized: this.isInitialized,
      memoryMonitoringActive: this.memoryMonitoringInterval !== null,
      cacheMonitoringActive: this.cacheMonitoringInterval !== null,
      hotReloadHandlingActive: true,
      memoryPressure,
      cacheEfficiency,
      hotReloadFrequency
    };
  }

  /**
   * Perform a manual health check
   */
  manualHealthCheck(): void {
    if (isDevMode()) {
      this.performHealthCheck();
    }
  }

  /**
   * Force cleanup of authentication state for Turbopack
   */
  forceStateCleanup(): void {
    if (isDevMode()) {
      authLogger.info(`[TURBOPACK-SAFEGUARDS] Forcing authentication state cleanup`);

      // Clear authentication state
      authStateManager.clearAuth();

      // Clear caches
      turbopackAuthCache.clear();

      // Clear trackers
      originTracker.clearRecords();

      authLogger.info(`[TURBOPACK-SAFEGUARDS] Authentication state cleanup completed`);
    }
  }

  /**
   * Generate a Turbopack-specific report
   */
  generateReport(): string {
    const status = this.getStatus();
    const memoryStats = getTurbopackMemoryStats();
    const cacheStats = getAuthCacheStats();
    const hotReloadStats = getHotReloadStats();

    let report = `=== TURBOPACK AUTHENTICATION SAFEGUARDS REPORT ===\n`;
    report += `Timestamp: ${new Date().toISOString()}\n`;
    report += `Initialized: ${status.isInitialized}\n`;
    report += `Memory Monitoring Active: ${status.memoryMonitoringActive}\n`;
    report += `Cache Monitoring Active: ${status.cacheMonitoringActive}\n`;
    report += `Hot Reload Handling Active: ${status.hotReloadHandlingActive}\n\n`;

    report += `MEMORY STATUS:\n`;
    report += `  Current Heap Used: ${(memoryStats.currentHeapUsed / 1024 / 1024).toFixed(2)} MB\n`;
    report += `  Auth Memory: ${(memoryStats.currentAuthMemory / 1024 / 1024).toFixed(2)} MB\n`;
    report += `  Stability: ${memoryStats.stability}\n`;
    report += `  Pressure: ${status.memoryPressure}\n\n`;

    report += `CACHE STATUS:\n`;
    report += `  Hits: ${cacheStats.hits}\n`;
    report += `  Misses: ${cacheStats.misses}\n`;
    report += `  Current Size: ${(cacheStats.currentSize / 1024 / 1024).toFixed(2)} MB\n`;
    report += `  Entries Count: ${cacheStats.entriesCount}\n`;
    report += `  Efficiency: ${status.cacheEfficiency}\n\n`;

    report += `HOT RELOAD STATUS:\n`;
    report += `  Total Reloads: ${hotReloadStats.totalReloads}\n`;
    report += `  Recent Reloads (5 min): ${hotReloadStats.recentReloads}\n`;
    report += `  Average Interval: ${hotReloadStats.averageInterval ? `${Math.round(hotReloadStats.averageInterval)}ms` : 'N/A'}\n`;
    report += `  Frequency: ${status.hotReloadFrequency}\n\n`;

    report += `RECOMMENDATIONS:\n`;

    if (status.memoryPressure !== 'normal') {
      report += `• Memory pressure is ${status.memoryPressure} - consider restarting dev server\n`;
    }

    if (status.cacheEfficiency !== 'high') {
      report += `• Cache efficiency is ${status.cacheEfficiency} - review caching strategy\n`;
    }

    if (status.hotReloadFrequency !== 'normal') {
      report += `• Hot reload frequency is ${status.hotReloadFrequency} - check for unnecessary changes\n`;
    }

    if (isHandlingHotReload()) {
      report += `• Currently handling hot reload - authentication may be unstable\n`;
    }

    report += `\n================================================\n`;

    return report;
  }

  /**
   * Stop all monitoring
   */
  stopMonitoring(): void {
    if (this.memoryMonitoringInterval) {
      turbopackMemoryMonitor.stopMonitoring();
      this.memoryMonitoringInterval = null;
    }

    if (this.cacheMonitoringInterval) {
      clearInterval(this.cacheMonitoringInterval);
      this.cacheMonitoringInterval = null;
    }

    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    this.isInitialized = false;

    authLogger.info(`[TURBOPACK-SAFEGUARDS] All monitoring stopped`);
  }

  /**
   * Restart monitoring
   */
  restartMonitoring(): void {
    this.stopMonitoring();
    this.initialize();
  }

  /**
   * Check if safeguards are active
   */
  areSafeguardsActive(): boolean {
    return this.isInitialized;
  }
}

export const turbopackSafeguards = TurbopackSafeguards.getInstance();

/**
 * Initialize Turbopack safeguards
 */
export function initializeTurbopackSafeguards(): void {
  if (isDevMode()) {
    turbopackSafeguards.initialize();
  }
}

/**
 * Get Turbopack safeguard status
 */
export function getTurbopackSafeguardStatus(): TurbopackSafeguardStatus {
  return turbopackSafeguards.getStatus();
}

/**
 * Perform manual health check
 */
export function performTurbopackManualHealthCheck(): void {
  turbopackSafeguards.manualHealthCheck();
}

/**
 * Force state cleanup for Turbopack
 */
export function forceTurbopackStateCleanup(): void {
  turbopackSafeguards.forceStateCleanup();
}

/**
 * Generate and log Turbopack report
 */
export function generateTurbopackSafeguardReport(): void {
  const report = turbopackSafeguards.generateReport();
  console.log(report);

  if (isDevMode()) {
    authLogger.info(`[TURBOPACK-SAFEGUARDS] Report generated`, {
      reportLength: report.length
    });
  }
}

/**
 * Stop Turbopack monitoring
 */
export function stopTurbopackMonitoring(): void {
  turbopackSafeguards.stopMonitoring();
}

/**
 * Restart Turbopack monitoring
 */
export function restartTurbopackMonitoring(): void {
  turbopackSafeguards.restartMonitoring();
}

/**
 * Check if Turbopack safeguards are active
 */
export function areTurbopackSafeguardsActive(): boolean {
  return turbopackSafeguards.areSafeguardsActive();
}

// Initialize safeguards in development mode
if (isDevMode()) {
  initializeTurbopackSafeguards();
}