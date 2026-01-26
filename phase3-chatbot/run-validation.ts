#!/usr/bin/env node

/**
 * Run validation tests to confirm the authentication memory leak fixes work as expected
 */

console.log('🔍 Running authentication memory leak fix validation...');

// Import the validation test
import { performCompleteValidation, generateValidationReport } from './frontend/src/lib/auth/validation-test';

async function runValidation() {
  try {
    console.log('🚀 Starting validation process...');

    // Generate validation report
    const report = generateValidationReport();

    // Perform complete validation
    const result = await performCompleteValidation();

    console.log('\n✅ Validation completed!');
    console.log(`📊 Result: ${result.passed ? 'PASSED' : 'FAILED'}`);

    if (result.issues.length > 0) {
      console.log(`⚠️  Issues found (${result.issues.length}):`);
      result.issues.forEach((issue, index) => {
        console.log(`   ${index + 1}. ${issue}`);
      });
    }

    if (result.recommendations.length > 0) {
      console.log(`💡 Recommendations (${result.recommendations.length}):`);
      result.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. ${rec}`);
      });
    }

    console.log('\n✨ Authentication memory leak fixes validation completed successfully!');
    console.log(`🎯 Overall result: ${result.passed ? 'SUCCESS - Fixes are working correctly' : 'NEEDS ATTENTION - Some issues detected'}`);

    return result.passed;
  } catch (error) {
    console.error('❌ Validation failed with error:', error);
    return false;
  }
}

// Run the validation
runValidation()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error('💥 Unhandled error during validation:', error);
    process.exit(1);
  });