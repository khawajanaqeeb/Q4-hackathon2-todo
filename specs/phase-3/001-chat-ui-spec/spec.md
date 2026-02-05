# 🧾 Chat UI Specification (ChatKit + MCP + SDD)

## 1. System Context

The chat UI serves as the primary interface for users to interact with the todo application through natural language. It exists as a standalone page within the todo application ecosystem, accessible from the main navigation.

### Backend Integration
- The UI connects to the backend chat endpoint at `/chat/{user_id}` via WebSocket or HTTP polling
- All conversational logic is handled by the ChatKit conversation engine
- Todo operations are executed through MCP tools that are invoked by the backend AI agent
- The UI receives real-time updates when MCP tools modify todo items

### Data Ownership
- **Backend owns**: Conversation history, user authentication, todo data, MCP tool execution
- **UI owns**: Real-time message display, user input handling, command suggestions, local UI state
- **Shared**: Current conversation state, pending operations status

### Persistence and Rehydration
- Conversation state is persisted server-side in the database
- Upon loading, the UI fetches the most recent conversation for the authenticated user
- Historical conversations can be accessed through a conversation history panel
- Local UI state (input focus, scroll position) is maintained during session

### Existing Todo Functionality Preservation
- The traditional todo list UI remains accessible alongside the chat interface
- Users can switch between chat and classic todo views
- Both interfaces remain synchronized - changes in one reflect in the other
- Existing todo operations (create, update, delete, complete) continue to function identically

## 2. UI Architecture

### Layout Structure
The UI follows a responsive layout with:
- **Header**: App branding, user profile, theme toggle
- **Main Content Area**: Split into chat panel and optional todo panel
- **Footer**: Status indicators, connection status

### Component Hierarchy
```
App
├── Layout
│   ├── Header
│   │   ├── Branding
│   │   ├── UserProfile
│   │   └── ThemeToggle
│   ├── MainContent
│   │   ├── ChatContainer
│   │   │   ├── MessageList
│   │   │   ├── TypingIndicator
│   │   │   ├── CommandSuggestions
│   │   │   └── MessageInput
│   │   └── TodoPanel (conditional)
│   │       ├── TodoFilter
│   │       ├── TodoList
│   │       └── TodoControls
│   └── Footer
└── ErrorBoundary
    └── NotificationSystem
```

### Separation of Concerns
- **Presentation**: Components handle rendering and styling
- **State**: Global state management for conversations, todos, and UI state
- **Effects/Networking**: API calls, WebSocket connections, and data synchronization

### Responsive Behavior
- **Desktop (1024px+)**: Side-by-side chat and todo panels
- **Tablet (768px-1023px)**: Stacked layout with collapsible todo panel
- **Mobile (<768px)**: Chat panel only, todo accessible via tab/drawer

## 3. Component-Level Specifications

### Root Application Layout
**Purpose**: Container for all UI elements with consistent structure
**Responsibilities**: Layout management, global state provision, error handling
**Inputs**: User authentication state, theme preference
**Outputs**: Navigation events, theme changes
**Loading States**: Shows skeleton while authenticating
**Error States**: Displays global error notifications
**Accessibility**: Landmarks and region labels for screen readers

### Chat Container
**Purpose**: Wrapper for chat-specific components
**Responsibilities**: Scroll management, message history loading, viewport tracking
**Inputs**: Conversation ID, message history, loading state
**Outputs**: Scroll position changes, load more requests
**Loading States**: Shows loading spinner when fetching history
**Error States**: Displays error banner if conversation fails to load
**Accessibility**: Live region for new messages, keyboard navigation

### Message List
**Purpose**: Displays ordered sequence of conversation messages
**Responsibilities**: Message rendering, scroll anchoring, virtualization for long histories
**Inputs**: Array of messages with metadata (sender, timestamp, status)
**Outputs**: Click events for message actions (copy, react, etc.)
**Loading States**: Shows placeholder while messages load
**Error States**: Displays error indicators for failed messages
**Accessibility**: Proper role and labeling for message bubbles

### Message Bubble (User vs AI)
**Purpose**: Visual representation of individual messages
**Responsibilities**: Content rendering, status indication, sender identification
**Inputs**: Message content, sender type (user/ai), timestamp, delivery status
**Outputs**: Link clicks, media interactions
**Loading States**: N/A (always has content once rendered)
**Error States**: Shows error icon and retry option for failed messages
**Accessibility**: Clear role differentiation, timestamp announcement

### Streaming / Typing Indicator
**Purpose**: Visual feedback during AI response generation
**Responsibilities**: Animation display, timing feedback
**Inputs**: Is streaming boolean, estimated time remaining
**Outputs**: N/A
**Loading States**: Animated dots or progress bar
**Error States**: N/A (indicates active state only)
**Accessibility**: Announces to screen readers that AI is responding

