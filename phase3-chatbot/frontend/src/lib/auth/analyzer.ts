/**
 * Authentication Verification Flow Analyzer
 * Analyzes authentication verification patterns to detect anomalies and potential issues
 */

import { originTracker } from './origin-tracker';
import { authStateManager } from './state-manager';
import { authLogger } from './logging';
import { isDevMode } from './config';

export interface VerificationPattern {
  timestamp: number;
  origin: string;
  path: string;
  method: string;
  success: boolean;
  duration: number;
  context: string;
}

export interface FlowAnalysis {
  totalVerifications: number;
  successRate: number;
  averageDuration: number;
  errorPatterns: string[];
  potentialLoops: boolean;
  suspiciousPatterns: SuspiciousPattern[];
  timeline: VerificationPattern[];
}

export interface SuspiciousPattern {
  type: 'rapid-fire' | 'circular' | 'unusual-frequency' | 'cross-origin';
  description: string;
  occurrences: number;
  timeframe: number;
  severity: 'low' | 'medium' | 'high';
}

class AuthFlowAnalyzer {
  private static instance: AuthFlowAnalyzer;
  private patterns: VerificationPattern[] = [];
  private maxPatterns = 1000; // Keep only recent patterns

  private constructor() {}

  static getInstance(): AuthFlowAnalyzer {
    if (!AuthFlowAnalyzer.instance) {
      AuthFlowAnalyzer.instance = new AuthFlowAnalyzer();
    }
    return AuthFlowAnalyzer.instance;
  }

  /**
   * Add a verification pattern to the analysis
   */
  addVerificationPattern(pattern: Omit<VerificationPattern, 'duration'> & { startTime: number }): void {
    const duration = Date.now() - pattern.startTime;

    const fullPattern: VerificationPattern = {
      ...pattern,
      duration
    };

    this.patterns.push(fullPattern);

    // Keep only the most recent patterns
    if (this.patterns.length > this.maxPatterns) {
      this.patterns = this.patterns.slice(-this.maxPatterns);
    }

    // Log if in development mode
    if (isDevMode()) {
      authLogger.debug(`[ANALYZER] Added verification pattern`, {
        origin: pattern.origin,
        path: pattern.path,
        method: pattern.method,
        duration,
        success: pattern.success
      });
    }
  }

  /**
   * Analyze the current verification flow
   */
  analyzeFlow(): FlowAnalysis {
    const totalVerifications = this.patterns.length;

    if (totalVerifications === 0) {
      return {
        totalVerifications: 0,
        successRate: 0,
        averageDuration: 0,
        errorPatterns: [],
        potentialLoops: false,
        suspiciousPatterns: [],
        timeline: []
      };
    }

    // Calculate success rate
    const successfulVerifications = this.patterns.filter(p => p.success).length;
    const successRate = totalVerifications > 0 ? successfulVerifications / totalVerifications : 0;

    // Calculate average duration
    const totalDuration = this.patterns.reduce((sum, p) => sum + p.duration, 0);
    const averageDuration = totalVerifications > 0 ? totalDuration / totalVerifications : 0;

    // Identify error patterns
    const errorPatterns = this.patterns
      .filter(p => !p.success)
      .map(p => `${p.origin}:${p.path}`)
      .filter((value, index, self) => self.indexOf(value) === index); // Unique error patterns

    // Check for potential loops
    const potentialLoops = this.detectPotentialLoops();

    // Identify suspicious patterns
    const suspiciousPatterns = this.identifySuspiciousPatterns();

    return {
      totalVerifications,
      successRate,
      averageDuration,
      errorPatterns,
      potentialLoops,
      suspiciousPatterns,
      timeline: [...this.patterns] // Return a copy of the timeline
    };
  }

  /**
   * Detect potential loops in verification patterns
   */
  private detectPotentialLoops(): boolean {
    // Check for rapid-fire requests to the same endpoint
    const now = Date.now();
    const recentMs = 5000; // 5 seconds
    const recentPatterns = this.patterns.filter(p => now - p.timestamp <= recentMs);

    // Group by origin and path
    const grouped = recentPatterns.reduce((acc, pattern) => {
      const key = `${pattern.origin}:${pattern.path}`;
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(pattern);
      return acc;
    }, {} as Record<string, VerificationPattern[]>);

    // Check if any group has more than 5 requests in 5 seconds
    for (const [_, patterns] of Object.entries(grouped)) {
      if (patterns.length >= 5) {
        return true;
      }
    }

    return false;
  }

