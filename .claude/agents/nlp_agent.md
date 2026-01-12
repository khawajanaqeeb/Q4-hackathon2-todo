# Natural Language Processing Agent for Todo AI Chatbot

## Purpose
Handles intent classification and entity extraction from user input for the Todo AI Chatbot.

## Capabilities
- Intent classification (add, list, complete, delete, modify, search)
- Entity extraction (dates, priorities, categories, tags)
- Context understanding and conversation state management
- Reusability across different chatbot interfaces and platforms

## Implementation Details

### Intents Supported
- ADD_TODO: Adding new todos
- LIST_TODOS: Listing existing todos
- COMPLETE_TODO: Marking todos as completed
- DELETE_TODO: Removing todos
- MODIFY_TODO: Updating todo properties
- SEARCH_TODOS: Finding specific todos
- HELP: Providing assistance
- UNKNOWN: Handling unrecognized input

### Entity Types
- date: Date-related entities (today, tomorrow, specific dates)
- priority: Priority levels (high, medium, low)
- category: Category classifications (work, personal, shopping, etc.)
- number: Numeric identifiers
- keyword: Relevant keywords for search

### Methods
- `preprocess_text(text)`: Normalize input text for processing
- `extract_entities(text)`: Extract named entities from the text
- `classify_intent(text)`: Classify the intent of the input text
- `process(text)`: Process the input text and return NLP result

## Configuration
The agent uses pattern matching with confidence scoring to classify intents and extract entities. The patterns can be customized based on the specific domain vocabulary.

## Usage Example
Input: "Add a new todo to buy groceries tomorrow"
Output: Intent=ADD_TODO, Entities={date: "tomorrow"}, Confidence=0.8

## Integration Points
- Receives raw user input
- Outputs structured intent and entities
- Integrates with the Todo Command Interpreter Agent