### Message Input
**Purpose**: User input field for sending messages
**Responsibilities**: Text input, submission handling, command history
**Inputs**: Current input text, disabled state, placeholder text
**Outputs**: Message submission, text changes, keyboard events
**Loading States**: Disabled during message processing
**Error States**: Shows validation errors for invalid input
**Accessibility**: Proper labeling, keyboard shortcuts, ARIA live for errors

### Command Suggestion Panel
**Purpose**: Contextual suggestions for common commands
**Responsibilities**: Suggestion display, selection handling, relevance calculation
**Inputs**: Current context, available commands, user preferences
**Outputs**: Command selection events, dismissal events
**Loading States**: Hidden while determining relevant suggestions
**Error States**: N/A (passive component)
**Accessibility**: Keyboard navigable, clear selection indicators

### Todo List Panel
**Purpose**: Visual representation of todo items alongside chat
**Responsibilities**: Todo display, filtering, real-time synchronization with chat actions
**Inputs**: Todo list, filter state, loading indicators
**Outputs**: Todo action events (complete, delete, edit)
**Loading States**: Skeleton loading while todos fetch
**Error States**: Error banners for todo operation failures
**Accessibility**: Proper list semantics, action labeling

### Theme Toggle
**Purpose**: Control for light/dark mode preference
**Responsibilities**: Theme state management, CSS class application
**Inputs**: Current theme preference
**Outputs**: Theme change events
**Loading States**: N/A
**Error States**: N/A
**Accessibility**: Proper labeling, system preference detection

### Error and Notification System
**Purpose**: Display of system messages and errors
**Responsibilities**: Message queue management, timing, user interaction
**Inputs**: Error/warning messages, severity levels
**Outputs**: Dismissal events, action button clicks
**Loading States**: N/A
**Error States**: Self-contained error display
**Accessibility**: ARIA live regions, proper severity announcements

## 4. Interaction & UX Flows

### Message Submission Lifecycle
1. **Idle State**: Input field enabled, cursor blinking
2. **Sending State**: Input disabled, send button shows spinner, user message appears in chat
3. **Streaming State**: AI "typing" indicator shows, partial response streams in real-time
4. **Completed State**: Full AI response displays, input re-enabled, suggestions may appear

### ChatKit Streaming Response Handling
1. AI begins processing user input
2. UI shows typing indicator immediately
3. Partial responses stream character-by-character to UI
4. AI response completes with full message
5. Command suggestions appear based on conversation context
6. If MCP tools execute, status updates appear in real-time

### Tool Execution Feedback in UI
1. User command triggers MCP tool invocation
2. UI shows "Processing..." status with spinner
3. Tool executes on backend
4. UI updates with success/error status
5. If tool modifies todos, todo panel updates in real-time
6. AI provides natural language confirmation of changes

### Error Handling Flows

#### Network Errors
1. Connection failure detected
2. Error notification appears: "Connection lost, reconnecting..."
3. Retry mechanism initiates automatically
4. Upon reconnection, UI syncs with server state
5. User receives notification: "Connection restored"

#### Backend Errors
1. Backend returns error response
2. Error notification appears with user-friendly message
3. Failed message shows error indicator
4. User can retry the message if appropriate

#### Invalid Commands
1. AI determines user input is invalid
2. AI responds with clarification request
3. Suggestion panel updates with relevant command examples
4. Input maintains focus for immediate correction

### Command Suggestion Behavior
1. Suggestions appear after user sends message
2. Up to 3 contextually relevant commands display
3. User can click or use keyboard to select
4. Selected command populates input field
5. Suggestions dismiss when user types or clicks away

### Keyboard-Only Usage
- Tab navigation moves between interactive elements in logical order
- Enter/Return submits messages when input has focus
- Arrow keys navigate command suggestions
- Esc dismisses active suggestions or modals
- Ctrl/Cmd + Enter submits message from input field

## 5. State Management Specification

### UI-Local vs Server-Side State

#### UI-Local State
- Input field content
- Scroll positions
- Active UI elements (selected tabs, open accordions)
- Temporary status indicators
- Theme preference
- Local session data

#### Server-Side State
- Complete conversation history
- User authentication
- Todo data and metadata
- MCP tool configurations
- User preferences and settings

### ChatKit-Owned Conversation Lifecycle
- ChatKit manages turn-taking and conversation flow
- UI subscribes to conversation events
- UI renders messages as they arrive from ChatKit
- UI sends raw user input directly to ChatKit
- UI receives and renders AI responses and tool execution status

### Rendering of ChatKit Events
- User messages render immediately upon send
- AI responses render as streaming data arrives
- Tool execution status renders as separate status messages
- Error states render for failed operations
- Typing indicators show during response generation

### Long Conversation Handling
- UI loads initial batch of 50 messages
- Infinite scrolling loads additional batches
- Memory management removes oldest messages from DOM after 1000+ messages
- Jump-to-present functionality maintains near-real-time view

### Optimistic Updates and Rollback
- Todo operations show immediate UI feedback
- If backend operation fails, UI rolls back to previous state
- Visual indicators show pending vs confirmed operations
- User receives clear feedback about operation status