  /**
   * Identify suspicious patterns in verification flow
   */
  private identifySuspiciousPatterns(): SuspiciousPattern[] {
    const suspicious: SuspiciousPattern[] = [];
    const now = Date.now();
    const patterns = this.patterns;

    // Check for rapid-fire requests (more than 3 per second to same endpoint)
    const oneSecondAgo = now - 1000;
    const patternsLastSecond = patterns.filter(p => now - p.timestamp <= 1000);

    const endpointFrequency = patternsLastSecond.reduce((acc, p) => {
      const key = `${p.origin}:${p.path}`;
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    for (const [endpoint, count] of Object.entries(endpointFrequency)) {
      if (count > 3) {
        suspicious.push({
          type: 'rapid-fire',
          description: `High frequency requests to ${endpoint}: ${count} requests in 1 second`,
          occurrences: count,
          timeframe: 1000,
          severity: count > 10 ? 'high' : count > 5 ? 'medium' : 'low'
        });
      }
    }

    // Check for unusual duration patterns (very slow requests)
    const slowThreshold = 5000; // 5 seconds
    const slowPatterns = patterns.filter(p => p.duration > slowThreshold);

    if (slowPatterns.length > 0) {
      suspicious.push({
        type: 'unusual-frequency',
        description: `${slowPatterns.length} slow verification requests (> ${slowThreshold}ms)`,
        occurrences: slowPatterns.length,
        timeframe: now - (this.patterns[0]?.timestamp || now),
        severity: slowPatterns.length > 5 ? 'high' : slowPatterns.length > 2 ? 'medium' : 'low'
      });
    }

    // Check for cross-origin authentication attempts that might be suspicious
    const origins = [...new Set(patterns.map(p => p.origin))];
    if (origins.length > 3) { // More than 3 different origins might be suspicious
      suspicious.push({
        type: 'cross-origin',
        description: `Authentication requests from ${origins.length} different origins: ${origins.join(', ')}`,
        occurrences: origins.length,
        timeframe: now - (this.patterns[0]?.timestamp || now),
        severity: origins.length > 5 ? 'high' : origins.length > 3 ? 'medium' : 'low'
      });
    }

    return suspicious;
  }

  /**
   * Get verification patterns for a specific time range
   */
  getPatternsInRange(startTime: number, endTime: number): VerificationPattern[] {
    return this.patterns.filter(p => p.timestamp >= startTime && p.timestamp <= endTime);
  }

  /**
   * Get verification patterns by origin
   */
  getPatternsByOrigin(origin: string): VerificationPattern[] {
    return this.patterns.filter(p => p.origin === origin);
  }

  /**
   * Get verification patterns by path
   */
  getPatternsByPath(path: string): VerificationPattern[] {
    return this.patterns.filter(p => p.path.includes(path));
  }

  /**
   * Get statistics for a specific time window
   */
  getStatistics(timeWindowMs: number = 60000): {
    count: number;
    successRate: number;
    avgDuration: number;
    errorCount: number;
  } {
    const now = Date.now();
    const patterns = this.patterns.filter(p => now - p.timestamp <= timeWindowMs);

    if (patterns.length === 0) {
      return {
        count: 0,
        successRate: 0,
        avgDuration: 0,
        errorCount: 0
      };
    }

    const successful = patterns.filter(p => p.success).length;
    const errorCount = patterns.length - successful;
    const totalDuration = patterns.reduce((sum, p) => sum + p.duration, 0);

    return {
      count: patterns.length,
      successRate: successful / patterns.length,
      avgDuration: totalDuration / patterns.length,
      errorCount
    };
  }

  /**
   * Clear all stored patterns (useful for testing or memory management)
   */
  clearPatterns(): void {
    this.patterns = [];
    authLogger.info('[ANALYZER] Verification patterns cleared');
  }

  /**
   * Generate a detailed report of the analysis
   */
  generateReport(): string {
    const analysis = this.analyzeFlow();

    let report = `=== AUTHENTICATION VERIFICATION ANALYSIS REPORT ===\n`;
    report += `Timestamp: ${new Date().toISOString()}\n`;
    report += `Total Verifications: ${analysis.totalVerifications}\n`;
    report += `Success Rate: ${(analysis.successRate * 100).toFixed(2)}%\n`;
    report += `Average Duration: ${analysis.averageDuration.toFixed(2)}ms\n`;
    report += `Potential Loops Detected: ${analysis.potentialLoops ? 'YES' : 'NO'}\n`;

    if (analysis.errorPatterns.length > 0) {
      report += `Error Patterns: ${analysis.errorPatterns.join(', ')}\n`;
    }

    if (analysis.suspiciousPatterns.length > 0) {
      report += `\nSUSPICIOUS PATTERNS:\n`;
      analysis.suspiciousPatterns.forEach((pattern, index) => {
        report += `  ${index + 1}. [${pattern.severity.toUpperCase()}] ${pattern.type}: ${pattern.description}\n`;
      });
    }

    report += `\n==============================================\n`;

    return report;
  }

  /**
   * Check if verification patterns are within normal ranges
   */
  isFlowNormal(): boolean {
    const analysis = this.analyzeFlow();

    // Consider flow abnormal if:
    // - Success rate is below 80%
    // - Potential loops detected
    // - More than 3 high-severity suspicious patterns
    // - More than 10 requests per minute to same endpoint

    const highSeveritySuspicious = analysis.suspiciousPatterns.filter(p => p.severity === 'high').length;

    return !(
      analysis.successRate < 0.8 ||
      analysis.potentialLoops ||
      highSeveritySuspicious > 3
    );
  }
}

export const authFlowAnalyzer = AuthFlowAnalyzer.getInstance();

/**
 * Convenience function to add a verification pattern
 */
export function addVerificationPattern(
  origin: string,
  path: string,
  method: string,
  success: boolean,
  context: string,
  startTime: number
): void {
  authFlowAnalyzer.addVerificationPattern({
    timestamp: Date.now(),
    origin,
    path,
    method,
    success,
    context,
    startTime
  });
}

/**
 * Get the current flow analysis
 */
export function getFlowAnalysis(): FlowAnalysis {
  return authFlowAnalyzer.analyzeFlow();
}

/**
 * Check if the verification flow is normal
 */
export function isVerificationFlowNormal(): boolean {
  return authFlowAnalyzer.isFlowNormal();
}

/**
 * Generate and log a detailed analysis report
 */
export function generateAnalysisReport(): void {
  const report = authFlowAnalyzer.generateReport();
  console.log(report);

  if (isDevMode()) {
    authLogger.info('[ANALYZER] Flow analysis report generated', {
      reportLines: report.split('\n').length
    });
  }
}