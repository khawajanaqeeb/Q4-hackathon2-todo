/**
 * Development environment detection utilities for authentication
 * Helps differentiate between development and production for special handling
 */

export interface EnvironmentConfig {
  isDevelopment: boolean;
  isProduction: boolean;
  isTest: boolean;
  envName: string;
  isDevModeWithSpecialHandling: boolean;
}

/**
 * Get environment configuration
 */
export function getEnvironmentConfig(): EnvironmentConfig {
  // Check various environment indicators
  const nodeEnv = process.env.NODE_ENV || 'development';
  const vercelEnv = process.env.VERCEL_ENV;
  const nextEnv = process.env.NEXT_PUBLIC_ENV;

  // Determine environment based on multiple indicators
  const isDevelopment =
    nodeEnv === 'development' ||
    nextEnv === 'development' ||
    (!vercelEnv && !nextEnv) || // Default to development if no env vars set
    false;

  const isProduction =
    nodeEnv === 'production' ||
    vercelEnv === 'production' ||
    nextEnv === 'production';

  const isTest =
    nodeEnv === 'test' ||
    process.env.NODE_ENV === 'test' ||
    nextEnv === 'test';

  return {
    isDevelopment,
    isProduction,
    isTest,
    envName: isProduction ? 'production' : isTest ? 'test' : 'development',
    isDevModeWithSpecialHandling: isDevelopment
  };
}

/**
 * Check if running in development mode
 */
export function isDevelopment(): boolean {
  return getEnvironmentConfig().isDevelopment;
}

/**
 * Check if running in production mode
 */
export function isProduction(): boolean {
  return getEnvironmentConfig().isProduction;
}

/**
 * Check if running in test mode
 */
export function isTest(): boolean {
  return getEnvironmentConfig().isTest;
}

/**
 * Get environment-specific configuration for authentication
 */
export function getAuthEnvironmentConfig() {
  const envConfig = getEnvironmentConfig();

  return {
    ...envConfig,
    // Development-specific settings
    maxVerificationAttempts: envConfig.isDevelopment ? 3 : 5, // Lower in dev to catch loops faster
    verificationRetryDelay: envConfig.isDevelopment ? 500 : 1000, // Faster in dev
    enableLoopDetection: true, // Always enabled
    enableDetailedLogging: envConfig.isDevelopment, // More logging in dev
    enableSafeguards: true, // Always enabled

    // Feature flags for development
    enableDevSafeguards: envConfig.isDevelopment,
    enableMockAuth: envConfig.isDevelopment && process.env.NEXT_PUBLIC_MOCK_AUTH === 'true',

    // Memory monitoring settings
    memoryCheckEnabled: envConfig.isDevelopment,
    memoryThreshold: envConfig.isDevelopment ? 0.7 : 0.8, // Lower threshold in dev to catch issues early
  };
}

/**
 * Check if development safeguards should be active
 */
export function shouldApplyDevSafeguards(): boolean {
  return getAuthEnvironmentConfig().enableDevSafeguards;
}

/**
 * Check if detailed logging should be enabled
 */
export function shouldEnableDetailedLogging(): boolean {
  return getAuthEnvironmentConfig().enableDetailedLogging;
}

/**
 * Get the maximum number of verification attempts allowed
 */
export function getMaxVerificationAttempts(): number {
  return getAuthEnvironmentConfig().maxVerificationAttempts;
}

/**
 * Check if mock authentication should be used (for development/testing)
 */
export function shouldUseMockAuth(): boolean {
  return getAuthEnvironmentConfig().enableMockAuth;
}

/**
 * Check if memory monitoring should be enabled
 */
export function shouldMonitorMemory(): boolean {
  return getAuthEnvironmentConfig().memoryCheckEnabled;
}

/**
 * Get memory threshold for warnings
 */
export function getMemoryThreshold(): number {
  return getAuthEnvironmentConfig().memoryThreshold;
}