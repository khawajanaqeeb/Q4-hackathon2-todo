// lib/auth.ts
export interface AuthState {
  isLoggedIn: boolean;
  user: UserInfo | null;
  token: string | null;
  isLoading: boolean;
}

export interface UserInfo {
  id: number;
  email: string;
  name: string;
  createdAt: Date;
}

/**
 * Verifies the Better Auth session from Phase 2
 * @returns Promise<AuthState> - The current authentication state
 */
export const verifyBetterAuthSession = async (): Promise<AuthState> => {
  // In a real implementation, this would interface with Better Auth
  // For now, we'll simulate the verification process
  try {
    // Simulate checking for a valid session in the browser
    const sessionToken = localStorage.getItem('better_auth_token');

    if (!sessionToken) {
      return {
        isLoggedIn: false,
        user: null,
        token: null,
        isLoading: false
      };
    }

    // In a real implementation, we'd verify the JWT token with the backend
    // For simulation, we'll decode the token to extract user info
    const decodedUser = decodeJWT(sessionToken);

    if (decodedUser && !isTokenExpired(decodedUser)) {
      return {
        isLoggedIn: true,
        user: {
          id: decodedUser.userId || 1,
          email: decodedUser.email || 'user@example.com',
          name: decodedUser.name || 'User',
          createdAt: new Date(decodedUser.createdAt || Date.now())
        },
        token: sessionToken,
        isLoading: false
      };
    } else {
      // Token is expired, clear it
      localStorage.removeItem('better_auth_token');
      return {
        isLoggedIn: false,
        user: null,
        token: null,
        isLoading: false
      };
    }
  } catch (error) {
    console.error('Error verifying session:', error);
    return {
      isLoggedIn: false,
      user: null,
      token: null,
      isLoading: false
    };
  }
};

/**
 * Extracts JWT token from session for API authentication
 * @param session - The Better Auth session object
 * @returns string - The JWT token for API requests
 */
export const extractJWTToken = (authState: AuthState): string | null => {
  return authState.token;
};

/**
 * Redirects unauthenticated users to login page
 * @param redirectTo - Optional path to redirect to after login
 */
export const redirectToLogin = (redirectTo?: string): void => {
  const redirectParam = redirectTo ? `?redirect=${encodeURIComponent(redirectTo)}` : '';
  window.location.href = `/login${redirectParam}`;
};

// Helper function to decode JWT token (simplified)
const decodeJWT = (token: string) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];
    // Add padding if needed
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    const decoded = atob(paddedPayload);
    return JSON.parse(decoded);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

// Helper function to check if token is expired
const isTokenExpired = (payload: any) => {
  if (!payload.exp) {
    return false; // No expiration set
  }

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
};