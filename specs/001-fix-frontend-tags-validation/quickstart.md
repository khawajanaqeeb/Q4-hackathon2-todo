# Quickstart: Fix Frontend Tags Validation

## Overview
This guide provides a quick reference for fixing the validation error where the frontend sends tags as a string but the backend expects an array.

## Target Files
- **Primary**: `phase2-fullstack/frontend/app/dashboard/page.tsx`
- **Function**: `handleAddTask` function

## Implementation Steps

### 1. Locate the Problem Code
Find the `handleAddTask` function in `app/dashboard/page.tsx` where the request body is constructed.

### 2. Apply the Fix
Update the request body construction to ensure tags are always sent as an array:

```typescript
// Before (problematic):
const requestBody = {
  title: formData.title,
  description: formData.description,
  tags: formData.tags, // This might be a string
};

// After (fixed):
const formatTags = (tagsInput: string | string[] | undefined): string[] => {
  if (!tagsInput) return [];
  if (typeof tagsInput === 'string') {
    // Handle comma-separated tags or single tag
    return tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag.length > 0);
  }
  return tagsInput; // Already an array
};

const requestBody = {
  title: formData.title,
  description: formData.description,
  tags: formatTags(formData.tags), // Ensure this is always an array
};
```

### 3. Update API Call
Ensure the API call uses the properly formatted request body:

```typescript
// Use the formatted request body
const response = await fetch('/api/tasks', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(requestBody),
});
```

### 4. Test the Fix
- Create tasks with single tags
- Create tasks with multiple comma-separated tags
- Create tasks without tags
- Verify API requests succeed without validation errors

## Files to Modify
- `phase2-fullstack/frontend/app/dashboard/page.tsx` - Main fix location

## Dependencies
- Standard JavaScript/TypeScript environment
- No additional dependencies required

## Expected Outcomes
- Users can create tasks with tags without validation errors
- API requests succeed with proper array format
- Backward compatibility maintained