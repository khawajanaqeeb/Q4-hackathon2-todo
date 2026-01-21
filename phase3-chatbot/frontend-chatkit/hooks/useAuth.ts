// hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { verifyBetterAuthSession, AuthState, redirectToLogin } from '../lib/auth';

/**
 * Custom authentication hook for managing authentication state in components
 * @returns AuthState - The current authentication state with loading and user info
 */
const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isLoggedIn: false,
    user: null,
    token: null,
    isLoading: true
  });

  /**
   * Refreshes the authentication state by verifying the current session
   */
  const refreshAuth = async () => {
    setAuthState(prev => ({ ...prev, isLoading: true }));

    const newAuthState = await verifyBetterAuthSession();
    setAuthState({ ...newAuthState, isLoading: false });
  };

  useEffect(() => {
    // Initialize auth state when the hook mounts
    refreshAuth();
  }, []);

  /**
   * Redirects to login if not authenticated
   * @param redirectTo - Optional path to redirect to after login
   */
  const requireAuth = (redirectTo?: string) => {
    if (!authState.isLoggedIn) {
      redirectToLogin(redirectTo);
    }
  };

  return {
    ...authState,
    refreshAuth,
    requireAuth
  };
};

export default useAuth;