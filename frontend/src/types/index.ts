// Message types
export type MessageSender = 'user' | 'ai';

export type MessageStatus = 'sent' | 'delivered' | 'failed' | 'streaming';

export interface Message {
  id: string;
  content: string;
  sender: MessageSender;
  timestamp: Date;
  status: MessageStatus;
  metadata?: object;
}

// Conversation types
export interface Conversation {
  id: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
  isActive: boolean;
}

// TodoItem types (referenced from existing system)
export type TodoPriority = 'low' | 'medium' | 'high';

export interface TodoItem {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: TodoPriority;
  dueDate?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// CommandSuggestion types
export interface CommandSuggestion {
  id: string;
  text: string;
  category: string;
  context: string;
  isUsed: boolean;
}

// UIState types
export type ThemePreference = 'light' | 'dark';

export interface UIState {
  inputText: string;
  isInputDisabled: boolean;
  scrollPosition: number;
  activeTheme: ThemePreference;
  isTypingIndicatorVisible: boolean;
  commandSuggestionsVisible: boolean;
}

// API Response types
export interface ChatMessageResponse {
  message: string;
  conversation_id: string;
  timestamp: string;
  action_taken: string;
  confirmation_message: string;
}

export interface ConversationSummary {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface GetConversationsResponse {
  conversations: ConversationSummary[];
  total_count: number;
  limit: number;
  offset: number;
}

export interface InvokeToolResponse {
  success: boolean;
  result?: object;
  error?: string;
  tool_name: string;
  provider: string;
}

export interface ToolInfo {
  name: string;
  description: string;
  provider: string;
  has_access: boolean;
}

// State transition types
export type MessageTransition =
  | { from: 'draft'; to: 'sent' }
  | { from: 'sent'; to: 'delivered' }
  | { from: 'sent'; to: 'failed' }
  | { from: 'delivered'; to: 'streaming' }
  | { from: 'streaming'; to: 'delivered' };

export type TodoItemTransition =
  | { from: 'active'; to: 'completed' }
  | { from: 'active'; to: 'updated' }
  | { from: 'created'; to: 'active' }
  | { from: 'active'; to: 'deleted' };

export type UIStateTransition =
  | { type: 'INPUT_FOCUS' | 'INPUT_BLUR'; field: 'isInputDisabled' }
  | { type: 'MESSAGE_RECEIVED'; field: 'scrollPosition' }
  | { type: 'THEME_CHANGE'; field: 'activeTheme' }
  | { type: 'AI_PROCESSING'; field: 'isTypingIndicatorVisible' }
  | { type: 'CONTEXT_CHANGE'; field: 'commandSuggestionsVisible' };