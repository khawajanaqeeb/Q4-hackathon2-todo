/**
 * Turbopack Hot Reload Handler for Authentication
 * Manages authentication state during Turbopack hot reloads to prevent inconsistencies
 */

import { authLogger } from './logging';
import { authStateManager } from './state-manager';
import { originTracker } from './origin-tracker';
import { depthTracker } from './depth-tracker';
import { turbopackAuthCache, handleTurbopackHotReload } from './turbopack-cache';
import { isDevMode } from './config';

export interface HotReloadContext {
  reason: 'hot-update' | 'full-reload' | 'module-reload' | 'unknown';
  timestamp: number;
  affectedModules?: string[];
  previousState?: any;
}

class HotReloadHandler {
  private static instance: HotReloadHandler;
  private reloadHistory: HotReloadContext[] = [];
  private maxHistory = 50;
  private isHandlingReload = false;
  private lastReloadTime = 0;
  private reloadDebounceTimer: NodeJS.Timeout | null = null;
  private reloadCooldownMs = 1000; // 1 second cooldown between reloads

  private constructor() {}

  static getInstance(): HotReloadHandler {
    if (!HotReloadHandler.instance) {
      HotReloadHandler.instance = new HotReloadHandler();
    }
    return HotReloadHandler.instance;
  }

  /**
   * Handle a hot reload event
   */
  handleHotReload(context: Omit<HotReloadContext, 'timestamp'>): void {
    const now = Date.now();

    // Debounce reloads that happen too quickly
    if (now - this.lastReloadTime < this.reloadCooldownMs) {
      authLogger.debug(`[HOT-RELOAD-HANDLER] Reload debounced (too frequent)`);

      if (this.reloadDebounceTimer) {
        clearTimeout(this.reloadDebounceTimer);
      }

      this.reloadDebounceTimer = setTimeout(() => {
        this.processReload({ ...context, timestamp: now });
      }, this.reloadCooldownMs - (now - this.lastReloadTime));

      return;
    }

    this.processReload({ ...context, timestamp: now });
  }

  /**
   * Process the reload event with proper authentication state management
   */
  private processReload(context: HotReloadContext): void {
    if (this.isHandlingReload) {
      authLogger.warn(`[HOT-RELOAD-HANDLER] Already handling a reload, skipping`);
      return;
    }

    this.isHandlingReload = true;
    this.lastReloadTime = context.timestamp;

    authLogger.info(`[HOT-RELOAD-HANDLER] Processing hot reload`, {
      reason: context.reason,
      timestamp: new Date(context.timestamp).toISOString(),
      affectedModules: context.affectedModules?.length || 0
    });

    try {
      // Save current state before reset
      const currentState = {
        isAuthenticated: authStateManager.isAuthenticated(),
        user: authStateManager.getUser(),
        state: authStateManager.getState()
      };

      // Update reload history
      this.reloadHistory.push(context);
      if (this.reloadHistory.length > this.maxHistory) {
        this.reloadHistory = this.reloadHistory.slice(-this.maxHistory);
      }

      // Reset authentication state management
      this.resetAuthStateForReload();

      // Clear caches that might be inconsistent after reload
      this.clearVolatileCaches();

      // Reset tracking systems
      this.resetTrackingSystems();

      // Log the completion
      authLogger.info(`[HOT-RELOAD-HANDLER] Completed hot reload handling`, {
        reason: context.reason,
        newState: {
          isAuthenticated: authStateManager.isAuthenticated(),
          user: authStateManager.getUser()
        }
      });

    } catch (error) {
      authLogger.error(`[HOT-RELOAD-HANDLER] Error handling hot reload`, {
        error: error instanceof Error ? error.message : String(error),
        reason: context.reason
      });
    } finally {
      this.isHandlingReload = false;
    }
  }

