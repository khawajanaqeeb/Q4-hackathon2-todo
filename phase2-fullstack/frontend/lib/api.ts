import { Todo, TodoCreate, TodoUpdate } from '../types/todo';

// Base API URL from environment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create a base request function with common headers
const makeRequest = async (endpoint: string, options: RequestInit = {}) => {
  // For the new proxy pattern, we route all authenticated requests through our proxy
  // The proxy will handle authentication and forward to the backend
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Route the request through our unified auth proxy (catches all /api/auth/*)
  const proxyEndpoint = `/api/auth${endpoint}`;
  const response = await fetch(proxyEndpoint, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // Check for new proxy error format first, then backend format
    let errorMessage = 'HTTP error!';

    // New proxy format: { error: string, details?: string }
    if (errorData.error) {
      errorMessage = errorData.error;
      if (errorData.details) {
        errorMessage += ` (${errorData.details})`;
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
    const endpoint = `/todos${queryString ? `?${queryString}` : ''}`;

    return makeRequest(endpoint);
  },

  createTodo: async (todoData: TodoCreate) => {
    return makeRequest('/todos', {
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