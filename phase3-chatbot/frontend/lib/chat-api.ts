// Frontend API client for chat endpoints

interface ChatMessageRequest {
  message: string;
  conversation_id?: string;
}

interface ChatMessageResponse {
  message: string;
  conversation_id: string;
  timestamp: string;
  action_taken: string;
  confirmation_message: string;
}

interface ConversationSummary {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

interface GetConversationsResponse {
  conversations: ConversationSummary[];
  total_count: number;
  limit: number;
  offset: number;
}

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata: any;
}

interface GetConversationMessagesResponse {
  conversation_id: string;
  title: string | null;
  messages: Message[];
}

class ChatAPIClient {
  private baseUrl: string;
  private authToken: string | null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.authToken = null;
  }

  setAuthToken(token: string) {
    this.authToken = token;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseUrl}${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorData}`);
    }

    return response.json();
  }

  async sendMessage(userId: string, request: ChatMessageRequest): Promise<ChatMessageResponse> {
    return this.request(`/chat/${userId}`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getUserConversations(userId: string, limit: number = 20, offset: number = 0): Promise<GetConversationsResponse> {
    const params = new URLSearchParams({ limit: limit.toString(), offset: offset.toString() });
    return this.request(`/chat/${userId}/conversations?${params}`);
  }

  async getConversationMessages(userId: string, conversationId: string): Promise<GetConversationMessagesResponse> {
    return this.request(`/chat/${userId}/conversations/${conversationId}`);
  }

  async deleteConversation(userId: string, conversationId: string): Promise<{ message: string }> {
    return this.request(`/chat/${userId}/conversations/${conversationId}`, {
      method: 'DELETE',
    });
  }
}

// Default export with base URL
const chatApiClient = new ChatAPIClient(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

export {
  ChatAPIClient,
  chatApiClient,
  type ChatMessageRequest,
  type ChatMessageResponse,
  type ConversationSummary,
  type GetConversationsResponse,
  type Message,
  type GetConversationMessagesResponse,
};