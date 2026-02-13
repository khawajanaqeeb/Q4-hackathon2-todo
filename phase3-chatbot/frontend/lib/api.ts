import { Todo, TodoCreate, TodoUpdate } from '../types/todo';

// Base API URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create a base request function with common headers
const makeRequest = async (endpoint: string, options: RequestInit = {}) => {
  // For the new proxy pattern, we route all API requests through our unified proxy
  // The proxy handles authentication and forwards to the backend appropriately
  let headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Handle tags conversion from array to JSON string for backend compatibility
  let modifiedOptions = { ...options };
  if (modifiedOptions.body && typeof modifiedOptions.body === 'string') {
    try {
      let bodyObj = JSON.parse(modifiedOptions.body);

      // Convert tags array to JSON string for backend compatibility
      // Backend expects tags as a JSON string, not as an array
      if (bodyObj.tags && Array.isArray(bodyObj.tags)) {
        bodyObj.tags = JSON.stringify(bodyObj.tags);
      }

      modifiedOptions.body = JSON.stringify(bodyObj);
    } catch (e) {
      // If parsing fails, continue with original body
      console.warn('Could not parse request body for tags conversion:', e);
    }
  }

  // Route API requests through our unified proxy which handles auth and forwards to backend
  // The proxy is located at /api/auth/[...path] and handles various routes:
  // - /login, /register -> backend /auth/
  // - /todos, /chat, etc. -> backend /api/todos, /chat, etc.
  // So we call the appropriate paths for the proxy to handle
  const proxyEndpoint = `/api/auth${endpoint}`;
  const response = await fetch(proxyEndpoint, {
    ...modifiedOptions,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    // Try to get error data, but handle various response types safely
    let errorData: Record<string, any> = {};
    try {
      // Clone the response to read it multiple times if needed
      const clonedResponse = response.clone();
      errorData = await clonedResponse.json();
    } catch (e) {
      // If response is not JSON, try to get text
      try {
        const clonedResponse = response.clone();
        const errorText = await clonedResponse.text();
        errorData = { detail: errorText || `HTTP error! status: ${response.status}` };
      } catch (textError) {
        // If we can't read the response at all, use generic message
        errorData = { detail: `HTTP error! status: ${response.status}` };
      }
    }

    // Check for new proxy error format first, then backend format
    let errorMessage = 'HTTP error!';

    // New proxy format: { error: string, details?: string }
    if (errorData.error) {
      if (typeof errorData.error === 'string') {
        errorMessage = errorData.error;
      } else if (typeof errorData.error === 'object') {
        // Handle case where error itself is an object
        try {
          errorMessage = JSON.stringify(errorData.error);
        } catch (e) {
          errorMessage = errorData.error.toString ? errorData.error.toString() : 'Error in error object';
        }
      } else {
        errorMessage = String(errorData.error);
      }

      if (errorData.details) {
        if (typeof errorData.details === 'string') {
          errorMessage += ` (${errorData.details})`;
        } else {
          try {
            errorMessage += ` (${JSON.stringify(errorData.details)})`;
          } catch (e) {
            errorMessage += ' (details serialization error)';
          }
        }
      }
    }
    // Backend format: { detail: string | object }
    else if (errorData.detail) {
      if (typeof errorData.detail === 'string') {
        errorMessage = errorData.detail;
      } else if (typeof errorData.detail === 'object') {
        try {
          errorMessage = JSON.stringify(errorData.detail);
        } catch (e) {
          // Fallback for circular references or other JSON issues
          errorMessage = errorData.detail.toString ? errorData.detail.toString() : 'Error occurred';
        }
      } else {
        errorMessage = String(errorData.detail);
      }
    } else {
      errorMessage = `HTTP error! status: ${response.status}`;
    }

    throw new Error(errorMessage);
  }

  return response.json();
};

// Auth API functions - these are public endpoints, so they call the backend directly
export const authAPI = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('email', email);
    formData.append('password', password);

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Properly serialize error detail to string
      let errorMessage = 'Login failed';
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object') {
          try {
            errorMessage = JSON.stringify(errorData.detail);
          } catch (e) {
            // Fallback for circular references or other JSON issues
            errorMessage = errorData.detail.toString ? errorData.detail.toString() : 'Error occurred';
          }
        } else {
          errorMessage = String(errorData.detail);
        }
      }

      throw new Error(errorMessage);
    }

    return response.json();
  },

  register: async (name: string, email: string, password: string) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, password }),
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      // Properly serialize error detail to string
      let errorMessage = 'Registration failed';
      if (errorData.detail) {
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (typeof errorData.detail === 'object') {
          try {
            errorMessage = JSON.stringify(errorData.detail);
          } catch (e) {
            // Fallback for circular references or other JSON issues
            errorMessage = errorData.detail.toString ? errorData.detail.toString() : 'Error occurred';
          }
        } else {
          errorMessage = String(errorData.detail);
        }
      }

      throw new Error(errorMessage);
    }

    return response.json();
  },
};

// Todo API functions
export const todoAPI = {
  getTodos: async (params?: {
    skip?: number;
    limit?: number;
    completed?: boolean;
    priority?: 'low' | 'medium' | 'high';
    search?: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, String(value));
        }
      });
    }

    const queryString = searchParams.toString();
    const endpoint = `/todos/${queryString ? `?${queryString}` : ''}`;

    return makeRequest(endpoint);
  },

  createTodo: async (todoData: TodoCreate) => {
    return makeRequest('/todos/', {
      method: 'POST',
      body: JSON.stringify(todoData),
    });
  },

  updateTodo: async (id: number, todoData: TodoUpdate) => {
    return makeRequest(`/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(todoData),
    });
  },

  deleteTodo: async (id: number) => {
    return makeRequest(`/todos/${id}`, {
      method: 'DELETE',
    });
  },

  toggleTodoCompletion: async (id: number) => {
    return makeRequest(`/todos/${id}/toggle`, {
      method: 'PATCH',
    });
  },
};