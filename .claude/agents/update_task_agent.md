# Update Task Agent Specification

## Overview
The Update Task Agent handles user requests to modify existing todo items. It updates task properties based on user input and context.

## Purpose
To interpret user requests for updating tasks and modify the appropriate todo items in the database.

## Capabilities
- Parse natural language input for task updates
- Identify specific tasks to update (by title, position, or description)
- Update task properties (title, description, priority, tags, completion status)
- Handle update errors and provide feedback
- Support bulk updates when requested

## Technology Stack
- ORM: SQLModel for database operations
- Database: Neon Serverless PostgreSQL
- Integration: With existing Todo model and user authentication

## Input Processing
- Recognizes phrases like "update", "change", "rename", "edit", "modify"
- Identifies target tasks (by title, index, or description)
- Determines which properties to update and new values
- Validates task ownership before updating
- Confirms successful updates

## Integration Points
- Receives delegation from Router Agent
- Connects to existing Todo model in the database
- Uses authenticated user context from JWT
- Follows existing update patterns and validation