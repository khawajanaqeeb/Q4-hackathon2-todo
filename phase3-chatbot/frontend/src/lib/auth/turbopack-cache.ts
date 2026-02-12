/**
 * Turbopack-Specific Authentication Caching
 * Implements caching strategies optimized for Turbopack's hot reloading behavior
 */

import { authLogger } from './logging';
import { isDevMode } from './config';
import { authStateManager } from './state-manager';

export interface CacheEntry<T = any> {
  value: T;
  timestamp: number;
  ttl: number; // time to live in milliseconds
  size: number; // estimated size in bytes
  tags: string[]; // cache tags for invalidation
}

export interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  currentSize: number;
  maxSize: number;
  entriesCount: number;
}

export interface TurbopackCacheOptions {
  maxSize?: number; // Maximum cache size in bytes
  defaultTTL?: number; // Default time to live in milliseconds
  enableCompression?: boolean; // Whether to compress cached values
  enablePersistence?: boolean; // Whether to persist to localStorage
  persistenceKey?: string; // Key for localStorage
}

class TurbopackAuthCache {
  private static instance: TurbopackAuthCache;
  private cache: Map<string, CacheEntry> = new Map();
  private stats: CacheStats = {
    hits: 0,
    misses: 0,
    evictions: 0,
    currentSize: 0,
    maxSize: 10 * 1024 * 1024, // 10MB default
    entriesCount: 0
  };
  private options: Required<TurbopackCacheOptions>;

  private constructor(options: TurbopackCacheOptions = {}) {
    this.options = {
      maxSize: options.maxSize ?? 10 * 1024 * 1024, // 10MB
      defaultTTL: options.defaultTTL ?? 5 * 60 * 1000, // 5 minutes
      enableCompression: options.enableCompression ?? false,
      enablePersistence: options.enablePersistence ?? isDevMode(), // Enable in dev mode for debugging
      persistenceKey: options.persistenceKey ?? 'auth-turbopack-cache'
    };

    // Restore cache from persistence if enabled
    if (this.options.enablePersistence) {
      this.restoreFromPersistence();
    }

    // Set up cleanup interval
    this.startCleanupInterval();
  }

  static getInstance(options?: TurbopackCacheOptions): TurbopackAuthCache {
    if (!TurbopackAuthCache.instance) {
      TurbopackAuthCache.instance = new TurbopackAuthCache(options);
    }
    return TurbopackAuthCache.instance;
  }

  /**
   * Set a value in the cache
   */
  set<T = any>(key: string, value: T, ttl?: number, tags: string[] = []): boolean {
    // Check if we need to make space
    if (this.stats.currentSize >= this.options.maxSize) {
      this.evictOldestEntries();
    }

    // Estimate size of the value
    const size = this.estimateSize(value);

    // Create cache entry
    const cacheEntry: CacheEntry<T> = {
      value,
      timestamp: Date.now(),
      ttl: ttl ?? this.options.defaultTTL,
      size,
      tags
    };

    // Check if adding this entry would exceed max size
    if (size > this.options.maxSize) {
      authLogger.warn(`[TURBOPACK-CACHE] Value too large to cache (key: ${key})`, {
        valueSize: size,
        maxSize: this.options.maxSize
      });
      return false;
    }

    // Remove old entry if exists
    const oldEntry = this.cache.get(key);
    if (oldEntry) {
      this.stats.currentSize -= oldEntry.size;
    }

    // Add new entry
    this.cache.set(key, cacheEntry);
    this.stats.currentSize += size;
    this.stats.entriesCount++;

    authLogger.debug(`[TURBOPACK-CACHE] Set value (key: ${key})`, {
      size,
      ttl: cacheEntry.ttl,
      totalSize: this.stats.currentSize
    });

    return true;
  }