### Synchronization Rules
- Chat-initiated todo changes update todo panel immediately
- Direct todo panel changes update chat with informational message
- Conflicting operations queue and resolve sequentially
- Server state ultimately authoritative for all data

## 6. ChatKit Constraints (NON-NEGOTIABLE)

### ChatKit Responsibilities
- Conversation orchestration and turn management
- AI response generation and streaming
- MCP tool invocation and execution coordination
- Conversation state persistence
- Natural language understanding and command parsing

### UI Responsibilities (Thin Client Only)
- Message display and input handling
- Real-time updates visualization
- User interaction capture
- Local state management
- Accessibility and theming

### UI Restrictions
- UI must NOT contain AI logic or decision-making
- UI must NOT construct prompts or modify conversation context
- UI must NOT route tools or determine which MCP tools to invoke
- UI must NOT manage conversation state persistence

### UI Permissions
- Send raw user input to ChatKit
- Render ChatKit responses and events exactly as received
- Handle presentation and user experience concerns
- Manage local UI state and accessibility features

### Message Roles and Lifecycle
- User messages: Sent to ChatKit, rendered immediately
- AI messages: Received from ChatKit, rendered as received
- Tool status: Received from ChatKit during MCP execution
- All message ordering and correlation managed by ChatKit

### Conversation State Persistence
- Server-side persistence handled by ChatKit
- UI fetches conversation state on initial load
- UI maintains real-time synchronization with server state

## 7. Accessibility Specification (WCAG 2.1 AA)

### ARIA Roles and Landmarks
- Main landmark for primary content
- Banner landmark for header
- Complementary landmark for todo panel
- Log role for message list
- Article role for individual messages
- Search role for message input
- Status role for typing indicators

### Screen Reader Behavior
- New messages announced with polite priority
- Typing indicators announced when appearing
- Error messages announced with assertive priority
- Navigation landmarks properly labeled
- Interactive elements have descriptive labels

### Focus Management
- Focus returns to input after sending message
- Focus moves to new AI response when appropriate
- Command suggestions keyboard navigable
- Error elements receive focus when appearing
- Skip links provided for main content areas

### Keyboard Navigation
- Tab order follows visual hierarchy
- Arrow keys navigate command suggestions
- Enter/Return activates selected items
- Esc dismisses active elements
- Ctrl/Cmd combinations for power features

### Color Contrast
- Text/background contrast ratio ≥ 4.5:1
- Decorative elements exempt from contrast requirements
- Status indicators meet 3:1 contrast ratio
- Focus indicators meet 3:1 contrast ratio

### Theme Accessibility
- High contrast mode support
- Reduced motion preferences respected
- System color scheme detection
- Consistent semantic color usage across themes

## 8. Performance Requirements

### Message Rendering Limits
- Support 1000+ messages in conversation history
- Virtualize message list beyond 100 visible messages
- Maintain 60fps scrolling performance
- Implement progressive loading for long histories

### Streaming Performance
- Character-level updates display within 100ms of receipt
- Maintain smooth animation during response streaming
- Handle bursts of rapid updates without stuttering
- Implement intelligent throttling for high-frequency updates

### Long Response Handling
- Stream responses longer than 1000 characters smoothly
- Maintain UI responsiveness during long responses
- Implement scroll anchoring during streaming
- Handle network interruptions gracefully during streaming

### Mobile Performance
- Maintain 60fps animations and interactions
- Optimize for devices with 2GB RAM or less
- Minimize battery impact of real-time updates
- Optimize network usage for metered connections

### Responsiveness Targets
- Input field accepts keystrokes within 50ms
- Message submission processes within 200ms
- Command suggestions appear within 300ms
- Page navigation completes within 1000ms

## 9. Non-Goals / Explicit Exclusions

### Backend Implementation
- MCP tool development and configuration
- ChatKit conversation engine implementation
- Database schema design for conversations
- Authentication system implementation

### ChatKit Internals
- AI model selection or configuration
- Prompt engineering or template creation
- Conversation memory management algorithms
- Tool routing and orchestration logic

### MCP Tool Implementation
- Individual todo operation implementations
- API endpoint creation for tools
- MCP protocol implementation details
- Tool discovery and registration mechanisms

### Authentication Redesign
- User account creation workflows
- Password reset mechanisms
- Social login integration
- Multi-factor authentication implementation

## 10. Assumptions & Open Questions

### Assumptions
- Users have existing accounts in the todo application
- Network connectivity is generally reliable
- ChatKit and MCP infrastructure is already implemented
- Backend provides WebSocket support for real-time updates
- Users are familiar with chat interfaces
- Mobile devices support modern web standards

### Open Questions
- When a user account is deleted, all associated conversation history is immediately purged to protect user privacy.
- Rate limiting is handled by displaying error messages only when the limit is exceeded, without proactive countdown timers.
- The UI does not support offline message composition; messaging functionality is disabled when network connectivity is lost.