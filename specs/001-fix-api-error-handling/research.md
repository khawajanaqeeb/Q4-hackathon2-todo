# Research: Fix API Error Handling

## Overview
This research document addresses the issue where API error responses in `lib/api.ts` are not properly serialized, causing "[object Object]" to be displayed instead of meaningful error messages.

## Problem Analysis
- **Issue Location**: `lib/api.ts` line 24 in the `makeRequest` function
- **Current Code**: `throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);`
- **Root Cause**: When `errorData.detail` is an object instead of a string, JavaScript's default string conversion results in "[object Object]"
- **Impact**: Poor user experience with unhelpful error messages

## Solution Approaches
1. **JSON Serialization**: Convert error objects to JSON strings using `JSON.stringify()`
2. **Recursive Stringification**: Handle nested objects and arrays appropriately
3. **Fallback Strategy**: Preserve original behavior when detail is already a string

## Recommended Implementation
```typescript
// Enhanced error handling in makeRequest function
if (!response.ok) {
  const errorData = await response.json().catch(() => ({}));

  // Properly serialize error detail to string
  let errorMessage = 'HTTP error!';
  if (errorData.detail) {
    if (typeof errorData.detail === 'string') {
      errorMessage = errorData.detail;
    } else if (typeof errorData.detail === 'object') {
      try {
        errorMessage = JSON.stringify(errorData.detail);
      } catch (e) {
        // Fallback for circular references or other JSON issues
        errorMessage = errorData.detail.toString ? errorData.detail.toString() : 'Error occurred';
      }
    } else {
      errorMessage = String(errorData.detail);
    }
  } else {
    errorMessage = `HTTP error! status: ${response.status}`;
  }

  throw new Error(errorMessage);
}
```

## Considerations
- **Backward Compatibility**: Maintain existing API behavior for string error details
- **Performance**: Minimal overhead added to error paths only
- **Security**: Avoid exposing sensitive internal information in error messages
- **Debugging**: Preserve enough information for effective debugging

## Alternatives Considered
- **Simple JSON.stringify**: Could fail with circular references
- **Library approach**: Would add dependencies for a simple function
- **Type checking**: TypeScript compilation may catch some issues but not runtime ones

## Decision
Implement the recursive stringification approach with proper fallbacks to handle all possible error data types while maintaining backward compatibility.