  /**
   * Get a value from the cache
   */
  get<T = any>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      this.stats.misses++;
      return null;
    }

    // Check if entry is expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.stats.currentSize -= entry.size;
      this.stats.entriesCount--;
      this.stats.evictions++;

      authLogger.debug(`[TURBOPACK-CACHE] Entry expired (key: ${key})`, {
        age: Date.now() - entry.timestamp,
        ttl: entry.ttl
      });

      return null;
    }

    this.stats.hits++;

    authLogger.debug(`[TURBOPACK-CACHE] Retrieved value (key: ${key})`, {
      size: entry.size,
      age: Date.now() - entry.timestamp
    });

    return entry.value as T;
  }

  /**
   * Check if a key exists in the cache
   */
  has(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    // Check if expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      this.stats.currentSize -= entry.size;
      this.stats.entriesCount--;
      this.stats.evictions++;
      return false;
    }

    return true;
  }

  /**
   * Delete a key from the cache
   */
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (entry) {
      this.cache.delete(key);
      this.stats.currentSize -= entry.size;
      this.stats.entriesCount--;
      return true;
    }
    return false;
  }

  /**
   * Clear all cache entries
   */
  clear(): void {
    this.cache.clear();
    this.stats.currentSize = 0;
    this.stats.entriesCount = 0;
    this.stats.hits = 0;
    this.stats.misses = 0;
    this.stats.evictions = 0;

    authLogger.info(`[TURBOPACK-CACHE] Cache cleared`);

    // Clear persistent storage if enabled
    if (this.options.enablePersistence && typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.options.persistenceKey);
    }
  }

  /**
   * Invalidate entries by tag
   */
  invalidateByTag(tag: string): number {
    let invalidatedCount = 0;
    const keysToDelete: string[] = [];

    for (const [key, entry] of this.cache.entries()) {
      if (entry.tags.includes(tag)) {
        keysToDelete.push(key);
        invalidatedCount++;
      }
    }

    for (const key of keysToDelete) {
      const entry = this.cache.get(key);
      if (entry) {
        this.cache.delete(key);
        this.stats.currentSize -= entry.size;
        this.stats.entriesCount--;
        this.stats.evictions++;
      }
    }

    authLogger.debug(`[TURBOPACK-CACHE] Invalidated entries by tag '${tag}'`, {
      count: invalidatedCount
    });

    return invalidatedCount;
  }

  /**
   * Get cache statistics
   */
  getStats(): CacheStats {
    return { ...this.stats };
  }

  /**
   * Get cache size in bytes
   */
  getSize(): number {
    return this.stats.currentSize;
  }

  /**
   * Get the number of entries in the cache
   */
  getEntryCount(): number {
    return this.stats.entriesCount;
  }

  /**
   * Estimate the size of a value in bytes
   */
  private estimateSize(value: any): number {
    try {
      if (value === null || value === undefined) {
        return 0;
      }

      if (typeof value === 'string') {
        return value.length * 2; // UTF-16 characters are 2 bytes
      }

      if (typeof value === 'number') {
        return 8; // Numbers are 8 bytes in JavaScript
      }

      if (typeof value === 'boolean') {
        return 4; // Booleans are 4 bytes
      }

      if (Array.isArray(value)) {
        return value.reduce((sum, item) => sum + this.estimateSize(item), 0);
      }

      if (typeof value === 'object') {
        const serialized = JSON.stringify(value);
        return serialized.length * 2; // UTF-16
      }

      // For functions, dates, etc., return a conservative estimate
      return 100;
    } catch (error) {
      authLogger.error(`[TURBOPACK-CACHE] Error estimating size`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return 100; // Conservative estimate
    }
  }

  /**
   * Evict the oldest entries to make space
   */
  private evictOldestEntries(): void {
    // Sort entries by timestamp (oldest first)
    const sortedEntries = Array.from(this.cache.entries())
      .map(([key, entry]) => ({ key, entry, age: Date.now() - entry.timestamp }))
      .sort((a, b) => a.age - b.age);

    // Remove oldest entries until we have enough space
    let freedSpace = 0;
    const targetFreeSpace = this.options.maxSize * 0.2; // Free up 20% of max size

    for (const { key, entry } of sortedEntries) {
      if (freedSpace >= targetFreeSpace) break;

      this.cache.delete(key);
      this.stats.currentSize -= entry.size;
      this.stats.entriesCount--;
      this.stats.evictions++;
      freedSpace += entry.size;
    }

    authLogger.debug(`[TURBOPACK-CACHE] Evicted entries to make space`, {
      freedSpace,
      entriesEvicted: sortedEntries.length,
      newSize: this.stats.currentSize
    });
  }

  /**
   * Start cleanup interval to remove expired entries
   */
  private startCleanupInterval(): void {
    // Only run cleanup in development mode to save resources in production
    if (isDevMode()) {
      setInterval(() => {
        this.cleanupExpired();
      }, 30000); // Cleanup every 30 seconds
    }
  }

  /**
   * Remove expired entries
   */
  private cleanupExpired(): void {
    const now = Date.now();
    let cleanedCount = 0;
    let freedSpace = 0;

    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
        this.stats.currentSize -= entry.size;
        this.stats.entriesCount--;
        this.stats.evictions++;
        cleanedCount++;
        freedSpace += entry.size;
      }
    }

    if (cleanedCount > 0) {
      authLogger.debug(`[TURBOPACK-CACHE] Cleaned up expired entries`, {
        cleanedCount,
        freedSpace
      });
    }
  }

  /**
   * Persist cache to localStorage
   */
  private persistToStorage(): void {
    if (!this.options.enablePersistence || typeof localStorage === 'undefined') {
      return;
    }

    try {
      // Only persist non-expired entries
      const validEntries: [string, CacheEntry][] = [];
      const now = Date.now();

      for (const [key, entry] of this.cache.entries()) {
        if (now - entry.timestamp <= entry.ttl) {
          validEntries.push([key, entry]);
        }
      }

      const dataToPersist = {
        entries: validEntries,
        stats: this.stats
      };

      const serialized = JSON.stringify(dataToPersist);
      localStorage.setItem(this.options.persistenceKey, serialized);

      authLogger.debug(`[TURBOPACK-CACHE] Persisted to localStorage`, {
        entriesCount: validEntries.length,
        dataSize: serialized.length
      });
    } catch (error) {
      authLogger.error(`[TURBOPACK-CACHE] Error persisting to localStorage`, {
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * Restore cache from localStorage
   */
  private restoreFromPersistence(): void {
    if (!this.options.enablePersistence || typeof localStorage === 'undefined') {
      return;
    }

    try {
      const serialized = localStorage.getItem(this.options.persistenceKey);
      if (!serialized) {
        return;
      }

      const data = JSON.parse(serialized);
      const now = Date.now();

      // Restore entries, filtering out expired ones
      for (const [key, entry] of data.entries as [string, CacheEntry][]) {
        // Check if entry hasn't expired since persistence
        if (now - entry.timestamp <= entry.ttl) {
          this.cache.set(key, entry);
          this.stats.currentSize += entry.size;
        }
      }

      // Restore stats (with some adjustments)
      this.stats = { ...data.stats };
      this.stats.entriesCount = this.cache.size;

      authLogger.debug(`[TURBOPACK-CACHE] Restored from localStorage`, {
        entriesRestored: this.cache.size,
        restoredSize: this.stats.currentSize
      });
    } catch (error) {
      authLogger.error(`[TURBOPACK-CACHE] Error restoring from localStorage`, {
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  /**
   * Handle Turbopack hot reload - clear volatile cache entries
   */
  handleHotReload(): void {
    // Invalidate authentication-related cache entries on hot reload
    // since authentication state might be inconsistent after reload
    this.invalidateByTag('auth-state');
    this.invalidateByTag('verification-result');
    this.invalidateByTag('user-data');

    authLogger.info(`[TURBOPACK-CACHE] Handled hot reload - invalidated auth-related entries`);
  }
}

export const turbopackAuthCache = TurbopackAuthCache.getInstance();

/**
 * Cache authentication token
 */
export function cacheAuthToken(token: string, ttl?: number): boolean {
  return turbopackAuthCache.set('auth_token', token, ttl, ['auth-state']);
}

/**
 * Get cached authentication token
 */
export function getCachedAuthToken(): string | null {
  return turbopackAuthCache.get('auth_token');
}

/**
 * Cache user information
 */
export function cacheUser(user: any, ttl?: number): boolean {
  return turbopackAuthCache.set('user_info', user, ttl, ['user-data']);
}

/**
 * Get cached user information
 */
export function getCachedUser(): any | null {
  return turbopackAuthCache.get('user_info');
}

/**
 * Cache verification result
 */
export function cacheVerificationResult(result: any, ttl?: number): boolean {
  return turbopackAuthCache.set('verification_result', result, ttl, ['verification-result']);
}

/**
 * Get cached verification result
 */
export function getCachedVerificationResult(): any | null {
  return turbopackAuthCache.get('verification_result');
}

/**
 * Clear authentication cache
 */
export function clearAuthCache(): void {
  turbopackAuthCache.delete('auth_token');
  turbopackAuthCache.delete('user_info');
  turbopackAuthCache.delete('verification_result');
  turbopackAuthCache.invalidateByTag('auth-state');
  turbopackAuthCache.invalidateByTag('user-data');
  turbopackAuthCache.invalidateByTag('verification-result');
}

/**
 * Handle hot reload event
 */
export function handleTurbopackHotReload(): void {
  turbopackAuthCache.handleHotReload();
}

/**
 * Get cache statistics
 */
export function getAuthCacheStats() {
  return turbopackAuthCache.getStats();
}

/**
 * Persist cache to storage (manually trigger)
 */
export function persistAuthCache(): void {
  turbopackAuthCache['persistToStorage']?.call(turbopackAuthCache);
}

/**
 * Check if authentication token is cached
 */
export function isAuthTokenCached(): boolean {
  return turbopackAuthCache.has('auth_token');
}