/**
 * Development-Mode Safeguards for Authentication
 * Additional protections and monitoring specifically for development environments
 */

import { authLogger } from './logging';
import { originTracker } from './origin-tracker';
import { authStateManager } from './state-manager';
import { isDevMode, getDevSafeguards } from './config';
import { memoryMonitor } from './memory-monitor';
import { handleAuthError } from './error-handler';

// Global flag to track if dev safeguards are initialized
let devSafeguardsInitialized = false;

// Interval ID for periodic monitoring
let monitoringInterval: NodeJS.Timeout | null = null;

// Function to initialize development safeguards
export function initializeDevSafeguards(): void {
  if (!isDevMode() || devSafeguardsInitialized) {
    return;
  }

  authLogger.info('[DEV SAFEGUARDS] Initializing development-specific safeguards');

  // Enable detailed logging in development
  if (getDevSafeguards().enableDetailedLogging) {
    authLogger.info('[DEV SAFEGUARDS] Detailed logging enabled');
  }

  // Start periodic monitoring if enabled
  if (getDevSafeguards().enableLoopDetection) {
    startPeriodicMonitoring();
  }

  // Set up error monitoring
  setupErrorMonitoring();

  // Set up memory monitoring
  if (getDevSafeguards().enableStateManagement) {
    setupMemoryMonitoring();
  }

  devSafeguardsInitialized = true;
}

// Start periodic monitoring to detect potential issues
function startPeriodicMonitoring(): void {
  if (monitoringInterval) {
    clearInterval(monitoringInterval);
  }

  monitoringInterval = setInterval(() => {
    checkForPotentialIssues();
  }, 5000); // Check every 5 seconds

  authLogger.info('[DEV SAFEGUARDS] Periodic monitoring started');
}

// Check for potential issues in the authentication system
function checkForPotentialIssues(): void {
  if (!isDevMode()) {
    return;
  }

  // Check for verification loops
  const loopStatus = originTracker.checkLoopStatus();
  if (loopStatus.isLooping && loopStatus.details) {
    authLogger.error('[DEV SAFEGUARDS] Potential authentication verification loop detected', {
      origin: loopStatus.details.origin,
      path: loopStatus.details.path,
      count: loopStatus.details.count,
      timeWindowMs: loopStatus.details.timeWindowMs
    });

    // Log recent verification records for debugging
    const recentRecords = originTracker.getRecentRecords(10);
    authLogger.debug('[DEV SAFEGUARDS] Recent verification records:', {
      records: recentRecords.map(r => ({
        timestamp: new Date(r.timestamp).toISOString(),
        origin: r.origin,
        path: r.path,
        method: r.method,
        context: r.context
      }))
    });
  }

  // Check verification state
  const verificationStatus = authStateManager.getVerificationStatus();
  if (!verificationStatus.canVerify && verificationStatus.timeUntilRetry) {
    authLogger.warn('[DEV SAFEGUARDS] Verification is rate limited', {
      attemptsRemaining: verificationStatus.attemptsRemaining,
      timeUntilRetry: `${verificationStatus.timeUntilRetry}ms`
    });
  }

  // Check if approaching verification limit
  if (authStateManager.isApproachingVerificationLimit()) {
    const remaining = authStateManager.getRemainingAttempts();
    authLogger.warn('[DEV SAFEGUARDS] Approaching verification attempt limit', {
      remaining,
      maxAttempts: authStateManager['maxVerificationAttempts']
    });
  }

  // Check for high memory usage if monitoring is enabled
  if (memoryMonitor.isMemoryGrowthConcerning()) {
    authLogger.warn('[DEV SAFEGUARDS] Concerning memory growth detected');

    const trend = memoryMonitor.getMemoryTrend();
    authLogger.info('[DEV SAFEGUARDS] Memory trend analysis', {
      isGrowing: trend.isGrowing,
      averageGrowthRate: `${(trend.averageGrowthRate / 1024 / 1024).toFixed(2)} MB/min`,
      samples: trend.samples
    });
  }
}

