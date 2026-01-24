'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Define types
interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

interface AuthAction {
  type: string;
  payload?: any;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateUser: (userData: Partial<User>) => void;
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  loading: true,
};

// Auth context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Reducer for state management
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false
      };
    case 'REGISTER_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false
      };
    case 'LOGOUT':
      return { ...initialState, loading: false };
    case 'SET_USER':
      return { ...state, user: action.payload, loading: false };
    case 'ERROR':
      return { ...state, loading: false };
    default:
      return state;
  }
};

// Auth provider component
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on initial load
  useEffect(() => {
    // In the new proxy pattern, tokens are stored in cookies
    // We'll check for authentication status using the unified auth proxy
    const checkAuth = async () => {
      try {
        const response = await fetch('/api/auth/verify', {
          method: 'GET',
        });
        if (response.ok) {
          const userData = await response.json();
          dispatch({ type: 'SET_USER', payload: userData });
        } else {
          dispatch({ type: 'LOGOUT' });
        }
      } catch (error) {
        dispatch({ type: 'LOGOUT' });
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      // Use the unified auth proxy - it handles cookie setting automatically
      // OAuth2PasswordRequestForm expects 'username' field (we pass email as username)
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: email,  // OAuth2 standard uses 'username' field
          password,
        }),
      });

      if (response.ok) {
        // Token is now automatically set in httpOnly cookie by the proxy
        const tokenData = await response.json();

        // Verify the user with the token in the cookie
        const userDataResponse = await fetch('/api/auth/verify', {
          method: 'GET',
        });

        if (userDataResponse.ok) {
          const userData = await userDataResponse.json();
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: { user: userData, token: null } // Token is handled via cookies now
          });
        } else {
          dispatch({ type: 'ERROR' });
          throw new Error('Failed to verify user after login');
        }
      } else {
        const errorData = await response.json();
        dispatch({ type: 'ERROR' });
        throw new Error(errorData.error || errorData.detail || 'Login failed');
      }
    } catch (error) {
      dispatch({ type: 'ERROR' });
      // Ensure we throw an Error object with a proper message
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error(String(error) || 'An unexpected error occurred');
      }
    }
  };

  // Register function
  const register = async (name: string, email: string, password: string) => {
    dispatch({ type: 'LOGIN_START' });

    try {
      // Use the unified auth proxy for registration
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          email,
          password,
        }),
      });

      if (response.ok) {
        // After successful registration, log the user in through the proxy
        // OAuth2PasswordRequestForm expects 'username' field (we pass email as username)
        const loginResponse = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: email,  // OAuth2 standard uses 'username' field
            password,
          }),
        });

        if (loginResponse.ok) {
          // Token is now automatically set in httpOnly cookie by the proxy
          const tokenData = await loginResponse.json();

          // Verify the user with the token in the cookie
          const userDataResponse = await fetch('/api/auth/verify', {
            method: 'GET',
          });

          if (userDataResponse.ok) {
            const userData = await userDataResponse.json();
            dispatch({
              type: 'REGISTER_SUCCESS',
              payload: { user: userData, token: null } // Token is handled via cookies now
            });
          } else {
            dispatch({ type: 'ERROR' });
            throw new Error('Failed to verify user after registration');
          }
        } else {
          const errorData = await loginResponse.json();
          dispatch({ type: 'ERROR' });
          throw new Error(errorData.error || errorData.detail || 'Registration successful but login failed');
        }
      } else {
        const errorData = await response.json();
        dispatch({ type: 'ERROR' });
        throw new Error(errorData.error || errorData.detail || 'Registration failed');
      }
    } catch (error) {
      dispatch({ type: 'ERROR' });
      // Ensure we throw an Error object with a proper message
      if (error instanceof Error) {
        throw error;
      } else {
        throw new Error(String(error) || 'An unexpected error occurred');
      }
    }
  };

  // Logout function
  const logout = () => {
    // In the new system, logout is handled by clearing the auth cookie
    // We can make a request to a logout endpoint or clear the session
    fetch('/api/auth/logout', {
      method: 'POST',
    }).finally(() => {
      dispatch({ type: 'LOGOUT' });
    });
  };

  // Update user function
  const updateUser = (userData: Partial<User>) => {
    dispatch({
      type: 'SET_USER',
      payload: { ...state.user, ...userData }
    });
  };

  const value = {
    user: state.user,
    token: state.token,
    loading: state.loading,
    login,
    register,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};