  /**
   * Reset authentication state for reload
   */
  private resetAuthStateForReload(): void {
    // Preserve authentication status but reset verification state
    const wasAuthenticated = authStateManager.isAuthenticated();
    const user = authStateManager.getUser();

    // Clear verification state but preserve user info
    authStateManager.clearAuth();

    // Restore authentication status if it was previously authenticated
    // (but keep verification as incomplete to force re-verification)
    if (wasAuthenticated && user) {
      authStateManager.setToken('preserved'); // Placeholder token
      authStateManager.setUser(user);
      // Note: The actual token will be re-verified separately
    }

    authLogger.debug(`[HOT-RELOAD-HANDLER] Reset auth state`, {
      wasAuthenticated,
      hasUser: !!user
    });
  }

  /**
   * Clear volatile caches that might be inconsistent after reload
   */
  private clearVolatileCaches(): void {
    // Handle Turbopack-specific cache invalidation
    handleTurbopackHotReload();

    authLogger.debug(`[HOT-RELOAD-HANDLER] Cleared volatile caches`);
  }

  /**
   * Reset tracking systems after reload
   */
  private resetTrackingSystems(): void {
    // Clear origin tracker to prevent false loop detection after reload
    originTracker.clearRecords();

    // Reset depth tracker
    depthTracker.reset();

    authLogger.debug(`[HOT-RELOAD-HANDLER] Reset tracking systems`);
  }

  /**
   * Check if we're currently handling a reload
   */
  isHandlingReload(): boolean {
    return this.isHandlingReload;
  }

  /**
   * Get reload history
   */
  getReloadHistory(): HotReloadContext[] {
    return [...this.reloadHistory];
  }

  /**
   * Get statistics about reloads
   */
  getReloadStats(): {
    totalReloads: number;
    recentReloads: number; // Last 5 minutes
    lastReloadTime: number | null;
    averageInterval: number | null; // Average time between reloads
    byReason: Record<string, number>;
  } {
    const now = Date.now();
    const fiveMinutesAgo = now - (5 * 60 * 1000);

    const recentReloads = this.reloadHistory.filter(r => r.timestamp >= fiveMinutesAgo);
    const byReason: Record<string, number> = {};

    this.reloadHistory.forEach(reload => {
      byReason[reload.reason] = (byReason[reload.reason] || 0) + 1;
    });

    // Calculate average interval
    let averageInterval = null;
    if (this.reloadHistory.length > 1) {
      const intervals = [];
      for (let i = 1; i < this.reloadHistory.length; i++) {
        intervals.push(this.reloadHistory[i].timestamp - this.reloadHistory[i - 1].timestamp);
      }
      averageInterval = intervals.reduce((sum, val) => sum + val, 0) / intervals.length;
    }

    return {
      totalReloads: this.reloadHistory.length,
      recentReloads: recentReloads.length,
      lastReloadTime: this.reloadHistory.length > 0 ? this.reloadHistory[this.reloadHistory.length - 1].timestamp : null,
      averageInterval,
      byReason
    };
  }

  /**
   * Register hot reload listener for browser environments
   */
  registerHotReloadListener(): void {
    if (typeof window === 'undefined') {
      // Server-side, nothing to do
      return;
    }

    // Check for Webpack/Next.js hot module replacement
    if ((module as any).hot) {
      (module as any).hot.addStatusHandler((status: string) => {
        if (status === 'apply' || status === 'ready') {
          this.handleHotReload({
            reason: 'hot-update',
            affectedModules: [] // We don't track specific modules for auth purposes
          });
        }
      });

      // Listen for hot update events
      (module as any).hot.addDisposeHandler(() => {
        authLogger.debug(`[HOT-RELOAD-HANDLER] Module disposing, preparing for reload`);
      });

      authLogger.info(`[HOT-RELOAD-HANDLER] Registered hot reload listener`);
    }

    // For Turbopack specifically, listen to Turbopack events if available
    this.setupTurbopackListener();
  }

