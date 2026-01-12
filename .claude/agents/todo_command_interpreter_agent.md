# Todo Command Interpreter Agent

## Purpose
Translates Natural Language Processing results into specific API commands for the todo system.

## Capabilities
- Maps NLP intents to specific API operations (GET, POST, PUT, DELETE)
- Transforms natural language entities to API-compatible parameters
- Validates command syntax and handles edge cases
- Provides human-readable command descriptions

## Implementation Details

### Intent-to-API Mapping
- ADD_TODO → POST /api/todos
- LIST_TODOS → GET /api/todos (with optional filters)
- COMPLETE_TODO → PUT /api/todos/{id}
- DELETE_TODO → DELETE /api/todos/{id}
- MODIFY_TODO → PUT /api/todos/{id}
- SEARCH_TODOS → GET /api/todos/search
- HELP → GET /api/help

### Entity Processing
- Converts natural language priority terms to API-compatible values
- Maps category names to standardized categories
- Parses dates to ISO format or relative terms
- Extracts todo content from natural language input

### Methods
- `interpret(nlp_result)`: Main method to interpret NLP results
- `_interpret_add_todo(nlp_result)`: Handle add todo commands
- `_interpret_list_todos(nlp_result)`: Handle list todos commands
- `_interpret_complete_todo(nlp_result)`: Handle complete todo commands
- `_interpret_delete_todo(nlp_result)`: Handle delete todo commands
- `_interpret_modify_todo(nlp_result)`: Handle modify todo commands
- `_interpret_search_todos(nlp_result)`: Handle search commands
- `_interpret_help(nlp_result)`: Handle help commands

### Data Transformation
- Maps natural language to API-compatible data structures
- Handles missing or ambiguous information gracefully
- Provides fallback mechanisms for incomplete commands

## Configuration
The agent requires access to the NLP agent's output and knowledge of the API structure. It can be configured with custom mappings for priorities, categories, and date formats.

## Usage Example
Input: NLP Result with intent=ADD_TODO, entities={date: "tomorrow", priority: "high"}
Output: API Command with method=POST, endpoint=/api/todos, data={"content": "buy groceries", "due_date": "tomorrow", "priority": "high"}

## Integration Points
- Receives structured NLP results
- Outputs API commands ready for execution
- Integrates with the API Integration Agent
- Works with the NLP Agent and Context Manager Agent