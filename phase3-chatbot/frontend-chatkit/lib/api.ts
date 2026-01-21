// lib/api.ts
import { AuthState } from './auth';

export interface APIConfig {
  baseUrl: string;
  headers: Record<string, string>;
  timeout: number;
}

export interface ChatRequest {
  message: string;
  userId: number;
  timestamp: Date;
}

export interface ApiResponse {
  response: string;
  routing_decision: string | null;
  handoff: boolean;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sent' | 'delivered' | 'error';
}

/**
 * Makes authenticated requests to the backend
 * @param endpoint - The API endpoint to call
 * @param options - Request options including method, body, etc.
 * @param authState - The current authentication state
 * @returns Promise<any> - The API response
 */
export const makeAuthenticatedRequest = async (
  endpoint: string,
  options: RequestInit = {},
  authState: AuthState
): Promise<any> => {
  const baseUrl = process.env.NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL || 'http://localhost:8000';
  const apiUrl = `${baseUrl}${endpoint}`;

  // Ensure we have a valid token
  if (!authState.token) {
    throw new Error('No authentication token available');
  }

  // Create default headers
  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authState.token}`,
  };

  // Safely merge headers
  const mergedHeaders: Record<string, string> = { ...defaultHeaders };

  if (options.headers) {
    if (options.headers instanceof Headers) {
      // If headers is a Headers object, convert to plain object
      options.headers.forEach((value, key) => {
        mergedHeaders[key] = value;
      });
    } else if (typeof options.headers === 'object') {
      // If headers is a plain object, merge safely
      Object.entries(options.headers).forEach(([key, value]) => {
        if (typeof value === 'string') {
          mergedHeaders[key] = value;
        }
      });
    }
  }

  const config: APIConfig = {
    baseUrl,
    headers: mergedHeaders,
    timeout: 30000, // 30 seconds
  };

  const requestOptions: RequestInit = {
    ...options,
    headers: config.headers,
  };

  try {
    const response = await fetch(apiUrl, requestOptions);

    if (!response.ok) {
      // Handle specific error statuses
      if (response.status === 401) {
        throw new Error('Unauthorized: Invalid or expired session');
      } else if (response.status === 403) {
        throw new Error('Forbidden: Access denied');
      } else if (response.status === 422) {
        throw new Error('Validation Error: Invalid request format');
      } else if (response.status >= 500) {
        throw new Error(`Server Error: ${response.statusText}`);
      } else {
        throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
      }
    }

    return await response.json();
  } catch (error) {
    console.error('API request error:', error);
    throw error;
  }
};

/**
 * Sends a chat message to the backend API
 * @param message - The user's message to send
 * @param userId - The ID of the authenticated user
 * @param authState - The current authentication state
 * @returns Promise<ApiResponse> - The AI response from the backend
 */
export const sendChatMessage = async (
  message: string,
  userId: number,
  authState: AuthState
): Promise<ApiResponse> => {
  const chatRequest: ChatRequest = {
    message,
    userId,
    timestamp: new Date(),
  };

  const response = await makeAuthenticatedRequest(
    `/api/${userId}/chat`,
    {
      method: 'POST',
      body: JSON.stringify(chatRequest),
    },
    authState
  );

  return response;
};

/**
 * Checks the health of the backend API
 * @returns Promise<boolean> - Whether the backend is healthy
 */
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const baseUrl = process.env.NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${baseUrl}/health`);

    if (!response.ok) {
      return false;
    }

    const healthData = await response.json();
    return healthData.status === 'healthy';
  } catch (error) {
    console.error('Health check error:', error);
    return false;
  }
};