  /**
   * Setup Turbopack-specific listener
   */
  private setupTurbopackListener(): void {
    if (typeof window === 'undefined') {
      return;
    }

    // Check for Turbopack-specific global variables
    if ((window as any).__TURBOPACK__) {
      // Turbopack might expose specific APIs for listening to reloads
      authLogger.info(`[HOT-RELOAD-HANDLER] Turbopack detected, setting up specific listener`);

      // For now, we'll use a generic approach
      // In the future, we might use Turbopack-specific events
    }

    // Listen for beforeunload to prepare for reloads
    window.addEventListener('beforeunload', () => {
      authLogger.debug(`[HOT-RELOAD-HANDLER] Page unload detected, preparing for reload/reset`);
    });
  }

  /**
   * Get reload status
   */
  getReloadStatus(): {
    isHandlingReload: boolean;
    lastReloadTime: number | null;
    timeSinceLastReload: number | null;
    shouldWaitBeforeAuth: boolean;
  } {
    const now = Date.now();
    const timeSinceLastReload = this.lastReloadTime ? now - this.lastReloadTime : null;

    return {
      isHandlingReload: this.isHandlingReload,
      lastReloadTime: this.lastReloadTime || null,
      timeSinceLastReload,
      // Wait a bit after reload before attempting authentication
      shouldWaitBeforeAuth: timeSinceLastReload !== null && timeSinceLastReload < 1000 // 1 second
    };
  }

  /**
   * Wait for reload to complete before proceeding
   */
  async waitForReloadComplete(timeoutMs: number = 5000): Promise<boolean> {
    const startTime = Date.now();

    while (this.isHandlingReload && (Date.now() - startTime) < timeoutMs) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    return !this.isHandlingReload;
  }

  /**
   * Clear reload history
   */
  clearHistory(): void {
    this.reloadHistory = [];
    authLogger.debug(`[HOT-RELOAD-HANDLER] Reload history cleared`);
  }

  /**
   * Reset the entire handler state
   */
  reset(): void {
    this.reloadHistory = [];
    this.isHandlingReload = false;
    this.lastReloadTime = 0;

    if (this.reloadDebounceTimer) {
      clearTimeout(this.reloadDebounceTimer);
      this.reloadDebounceTimer = null;
    }

    authLogger.info(`[HOT-RELOAD-HANDLER] Handler state reset`);
  }
}

export const hotReloadHandler = HotReloadHandler.getInstance();

/**
 * Handle hot reload event
 */
export function handleHotReload(context: Omit<HotReloadContext, 'timestamp'>): void {
  hotReloadHandler.handleHotReload(context);
}

/**
 * Register hot reload listeners
 */
export function registerHotReloadListeners(): void {
  hotReloadHandler.registerHotReloadListener();
}

/**
 * Check if reload is being handled
 */
export function isHandlingHotReload(): boolean {
  return hotReloadHandler.isHandlingReload();
}

/**
 * Get reload status
 */
export function getHotReloadStatus() {
  return hotReloadHandler.getReloadStatus();
}

/**
 * Wait for reload to complete
 */
export async function waitForHotReloadComplete(timeoutMs: number = 5000): Promise<boolean> {
  return hotReloadHandler.waitForReloadComplete(timeoutMs);
}

/**
 * Get reload statistics
 */
export function getHotReloadStats() {
  return hotReloadHandler.getReloadStats();
}

/**
 * Get reload history
 */
export function getHotReloadHistory() {
  return hotReloadHandler.getReloadHistory();
}

/**
 * Initialize hot reload handling for development
 */
export function initializeHotReloadHandling(): void {
  if (isDevMode()) {
    registerHotReloadListeners();
    authLogger.info(`[HOT-RELOAD-HANDLER] Initialized for development mode`);
  }
}

// Initialize hot reload handling if in development mode
if (isDevMode() && typeof window !== 'undefined') {
  setTimeout(() => {
    initializeHotReloadHandling();
  }, 100); // Delay slightly to ensure module system is ready
}