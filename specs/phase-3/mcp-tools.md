# MCP Tools Specification for Phase 3 Todo AI Chatbot

## Overview

This document defines the MCP (Multi-Agent Communication Protocol) tools that enable the AI agents to interact with the backend systems. These tools provide standardized interfaces for all todo management operations.

## Tool Schemas

### 1. add_task

**Purpose**: Create a new todo item in the user's list.

**Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new todo item for the authenticated user",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "The ID of the authenticated user"
      },
      "title": {
        "type": "string",
        "description": "The title of the task"
      },
      "description": {
        "type": "string",
        "description": "Detailed description of the task",
        "default": ""
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Priority level of the task",
        "default": "medium"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Tags to categorize the task",
        "default": []
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "Due date for the task (ISO 8601 format)",
        "default": null
      }
    },
    "required": ["user_id", "title"]
  }
}
```

**Example Usage**:
```json
{
  "user_id": 123,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, fruits",
  "priority": "medium",
  "tags": ["shopping", "errands"],
  "due_date": "2024-01-25T10:00:00Z"
}
```

**Expected Response**:
```json
{
  "success": true,
  "task_id": 456,
  "message": "Task 'Buy groceries' created successfully"
}
```

### 2. list_tasks

**Purpose**: Retrieve a filtered list of todo items for the user.

**Schema**:
```json
{
  "name": "list_tasks",
  "description": "Retrieve a list of todo items for the authenticated user with optional filtering",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "The ID of the authenticated user"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter by task completion status",
        "default": "all"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high", "all"],
        "description": "Filter by task priority",
        "default": "all"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Filter by tags",
        "default": []
      },
      "limit": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100,
        "description": "Maximum number of tasks to return",
        "default": 10
      },
      "offset": {
        "type": "integer",
        "minimum": 0,
        "description": "Offset for pagination",
        "default": 0
      }
    },
    "required": ["user_id"]
  }
}
```

**Example Usage**:
```json
{
  "user_id": 123,
  "status": "pending",
  "priority": "high",
  "limit": 5
}
```

**Expected Response**:
```json
{
  "success": true,
  "tasks": [
    {
      "id": 123,
      "title": "Complete project proposal",
      "description": "Finish the quarterly project proposal",
      "priority": "high",
      "tags": ["work", "urgent"],
      "completed": false,
      "created_at": "2024-01-20T09:00:00Z",
      "updated_at": "2024-01-20T09:00:00Z"
    }
  ],
  "total_count": 1
}
```

### 3. complete_task

**Purpose**: Mark a todo item as completed.

**Schema**:
```json
{
  "name": "complete_task",
  "description": "Mark a todo item as completed for the authenticated user",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "The ID of the authenticated user"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to mark as completed"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Example Usage**:
```json
{
  "user_id": 123,
  "task_id": 456
}
```

**Expected Response**:
```json
{
  "success": true,
  "task_id": 456,
  "message": "Task 'Buy groceries' marked as completed"
}
```

### 4. delete_task

**Purpose**: Delete a todo item from the user's list.

**Schema**:
```json
{
  "name": "delete_task",
  "description": "Delete a todo item for the authenticated user",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "The ID of the authenticated user"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to delete"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Example Usage**:
```json
{
  "user_id": 123,
  "task_id": 456
}
```

**Expected Response**:
```json
{
  "success": true,
  "task_id": 456,
  "message": "Task 'Buy groceries' deleted successfully"
}
```

### 5. update_task

**Purpose**: Modify an existing todo item.

**Schema**:
```json
{
  "name": "update_task",
  "description": "Update properties of an existing todo item for the authenticated user",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "integer",
        "description": "The ID of the authenticated user"
      },
      "task_id": {
        "type": "integer",
        "description": "The ID of the task to update"
      },
      "title": {
        "type": "string",
        "description": "New title for the task (optional)"
      },
      "description": {
        "type": "string",
        "description": "New description for the task (optional)"
      },
      "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "New priority for the task (optional)"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "New tags for the task (optional)"
      },
      "due_date": {
        "type": "string",
        "format": "date-time",
        "description": "New due date for the task (optional)"
      },
      "completed": {
        "type": "boolean",
        "description": "New completion status for the task (optional)"
      }
    },
    "required": ["user_id", "task_id"]
  }
}
```

**Example Usage**:
```json
{
  "user_id": 123,
  "task_id": 456,
  "priority": "high",
  "completed": true
}
```

**Expected Response**:
```json
{
  "success": true,
  "task_id": 456,
  "message": "Task 'Buy groceries' updated successfully"
}
```

## Error Handling

All tools follow a consistent error response format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descriptive error message",
    "details": {
      "field": "specific_field_if_applicable",
      "expected": "expected_value_or_format",
      "received": "actual_value_received"
    }
  }
}
```

## Common Error Codes

- `AUTHENTICATION_FAILED`: Invalid or expired JWT token
- `USER_MISMATCH`: Requested user_id doesn't match authenticated user
- `TASK_NOT_FOUND`: Specified task_id doesn't exist for the user
- `INVALID_INPUT`: Request data doesn't match schema requirements
- `PERMISSION_DENIED`: User doesn't have permission for the requested operation
- `DATABASE_ERROR`: Internal database operation failed