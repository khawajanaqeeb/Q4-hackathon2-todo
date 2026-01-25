import axios, { AxiosInstance } from 'axios';
import {
  Message,
  ChatMessageResponse,
  GetConversationsResponse,
  ConversationSummary,
} from '@/types';

const API_BASE_URL = process.env.REACT_APP_CHAT_API_URL || '/chat';

class ChatApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication if needed
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Send a message to the chatbot
   */
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatMessageResponse> {
    try {
      const response = await this.client.post<ChatMessageResponse>(`/${userId}`, {
        message,
        conversation_id: conversationId,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to send message: ${(error as Error).message}`);
    }
  }

  /**
   * Get user's conversations
   */
  async getUserConversations(
    userId: string,
    limit: number = 20,
    offset: number = 0
  ): Promise<GetConversationsResponse> {
    try {
      const response = await this.client.get<GetConversationsResponse>(`/${userId}/conversations`, {
        params: { limit, offset },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch conversations: ${(error as Error).message}`);
    }
  }

  /**
   * Get messages from a specific conversation
   */
  async getConversationMessages(userId: string, conversationId: string): Promise<{
    conversation_id: string;
    title?: string;
    messages: Message[];
  }> {
    try {
      const response = await this.client.get<{
        conversation_id: string;
        title?: string;
        messages: Message[];
      }>(`/${userId}/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch conversation messages: ${(error as Error).message}`);
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(userId: string, conversationId: string): Promise<{ message: string }> {
    try {
      const response = await this.client.delete<{ message: string }>(
        `/${userId}/conversations/${conversationId}`
      );
      return response.data;
    } catch (error) {
      throw new Error(`Failed to delete conversation: ${(error as Error).message}`);
    }
  }
}

export default new ChatApiService();