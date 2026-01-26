'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { verifyAuthentication, getVerificationState, useVerificationStatus } from './verification';
import { authStateManager } from './state-manager';
import { authLogger } from './logging';
import { isDevMode } from './config';

// Define the authentication context type
interface AuthContextType {
  isAuthenticated: boolean;
  user: any | null;
  isLoading: boolean;
  error: string | null;
  verifyAuth: () => Promise<void>;
  logout: () => void;
  status: ReturnType<typeof useVerificationStatus>;
}

// Create the authentication context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider Props
interface AuthProviderProps {
  children: ReactNode;
  initialState?: {
    isAuthenticated?: boolean;
    user?: any;
  };
}

// Auth Provider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children, initialState }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(initialState?.isAuthenticated ?? false);
  const [user, setUser] = useState(initialState?.user ?? null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get verification status
  const status = useVerificationStatus();

  // Effect to initialize auth state
  useEffect(() => {
    const initializeAuth = async () => {
      setIsLoading(true);
      setError(null);

      try {
        authLogger.info('Initializing authentication provider');

        // Check if we're already in a verification process
        if (authStateManager.isVerificationInProgress()) {
          authLogger.debug('Verification already in progress, waiting for completion');

          // Wait a bit and check the state again
          await new Promise(resolve => setTimeout(resolve, 500));
        }

        // Perform authentication verification
        const result = await verifyAuthentication({ includeUserDetails: true });

        if (result.isAuthenticated) {
          setIsAuthenticated(true);
          setUser(result.user || null);
          authLogger.info('Authentication provider initialized with authenticated user', {
            userId: result.user?.id
          });
        } else {
          setIsAuthenticated(false);
          setUser(null);
          authLogger.info('Authentication provider initialized as unauthenticated');
        }

        if (result.error) {
          setError(result.error);
          authLogger.warn('Authentication provider initialization had errors', {
            error: result.error
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Authentication initialization failed');
        setIsAuthenticated(false);
        setUser(null);
        authLogger.error('Error initializing authentication provider', {
          error: err instanceof Error ? err.message : String(err),
          stack: err instanceof Error ? err.stack : undefined
        });
      } finally {
        setIsLoading(false);
      }
    };

    // Only initialize on the client side
    if (typeof window !== 'undefined') {
      initializeAuth();
    }
  }, []);

  // Function to verify authentication
  const verifyAuth = async () => {
    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Verifying authentication via provider');

      const result = await verifyAuthentication({
        forceRefresh: true,
        includeUserDetails: true
      });

      if (result.isAuthenticated) {
        setIsAuthenticated(true);
        setUser(result.user || null);
        authLogger.info('Authentication verification succeeded via provider', {
          userId: result.user?.id
        });
      } else {
        setIsAuthenticated(false);
        setUser(null);
        authLogger.info('Authentication verification failed via provider');
      }

      if (result.error) {
        setError(result.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication verification failed');
      authLogger.error('Error during authentication verification in provider', {
        error: err instanceof Error ? err.message : String(err)
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle logout
  const logout = () => {
    authLogger.info('Logout initiated via provider');

    // Clear auth state
    authStateManager.clearAuth();

    // Clear user state
    setIsAuthenticated(false);
    setUser(null);
    setError(null);

    // Remove token from localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }

    authLogger.info('Logout completed via provider');
  };

  // Value to provide to consumers
  const value: AuthContextType = {
    isAuthenticated,
    user,
    isLoading,
    error,
    verifyAuth,
    logout,
    status
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }

  return context;
};

// Higher-order component to wrap components that require authentication
export const withAuth = (Component: React.ComponentType<any>) => {
  return (props: any) => {
    const { isAuthenticated, isLoading, verifyAuth } = useAuth();

    useEffect(() => {
      if (!isAuthenticated && !isLoading) {
        verifyAuth();
      }
    }, [isAuthenticated, isLoading, verifyAuth]);

    if (isLoading) {
      return <div>Loading...</div>; // Or a proper loading component
    }

    if (!isAuthenticated) {
      return <div>Please log in</div>; // Or redirect to login
    }

    return <Component {...props} />;
  };
};

// Component to guard routes based on authentication
export const AuthGuard: React.FC<{
  children: ReactNode;
  fallback?: ReactNode;
  loading?: ReactNode;
}> = ({ children, fallback = <div>Access denied</div>, loading = <div>Loading...</div> }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return loading;
  }

  if (!isAuthenticated) {
    return fallback;
  }

  return <>{children}</>;
};

// Component to guard routes based on authentication with redirect
export const ProtectedRoute: React.FC<{
  children: ReactNode;
  redirectTo?: string;
  loading?: ReactNode;
}> = ({ children, redirectTo = '/login', loading = <div>Loading...</div> }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return loading;
  }

  if (!isAuthenticated) {
    // In a real app, you'd use Next.js router to redirect
    if (typeof window !== 'undefined') {
      window.location.href = redirectTo;
    }
    return <div>Redirecting...</div>;
  }

  return <>{children}</>;
};