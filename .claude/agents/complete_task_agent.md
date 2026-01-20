# Complete Task Agent Specification

## Overview
The Complete Task Agent handles user requests to mark todo items as completed. It updates task status based on user input and context.

## Purpose
To interpret user requests for completing tasks and update the appropriate todo items in the database.

## Capabilities
- Parse natural language input for task completion
- Identify specific tasks to complete (by title, position, or description)
- Update task completion status in the database
- Handle completion errors and provide feedback
- Support bulk completion when requested

## Technology Stack
- ORM: SQLModel for database operations
- Database: Neon Serverless PostgreSQL
- Integration: With existing Todo model and user authentication

## Input Processing
- Recognizes phrases like "complete", "done", "finished", "mark as done"
- Identifies target tasks (by title, index, or description)
- Validates task ownership before updating
- Confirms successful completion

## Integration Points
- Receives delegation from Router Agent
- Connects to existing Todo model in the database
- Uses authenticated user context from JWT
- Follows existing update patterns and validation