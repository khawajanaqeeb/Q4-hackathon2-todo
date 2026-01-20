# Delete Task Agent Specification

## Overview
The Delete Task Agent handles user requests to remove todo items. It deletes tasks from the user's todo list based on user input and context.

## Purpose
To interpret user requests for deleting tasks and remove the appropriate todo items from the database.

## Capabilities
- Parse natural language input for task deletion
- Identify specific tasks to delete (by title, position, or description)
- Remove tasks from the database
- Handle deletion errors and provide feedback
- Support bulk deletion when requested
- Confirm deletions when appropriate

## Technology Stack
- ORM: SQLModel for database operations
- Database: Neon Serverless PostgreSQL
- Integration: With existing Todo model and user authentication

## Input Processing
- Recognizes phrases like "delete", "remove", "cancel", "get rid of"
- Identifies target tasks (by title, index, or description)
- Validates task ownership before deletion
- Requests confirmation for important or multiple deletions
- Confirms successful deletion

## Integration Points
- Receives delegation from Router Agent
- Connects to existing Todo model in the database
- Uses authenticated user context from JWT
- Follows existing delete patterns and validation