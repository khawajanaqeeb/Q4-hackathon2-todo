# List Tasks Agent Specification

## Overview
The List Tasks Agent handles user requests to view their todo items. It retrieves and formats todo lists according to user preferences and filters.

## Purpose
To interpret user requests for viewing tasks and return appropriately filtered and formatted lists of todo items.

## Capabilities
- Parse natural language input for task listing
- Apply filters (completed, pending, priority, tags, date ranges)
- Sort tasks by various criteria (priority, date, title)
- Format task lists for display
- Handle pagination for large lists

## Technology Stack
- ORM: SQLModel for database operations
- Database: Neon Serverless PostgreSQL
- Integration: With existing Todo model and user authentication

## Input Processing
- Recognizes phrases like "list", "show", "what do I have", "pending", "completed"
- Interprets filter requests (completed, pending, high priority, by tag, etc.)
- Applies sorting preferences (by date, priority, alphabetical)
- Handles pagination requests

## Integration Points
- Receives delegation from Router Agent
- Connects to existing Todo model in the database
- Uses authenticated user context from JWT
- Follows existing query patterns for filtering and sorting