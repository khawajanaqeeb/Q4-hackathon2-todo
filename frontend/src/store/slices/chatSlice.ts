import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Message, Conversation } from '@/types';

interface ChatState {
  conversations: Record<string, Conversation>;
  messages: Record<string, Message[]>;
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
}

const initialState: ChatState = {
  conversations: {},
  messages: {},
  currentConversationId: null,
  isLoading: false,
  error: null,
  isConnected: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // Connection actions
    setConnectionStatus(state, action: PayloadAction<boolean>) {
      state.isConnected = action.payload;
    },

    // Conversation actions
    setCurrentConversation(state, action: PayloadAction<string>) {
      state.currentConversationId = action.payload;
    },

    addConversation(state, action: PayloadAction<Conversation>) {
      state.conversations[action.payload.id] = action.payload;
    },

    // Message actions
    addMessage(state, action: PayloadAction<{ conversationId: string; message: Message }>) {
      const { conversationId, message } = action.payload;
      if (!state.messages[conversationId]) {
        state.messages[conversationId] = [];
      }
      state.messages[conversationId].push(message);
    },

    updateMessageStatus(state, action: PayloadAction<{ conversationId: string; messageId: string; status: string }>) {
      const { conversationId, messageId, status } = action.payload;
      if (state.messages[conversationId]) {
        const messageIndex = state.messages[conversationId].findIndex(msg => msg.id === messageId);
        if (messageIndex !== -1) {
          state.messages[conversationId][messageIndex].status = status as any;
        }
      }
    },

    // Loading and error actions
    setLoading(state, action: PayloadAction<boolean>) {
      state.isLoading = action.payload;
    },

    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },

    // Batch message addition
    addMessages(state, action: PayloadAction<{ conversationId: string; messages: Message[] }>) {
      const { conversationId, messages } = action.payload;
      if (!state.messages[conversationId]) {
        state.messages[conversationId] = [];
      }
      state.messages[conversationId].push(...messages);
    },
  },
});

export const {
  setConnectionStatus,
  setCurrentConversation,
  addConversation,
  addMessage,
  updateMessageStatus,
  setLoading,
  setError,
  addMessages,
} = chatSlice.actions;

export default chatSlice.reducer;