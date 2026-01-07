# Data Model: Fix Auth Proxy Error and Create Modern Landing Page

## Entities

### Todo (Reference from existing system)
**Description**: Represents a task in the todo application
**Fields**:
- `id`: string - Unique identifier for the task
- `title`: string - Task title/description
- `description`: string (optional) - Detailed task description
- `priority`: 'low' | 'medium' | 'high' - Task priority level
- `completed`: boolean - Completion status
- `tags`: string (optional) - Comma-separated tags for categorization
- `user_id`: string - ID of the user who owns the task
- `created_at`: string - Creation timestamp
- `updated_at`: string - Last update timestamp

**Validation Rules**:
- `id` must be a valid string identifier
- `title` must be non-empty string with max length 500
- `priority` must be one of 'low', 'medium', or 'high'
- `completed` must be boolean
- `created_at` and `updated_at` must be valid ISO date strings

**State Transitions**:
- `completed` can transition from `false` to `true` (marking as done)
- `completed` can transition from `true` to `false` (unmarking as done)
- Other fields can be updated through edit operations

### User (Reference from existing system)
**Description**: Represents an authenticated user
**Fields**:
- `id`: number - Unique identifier for the user
- `email`: string - User's email address (unique)
- `name`: string - User's display name
- `is_active`: boolean - Account active status
- `created_at`: string - Account creation timestamp
- `updated_at`: string - Last profile update timestamp

**Validation Rules**:
- `email` must be a valid email address and unique
- `name` must be non-empty string with max length 255
- `is_active` defaults to `true`

## Relationships

- **Todo → User**: Many-to-one relationship (many todos belong to one user)
- Foreign key: `user_id` in Todo references `id` in User

## Data Flow

### Sample Data for Landing Page
For the landing page demonstration, sample Todo objects will be created with realistic data that matches the production schema but without persistence requirements.

### API Proxy Data Flow
- Frontend makes requests to `/api/auth/proxy/[...path]`
- Proxy extracts auth token from cookies or headers
- Proxy awaits the params promise to properly access path segments
- Proxy forwards request to backend API with auth token
- Backend processes request and returns response
- Proxy returns response to frontend

## Data Validation

### Frontend Validation
- Input sanitization for all user-provided data
- Type checking using TypeScript interfaces
- Form validation before API submission

### Backend Validation
- Pydantic model validation for all API inputs
- SQLModel validation at database level
- Authentication and authorization checks
- Proper error handling with meaningful messages instead of raw objects

### API Error Response Format
- For 422 Unprocessable Entity errors: Return proper error format with message field
- For validation errors: Include specific field validation details
- For auth errors: Return consistent format with appropriate status codes
- No raw object displays to prevent "[object Object]" errors