// frontend/src/services/chatApi.js
import axios from 'axios';

// Create an axios instance with default configuration
const chatApi = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  withCredentials: true, // This ensures cookies are sent with requests for authentication
});

// Request interceptor to add any needed headers
chatApi.interceptors.request.use(
  (config) => {
    // Add authentication token if available (if using token-based auth in addition to cookies)
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common responses
chatApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Redirect to login if unauthorized
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

// API methods for chat functionality
const chatApiService = {
  /**
   * Send a message to the chat endpoint
   * @param {string} message - The user's message
   * @param {string} [conversationId] - Optional conversation ID for continuing a conversation
   * @returns {Promise<Object>} Response from the chat endpoint
   */
  sendMessage: async (message, conversationId = null) => {
    try {
      const response = await chatApi.post('/chat/messages', {
        message,
        conversation_id: conversationId
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  /**
   * Get streaming response from chat endpoint
   * @param {string} message - The user's message
   * @param {string} [conversationId] - Optional conversation ID
   * @param {Function} onMessage - Callback function to handle incoming messages
   * @returns {Promise<Object>} Response from the streaming endpoint
   */
  sendStreamMessage: async (message, conversationId = null, onMessage) => {
    try {
      // For server-sent events, we'll use fetch instead of axios
      const response = await fetch(`${chatApi.defaults.baseURL}/chat/stream?message=${encodeURIComponent(message)}${conversationId ? `&conversation_id=${conversationId}` : ''}`, {
        method: 'GET',
        credentials: 'include', // Include cookies for authentication
        headers: {
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        }
      });

      if (response.ok) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop(); // Last element might be incomplete

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // Remove 'data: ' prefix
              if (data.trim()) {
                try {
                  const parsedData = JSON.parse(data);
                  onMessage(parsedData);

                  // If the message indicates completion, we can break
                  if (parsedData.done) {
                    return parsedData;
                  }
                } catch (e) {
                  console.error('Error parsing SSE data:', e);
                }
              }
            }
          }
        }
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error in streaming message:', error);
      throw error;
    }
  },

  /**
   * Get user's conversation history
   * @returns {Promise<Array>} List of user's conversations
   */
  getUserConversations: async () => {
    try {
      const response = await chatApi.get('/chat/conversations');
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  /**
   * Get details of a specific conversation
   * @param {string} conversationId - The ID of the conversation to retrieve
   * @returns {Promise<Object>} Conversation details with messages
   */
  getConversationDetails: async (conversationId) => {
    try {
      const response = await chatApi.get(`/chat/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversation details:', error);
      throw error;
    }
  },

  /**
   * Create a new conversation
   * @param {string} title - Title for the new conversation
   * @returns {Promise<Object>} Created conversation details
   */
  createConversation: async (title) => {
    try {
      const response = await chatApi.post('/chat/conversations', {
        title
      });
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  /**
   * Delete a conversation
   * @param {string} conversationId - The ID of the conversation to delete
   * @returns {Promise<Object>} Deletion confirmation
   */
  deleteConversation: async (conversationId) => {
    try {
      const response = await chatApi.delete(`/chat/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  },

  /**
   * Archive a conversation
   * @param {string} conversationId - The ID of the conversation to archive
   * @returns {Promise<Object>} Archival confirmation
   */
  archiveConversation: async (conversationId) => {
    try {
      const response = await chatApi.post(`/chat/conversations/${conversationId}/archive`);
      return response.data;
    } catch (error) {
      console.error('Error archiving conversation:', error);
      throw error;
    }
  }
};

export default chatApiService;