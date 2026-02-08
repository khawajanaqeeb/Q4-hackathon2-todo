'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';

// Define types
interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
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

// Initial state - start with loading true, but handle hydration properly
const initialState: AuthState = {
  user: null,
  token: null,
  loading: true, // Start with loading true for both server and client
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

  // Check for existing auth status on initial load
  useEffect(() => {
    // Prevent hydration mismatch by only running on the client
    if (typeof window === 'undefined') return;

    // Delay setting loading to false to allow hydration to complete
    const timer = setTimeout(() => {
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
    }, 0); // Small delay to ensure hydration completes

    // Cleanup function
    return () => clearTimeout(timer);
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
          username: email,  // OAuth2 standard uses 'username' field (can be email or username)
          password,
        }),
      });

      const tokenData = await response.json();
      
      if (response.ok) {
        // Token is now automatically set in httpOnly cookie by the proxy

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
        dispatch({ type: 'ERROR' });
        throw new Error(tokenData.error || tokenData.detail || 'Login failed');
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
      // Backend expects form data with username, email, password
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: name,
          email,
          password,
        }),
      });

      const registerData = await response.json();
      
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

        const loginData = await loginResponse.json();
        
        if (loginResponse.ok) {
          // Token is now automatically set in httpOnly cookie by the proxy

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
          dispatch({ type: 'ERROR' });
          throw new Error(loginData.error || loginData.detail || 'Registration successful but login failed');
        }
      } else {
        dispatch({ type: 'ERROR' });
        throw new Error(registerData.error || registerData.detail || 'Registration failed');
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