/**
 * Environment-Specific Authentication Configuration
 * Provides configuration settings based on the current environment
 * to enable appropriate safeguards and behaviors
 */

export interface AuthConfig {
  // Environment settings
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
  envName: string;

  // Verification settings
  maxVerificationAttempts: number;
  verificationRetryDelay: number;
  verificationTimeout: number;

  // Circuit breaker settings
  circuitBreaker: {
    failureThreshold: number;
    timeoutMs: number;
    successThreshold: number;
  };

  // Memory and performance settings
  memoryMonitoringEnabled: boolean;
  memoryThreshold: number;

  // Development-specific safeguards
  devSafeguards: {
    enableLoopDetection: boolean;
    enableDetailedLogging: boolean;
    enableRequestCounting: boolean;
    enableOriginTracking: boolean;
    enableStateManagement: boolean;
    enableErrorHandling: boolean;
    maxRequestCountPerMinute: number;
  };

  // Security settings
  tokenRefreshThreshold: number; // Percentage of token life remaining when to refresh
  secureCookies: boolean;
  sameSitePolicy: 'strict' | 'lax' | 'none';

  // API settings
  apiTimeout: number;
  maxConcurrentRequests: number;
}

class AuthConfigManager {
  private static instance: AuthConfigManager;
  private config: AuthConfig;

  private constructor() {
    this.config = this.buildConfig();
  }

  static getInstance(): AuthConfigManager {
    if (!AuthConfigManager.instance) {
      AuthConfigManager.instance = new AuthConfigManager();
    }
    return AuthConfigManager.instance;
  }

  /**
   * Build configuration based on environment
   */
  private buildConfig(): AuthConfig {
    // Determine environment
    const nodeEnv = process.env.NODE_ENV || 'development';
    const vercelEnv = process.env.VERCEL_ENV;
    const nextEnv = process.env.NEXT_PUBLIC_ENV;

    const isDevelopment =
      nodeEnv === 'development' ||
      nextEnv === 'development' ||
      (!vercelEnv && !nextEnv) ||
      false;

    const isProduction =
      nodeEnv === 'production' ||
      vercelEnv === 'production' ||
      nextEnv === 'production';

    const isTest =
      nodeEnv === 'test' ||
      nextEnv === 'test';

    // Base configuration
    const baseConfig: AuthConfig = {
      isDevelopment,
      isProduction,
      isTest,
      envName: isProduction ? 'production' : isTest ? 'test' : 'development',

      // Verification settings
      maxVerificationAttempts: isDevelopment ? 3 : 5, // Lower in dev to catch loops faster
      verificationRetryDelay: isDevelopment ? 500 : 1000, // Faster in dev
      verificationTimeout: isDevelopment ? 10000 : 15000, // 10s in dev, 15s in prod

      // Circuit breaker settings
      circuitBreaker: {
        failureThreshold: isDevelopment ? 3 : 5, // Trip faster in development
        timeoutMs: isDevelopment ? 30000 : 60000, // 30s in dev, 1min in prod
        successThreshold: isDevelopment ? 1 : 3 // Close faster in development
      },

      // Memory and performance settings
      memoryMonitoringEnabled: isDevelopment, // Enabled in dev to catch issues early
      memoryThreshold: isDevelopment ? 0.7 : 0.85, // Lower threshold in dev

      // Development-specific safeguards
      devSafeguards: {
        enableLoopDetection: true,
        enableDetailedLogging: isDevelopment,
        enableRequestCounting: true,
        enableOriginTracking: true,
        enableStateManagement: true,
        enableErrorHandling: true,
        maxRequestCountPerMinute: isDevelopment ? 20 : 100 // Lower in dev to catch spam
      },

      // Security settings
      tokenRefreshThreshold: 0.2, // Refresh when 20% of token life remains
      secureCookies: isProduction, // Only use secure cookies in production
      sameSitePolicy: isProduction ? 'none' : 'lax', // Cross-site requests in production

      // API settings
      apiTimeout: isDevelopment ? 10000 : 30000, // 10s in dev, 30s in prod
      maxConcurrentRequests: isDevelopment ? 5 : 10 // Fewer concurrent requests in dev
    };

    return baseConfig;
  }

  /**
   * Get current configuration
   */
  getConfig(): AuthConfig {
    return { ...this.config };
  }

