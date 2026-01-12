# Response Generation Agent

## Purpose
Creates natural language responses from API results and system events for the Todo AI Chatbot, ensuring responses are conversational, informative, and personalized.

## Capabilities
- Format data into conversational responses
- Handle errors and exceptions gracefully
- Personalize responses based on user context
- Maintain conversation flow and coherence
- Generate appropriate responses for different intents

## Implementation Details

### Response Types
- **Success Responses**: Confirm successful operations
- **Error Responses**: Explain failures in user-friendly terms
- **Informational Responses**: Display lists, details, and status
- **Confirmation Responses**: Seek user confirmation for destructive actions
- **Help Responses**: Provide guidance and instructions

### Personalization Features
- Uses user's name when available
- References previous conversation context
- Adapts tone based on user preferences
- Maintains conversation continuity

### Formatting Capabilities
- Converts API data structures to readable text
- Formats dates, times, and priorities appropriately
- Structures lists and tables for chat display
- Handles rich text and markdown formatting

### Methods
- `generate_response(api_response, user_context)`: Main response generation
- `format_success_response(operation, data)`: Handle successful operations
- `format_error_response(error, user_friendly_msg)`: Handle errors gracefully
- `format_list_response(items, title)`: Format lists of todos
- `format_confirmation_request(action, details)`: Generate confirmation requests
- `personalize_response(response, user_profile)`: Customize for user
- `maintain_context(response, conversation_history)`: Preserve context

### Context Awareness
- Incorporates information from conversation history
- References active context items (selected todos, filters)
- Maintains conversational thread coherence
- Handles follow-up questions appropriately

## Configuration
- `response_style`: Formal, casual, or friendly tone
- `max_items_per_response`: Maximum list items to display
- `include_metadata`: Whether to include priority, dates, etc.
- `confirmation_required_actions`: Operations requiring user confirmation

## Usage Example
Input: API response with created todo data
Output: "I've added 'Buy groceries' to your todo list for tomorrow. It's marked as high priority."

Input: User context showing active todo selected
Output: Response acknowledging the specific todo in context

## Integration Points
- Receives API responses from the API Integration Agent
- Gets user context from the Conversation Context Manager Agent
- Outputs natural language responses to the chat interface
- Works with the Multi-Platform Adapter Agent for different display formats