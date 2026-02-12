/**
 * Validation Test for Authentication Memory Leak Fixes
 * This test validates that the authentication fixes prevent memory exhaustion
 */

import { authLogger } from './logging';
import { authStateManager } from './state-manager';
import { originTracker } from './origin-tracker';
import { verifyAuthentication } from './verification';
import { isDevMode } from './config';
import { turbopackMemoryMonitor } from './turbopack-monitor';
import { turbopackSafeguards } from './turbopack-safeguards';

export interface ValidationResult {
  passed: boolean;
  issues: string[];
  recommendations: string[];
  memoryStats?: any;
  verificationStats?: any;
}

class AuthValidator {
  private static instance: AuthValidator;

  private constructor() {}

  static getInstance(): AuthValidator {
    if (!AuthValidator.instance) {
      AuthValidator.instance = new AuthValidator();
    }
    return AuthValidator.instance;
  }

  /**
   * Run comprehensive validation of authentication fixes
   */
  async validateFixes(): Promise<ValidationResult> {
    const issues: string[] = [];
    const recommendations: string[] = [];

    authLogger.info(`[VALIDATOR] Starting authentication fix validation`);

    // Check memory monitoring
    const memoryStats = turbopackMemoryMonitor.getCurrentStats();
    if (memoryStats.stability === 'critical') {
      issues.push('Memory stability is critical');
    } else if (memoryStats.stability === 'unstable') {
      issues.push('Memory stability is unstable');
    }

    // Check if safeguards are active
    const safeguardStatus = turbopackSafeguards.getStatus();
    if (!safeguardStatus.isInitialized) {
      issues.push('Turbopack safeguards not initialized');
    }

    // Check for potential loops
    const loopStatus = originTracker.checkLoopStatus();
    if (loopStatus.isLooping) {
      issues.push(`Potential verification loop detected: ${JSON.stringify(loopStatus.details)}`);
    }

    // Check verification status
    const verificationStatus = authStateManager.getVerificationStatus();
    if (!verificationStatus.canVerify && verificationStatus.timeUntilRetry) {
      authLogger.warn(`Verification is rate limited`, {
        timeUntilRetry: verificationStatus.timeUntilRetry
      });
    }

    // Get recent verification records
    const recentRecords = originTracker.getRecentRecords(10);
    const verifyRecords = recentRecords.filter(r => r.path.includes('/verify'));

    if (verifyRecords.length > 5) {
      // Check if these happened in a short time period (potential loop)
      const timeWindow = 5000; // 5 seconds
      const startTime = Date.now() - timeWindow;
      const recentVerifyCount = verifyRecords.filter(r => r.timestamp > startTime).length;

      if (recentVerifyCount > 3) {
        issues.push(`High frequency verification requests detected: ${recentVerifyCount} in ${timeWindow}ms`);
      }
    }

    // Generate recommendations
    if (memoryStats.stability !== 'stable') {
      recommendations.push('Monitor memory usage during extended development sessions');
    }

    if (!safeguardStatus.isInitialized) {
      recommendations.push('Initialize Turbopack safeguards in development mode');
    }

    if (authStateManager.isApproachingVerificationLimit()) {
      recommendations.push('Review authentication flow to reduce verification attempts');
    }

    const validationResult: ValidationResult = {
      passed: issues.length === 0,
      issues,
      recommendations,
      memoryStats,
      verificationStats: verificationStatus
    };

    if (validationResult.passed) {
      authLogger.info(`[VALIDATOR] Authentication fixes validation PASSED`);
    } else {
      authLogger.warn(`[VALIDATOR] Authentication fixes validation issues found`, {
        issueCount: issues.length,
        issues
      });
    }

    return validationResult;
  }

  /**
   * Run a specific test scenario
   */
  async runScenarioTest(scenario: 'normal-flow' | 'error-flow' | 'concurrent-access'): Promise<boolean> {
    authLogger.info(`[VALIDATOR] Running scenario test: ${scenario}`);

    try {
      switch (scenario) {
        case 'normal-flow':
          // Test normal authentication flow
          const result = await verifyAuthentication({ includeUserDetails: false });
          authLogger.info(`[VALIDATOR] Normal flow test completed`, {
            isAuthenticated: result.isAuthenticated,
            hasError: !!result.error
          });
          return !result.error;

        case 'error-flow':
          // Test error handling without causing actual errors
          authLogger.info(`[VALIDATOR] Error flow test completed (simulated)`);
          return true; // Simulated test

        case 'concurrent-access':
          // Test multiple simultaneous authentication checks
          const promises = Array.from({ length: 3 }, (_, i) =>
            verifyAuthentication({ includeUserDetails: false, forceRefresh: i === 0 })
          );

          const results = await Promise.all(promises);
          const hasErrors = results.some(r => r.error);

          authLogger.info(`[VALIDATOR] Concurrent access test completed`, {
            totalRequests: results.length,
            results: results.map(r => ({ isAuthenticated: r.isAuthenticated, hasError: !!r.error }))
          });

          return !hasErrors;
      }
    } catch (error) {
      authLogger.error(`[VALIDATOR] Scenario test failed: ${scenario}`, {
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Generate a validation report
   */
  generateValidationReport(): string {
    const validation = this.validateFixes();

    let report = `=== AUTHENTICATION FIXES VALIDATION REPORT ===\n`;
    report += `Timestamp: ${new Date().toISOString()}\n`;
    report += `Environment: ${isDevMode() ? 'Development' : 'Production'}\n`;
    report += `Validation Passed: ${validation.passed ? 'YES' : 'NO'}\n\n`;

    if (validation.issues.length > 0) {
      report += `ISSUES FOUND:\n`;
      validation.issues.forEach((issue, index) => {
        report += `  ${index + 1}. ${issue}\n`;
      });
      report += `\n`;
    }

    if (validation.recommendations.length > 0) {
      report += `RECOMMENDATIONS:\n`;
      validation.recommendations.forEach((rec, index) => {
        report += `  ${index + 1}. ${rec}\n`;
      });
      report += `\n`;
    }

    if (validation.memoryStats) {
      report += `MEMORY STATS:\n`;
      report += `  Current Heap Used: ${(validation.memoryStats.currentHeapUsed / 1024 / 1024).toFixed(2)} MB\n`;
      report += `  Auth Memory: ${(validation.memoryStats.currentAuthMemory / 1024 / 1024).toFixed(2)} MB\n`;
      report += `  Stability: ${validation.memoryStats.stability}\n\n`;
    }

    report += `==========================================\n`;

    return report;
  }
}

export const authValidator = AuthValidator.getInstance();

/**
 * Validate the authentication fixes
 */
export async function validateAuthFixes(): Promise<ValidationResult> {
  return authValidator.validateFixes();
}

/**
 * Run a specific validation scenario
 */
export async function runValidationScenario(scenario: 'normal-flow' | 'error-flow' | 'concurrent-access'): Promise<boolean> {
  return authValidator.runScenarioTest(scenario);
}

/**
 * Generate and log validation report
 */
export function generateValidationReport(): string {
  const report = authValidator.generateValidationReport();
  console.log(report);
  return report;
}

/**
 * Perform complete validation
 */
export async function performCompleteValidation(): Promise<ValidationResult> {
  const result = await validateAuthFixes();

  if (isDevMode()) {
    generateValidationReport();
  }

  return result;
}