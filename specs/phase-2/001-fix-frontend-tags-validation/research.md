# Research: Fix Frontend Tags Validation

## Overview
This research addresses the validation error where the frontend sends the `tags` field as a string but the backend expects it as an array. The backend (FastAPI + Pydantic) validates the request body and expects `tags: list[str]` but receives a string value instead.

## Problem Analysis
- **Issue Location**: `app/dashboard/page.tsx` in the `handleAddTask` function
- **Current Behavior**: Tags are sent as a string (e.g., `"work"`) to the API
- **Expected Behavior**: Tags should be sent as an array (e.g., `["work"]`)
- **Root Cause**: The frontend code doesn't properly format tags as arrays before API submission

## Solution Approaches
1. **Array Conversion**: Convert single tag strings to arrays using `[tagString]`
2. **Comma-Separated Parsing**: Split comma-separated strings into arrays using `split()`
3. **Input Validation**: Ensure all tag inputs are properly formatted before API calls
4. **Type Safety**: Add TypeScript types to enforce proper array format

## Recommended Implementation
```typescript
// In handleAddTask function
const formatTags = (tagsInput: string | string[] | undefined): string[] => {
  if (!tagsInput) return [];
  if (typeof tagsInput === 'string') {
    // Handle comma-separated tags or single tag
    return tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
  }
  return tagsInput; // Already an array
};

// Usage in request body:
const requestBody = {
  title: formData.title,
  description: formData.description,
  tags: formatTags(formData.tags), // Ensure this is always an array
  // ... other fields
};
```

## Considerations
- **Backward Compatibility**: Maintain existing functionality while fixing validation
- **Performance**: Minimal overhead for tag processing
- **User Experience**: Handle various input formats gracefully
- **Error Handling**: Proper validation and user feedback for invalid inputs

## Alternatives Considered
- **Backend Change**: Modify Pydantic schema to accept both string and array (not preferred - frontend should match API contract)
- **Complex Parsing**: More sophisticated tag parsing with multiple delimiters (unnecessary complexity)
- **Input Restriction**: Force users to enter tags in specific format (poor UX)

## Decision
Implement the array conversion approach with proper handling of comma-separated inputs and empty values to ensure the API receives the expected array format while maintaining good user experience.