  /**
   * Get environment-specific settings
   */
  getEnvironmentSettings(): Pick<AuthConfig, 'isDevelopment' | 'isProduction' | 'isTest' | 'envName'> {
    return {
      isDevelopment: this.config.isDevelopment,
      isProduction: this.config.isProduction,
      isTest: this.config.isTest,
      envName: this.config.envName
    };
  }

  /**
   * Check if running in development mode
   */
  isDevelopment(): boolean {
    return this.config.isDevelopment;
  }

  /**
   * Check if running in production mode
   */
  isProduction(): boolean {
    return this.config.isProduction;
  }

  /**
   * Check if running in test mode
   */
  isTest(): boolean {
    return this.config.isTest;
  }

  /**
   * Get verification settings
   */
  getVerificationSettings(): Pick<AuthConfig, 'maxVerificationAttempts' | 'verificationRetryDelay' | 'verificationTimeout'> {
    return {
      maxVerificationAttempts: this.config.maxVerificationAttempts,
      verificationRetryDelay: this.config.verificationRetryDelay,
      verificationTimeout: this.config.verificationTimeout
    };
  }

  /**
   * Get circuit breaker settings
   */
  getCircuitBreakerSettings(): AuthConfig['circuitBreaker'] {
    return this.config.circuitBreaker;
  }

  /**
   * Get development safeguards settings
   */
  getDevSafeguards(): AuthConfig['devSafeguards'] {
    return this.config.devSafeguards;
  }

  /**
   * Check if a specific safeguard is enabled
   */
  isSafeguardEnabled(safeguard: keyof AuthConfig['devSafeguards']): boolean {
    return this.config.devSafeguards[safeguard] as boolean;
  }

  /**
   * Get security settings
   */
  getSecuritySettings(): Pick<AuthConfig, 'tokenRefreshThreshold' | 'secureCookies' | 'sameSitePolicy'> {
    return {
      tokenRefreshThreshold: this.config.tokenRefreshThreshold,
      secureCookies: this.config.secureCookies,
      sameSitePolicy: this.config.sameSitePolicy
    };
  }

  /**
   * Get API settings
   */
  getApiSettings(): Pick<AuthConfig, 'apiTimeout' | 'maxConcurrentRequests'> {
    return {
      apiTimeout: this.config.apiTimeout,
      maxConcurrentRequests: this.config.maxConcurrentRequests
    };
  }

  /**
   * Update configuration (useful for testing)
   */
  updateConfig(updates: Partial<AuthConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  /**
   * Reset configuration to environment defaults
   */
  resetConfig(): void {
    this.config = this.buildConfig();
  }
}

export const authConfig = AuthConfigManager.getInstance();

/**
 * Convenience functions for common checks
 */

export function isDevMode(): boolean {
  return authConfig.isDevelopment();
}

export function isProdMode(): boolean {
  return authConfig.isProduction();
}

export function isTestMode(): boolean {
  return authConfig.isTest();
}

export function shouldEnableDetailedLogging(): boolean {
  return authConfig.getConfig().devSafeguards.enableDetailedLogging;
}

export function getMaxVerificationAttempts(): number {
  return authConfig.getConfig().maxVerificationAttempts;
}

export function getVerificationRetryDelay(): number {
  return authConfig.getConfig().verificationRetryDelay;
}

export function getVerificationTimeout(): number {
  return authConfig.getConfig().verificationTimeout;
}

export function getCircuitBreakerSettings() {
  return authConfig.getCircuitBreakerSettings();
}

export function getDevSafeguards() {
  return authConfig.getDevSafeguards();
}

export function isLoopDetectionEnabled(): boolean {
  return authConfig.isSafeguardEnabled('enableLoopDetection');
}

export function isRequestCountingEnabled(): boolean {
  return authConfig.isSafeguardEnabled('enableRequestCounting');
}

export function isOriginTrackingEnabled(): boolean {
  return authConfig.isSafeguardEnabled('enableOriginTracking');
}

export function isStateManagementEnabled(): boolean {
  return authConfig.isSafeguardEnabled('enableStateManagement');
}

export function isMemoryMonitoringEnabled(): boolean {
  return authConfig.getConfig().memoryMonitoringEnabled;
}

export function getMemoryThreshold(): number {
  return authConfig.getConfig().memoryThreshold;
}