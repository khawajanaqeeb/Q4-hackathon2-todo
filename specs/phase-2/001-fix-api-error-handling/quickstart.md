# Quickstart: Fix API Error Handling

## Overview
This guide provides a quick reference for implementing the API error handling fix in the Next.js frontend application.

## Target File
- **File**: `phase2-fullstack/frontend/lib/api.ts`
- **Function**: `makeRequest`
- **Issue**: Line 24 where error objects are not properly serialized

## Implementation Steps

### 1. Locate the Problem Code
Find the error handling section in `lib/api.ts`:
```typescript
if (!response.ok) {
  const errorData = await response.json().catch(() => ({}));
  throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
}
```

### 2. Apply the Fix
Replace with proper error serialization:
```typescript
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

### 3. Test the Fix
- Trigger API errors in the application
- Verify that error messages are readable strings instead of "[object Object]"
- Ensure existing functionality remains intact

## Files to Modify
- `phase2-fullstack/frontend/lib/api.ts` - Main fix location

## Dependencies
- Standard JavaScript/TypeScript environment
- No additional dependencies required

## Expected Outcomes
- Users see meaningful error messages instead of "[object Object]"
- Error handling maintains backward compatibility
- Proper serialization of nested error objects