// Set up error monitoring
function setupErrorMonitoring(): void {
  // Monitor unhandled promise rejections related to auth
  if (typeof process !== 'undefined') {
    process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
      if (reason && (reason.message || '').toLowerCase().includes('auth')) {
        authLogger.error('[DEV SAFEGUARDS] Unhandled auth-related promise rejection', {
          reason: reason.message || String(reason),
          stack: reason.stack,
          promise: promise.constructor.name
        });
      }
    });

    process.on('uncaughtException', (error: Error) => {
      if (error.message.toLowerCase().includes('auth') || error.message.toLowerCase().includes('token')) {
        authLogger.error('[DEV SAFEGUARDS] Uncaught auth-related exception', {
          message: error.message,
          stack: error.stack
        });
      }
    });
  }

  authLogger.info('[DEV SAFEGUARDS] Error monitoring initialized');
}

// Set up memory monitoring
function setupMemoryMonitoring(): void {
  if (typeof process !== 'undefined' && process.memoryUsage) {
    // Monitor memory usage periodically
    authLogger.info('[DEV SAFEGUARDS] Memory monitoring initialized');
  }
}

// Function to get development safeguard status
export function getDevSafeguardStatus(): {
  initialized: boolean;
  loopDetectionEnabled: boolean;
  detailedLoggingEnabled: boolean;
  memoryMonitoringEnabled: boolean;
  requestCountingEnabled: boolean;
  originTrackingEnabled: boolean;
  stateManagementEnabled: boolean;
  errorHandlingEnabled: boolean;
  currentVerificationStatus: ReturnType<typeof authStateManager.getVerificationStatus>;
  loopStatus: ReturnType<typeof originTracker.checkLoopStatus>;
} {
  const devSafeguards = getDevSafeguards();

  return {
    initialized: devSafeguardsInitialized,
    loopDetectionEnabled: devSafeguards.enableLoopDetection,
    detailedLoggingEnabled: devSafeguards.enableDetailedLogging,
    memoryMonitoringEnabled: devSafeguards.enableStateManagement,
    requestCountingEnabled: devSafeguards.enableRequestCounting,
    originTrackingEnabled: devSafeguards.enableOriginTracking,
    stateManagementEnabled: devSafeguards.enableStateManagement,
    errorHandlingEnabled: devSafeguards.enableErrorHandling,
    currentVerificationStatus: authStateManager.getVerificationStatus(),
    loopStatus: originTracker.checkLoopStatus()
  };
}

// Function to force a safeguard check (useful for debugging)
export function forceSafeguardCheck(): void {
  if (!isDevMode()) {
    return;
  }

  authLogger.info('[DEV SAFEGUARDS] Forced safeguard check initiated');
  checkForPotentialIssues();
}

// Function to reset development safeguards (useful for testing)
export function resetDevSafeguards(): void {
  if (!isDevMode()) {
    return;
  }

  authLogger.info('[DEV SAFEGUARDS] Resetting development safeguards');

  if (monitoringInterval) {
    clearInterval(monitoringInterval);
    monitoringInterval = null;
  }

  originTracker.clearRecords();
  devSafeguardsInitialized = false;

  authLogger.info('[DEV SAFEGUARDS] Development safeguards reset');
}

// Function to log all current safeguards status
export function logSafeguardsStatus(): void {
  if (!isDevMode()) {
    return;
  }

  const status = getDevSafeguardStatus();
  authLogger.info('[DEV SAFEGUARDS] Current safeguards status', status);

  // Log recent verification records
  const recentRecords = originTracker.getRecentRecords(20);
  authLogger.debug('[DEV SAFEGUARDS] Recent verification activity', {
    count: recentRecords.length,
    records: recentRecords.slice(0, 5).map(r => ({
      timestamp: new Date(r.timestamp).toISOString(),
      origin: r.origin,
      path: r.path,
      context: r.context
    }))
  });

  // Log origin statistics
  const originStats = originTracker.getOriginStats();
  authLogger.debug('[DEV SAFEGUARDS] Verification origin statistics', originStats);
}

// Initialize safeguards when module is loaded (in development mode)
if (isDevMode()) {
  initializeDevSafeguards();

  // Log initialization
  authLogger.info('[DEV SAFEGUARDS] Module loaded and safeguards active');
}

// Export a function to manually trigger safeguards initialization
// (useful if imported in an environment where isDevMode() might not be accurate initially)
export function ensureDevSafeguardsInitialized(): void {
  if (!devSafeguardsInitialized && isDevMode()) {
    initializeDevSafeguards();
  }
}