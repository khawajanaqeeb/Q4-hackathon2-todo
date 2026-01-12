# Conversation Context Manager Agent

## Purpose
Manages conversation state, history, and user preferences across interactions for the Todo AI Chatbot.

## Capabilities
- Maintains conversation history for context awareness
- Tracks user preferences and settings
- Manages active context (currently selected todo, filters, etc.)
- Handles session management and timeouts
- Provides reference resolution for pronouns and contextual references

## Implementation Details

### Core Components
- **Message**: Represents individual conversation exchanges with role, content, and metadata
- **UserContext**: Stores all context information for a specific user
- **Session Management**: Handles user sessions with configurable timeouts

### Context Elements Managed
- **Conversation History**: Recent messages between user and assistant
- **User Preferences**: Customization settings and preferences
- **Active Context**: Currently selected todo, active filters, etc.
- **Reference Tracking**: Links between user references and specific todos

### Methods
- `create_user_context(user_id)`: Create a new user context
- `get_user_context(user_id)`: Retrieve user context with session management
- `update_user_preferences(user_id, preferences)`: Update user preferences
- `add_message_to_history(user_id, role, content)`: Add message to conversation history
- `get_recent_messages(user_id, count)`: Retrieve recent messages
- `set_active_context(user_id, context_data)`: Set active context for user
- `get_active_context(user_id)`: Get current active context
- `infer_reference_from_context(user_id, possible_references)`: Resolve ambiguous references
- `update_last_todo_id(user_id, todo_id)`: Track last referenced todo
- `serialize_context(user_id)`: Convert context to JSON for storage
- `deserialize_context(user_id, context_json)`: Restore context from JSON

### Session Management
- Configurable session timeout (default: 1 hour)
- Automatic context recreation after timeout
- History trimming to maintain performance

## Configuration
- `max_history_size`: Maximum number of messages to retain (default: 20)
- `session_timeout`: Duration before session expires (default: 1 hour)

## Usage Example
Scenario: User says "Mark it as completed" after adding a todo
- Context manager identifies "it" refers to the last added todo
- Returns the specific todo ID for the command interpreter
- Maintains continuity in the conversation

## Integration Points
- Receives user interactions from the chat interface
- Provides context to the NLP Agent for better understanding
- Shares state with all other agents in the system
- Integrates with the Response Generation Agent for personalized responses