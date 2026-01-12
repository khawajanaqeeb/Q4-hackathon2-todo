# Response Template Manager Skill

## Purpose
Manages and customizes response templates for the Todo AI Chatbot, ensuring consistent, high-quality, and personalized responses across all interactions.

## Capabilities
- Creates and edits response templates for different scenarios
- Personalizes responses based on user preferences and context
- Handles multilingual response templates
- Performs A/B testing of different response styles
- Manages conditional response variations

## Configuration Options
- Response tone and style settings (formal, casual, friendly)
- User personalization levels
- Multilingual template sets
- A/B testing parameters
- Conditional response triggers

## Usage Examples
```
Create ADD_TODO success template:
- Template: "I've added '{todo_content}' to your list for {due_date}. It's marked as {priority} priority."
- Condition: When todo creation succeeds
- Personalization: Include user's preferred称呼 if available

Create LIST_TODOS template:
- Template: "Here are your {filter} todos:"
- Format: Bulleted list with status indicators
- Fallback: "You don't have any todos matching that description."
```

## Template Management Process
- Defines template variables and placeholders
- Sets up conditional response logic
- Configures personalization options
- Implements multilingual support
- Establishes testing and validation procedures

## Integration Points
- Works with the Response Generation Agent
- Integrates with the Conversation Context Manager Agent for personalization
- Coordinates with the Multi-Platform Adapter Agent for format adjustments
- Updates based on user feedback through the Analytics & Learning Skill