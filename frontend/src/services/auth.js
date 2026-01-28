import apiClient from './api';

class AuthService {
  /**
   * Register a new user
   */
  async register(username, email, password) {
    try {
      const response = await apiClient.post('/auth/register', {
        username,
        email,
        password,
      });

      // Store user info in localStorage (though session is maintained via cookies)
      if (response.data && response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  /**
   * Login user
   */
  async login(username, password) {
    try {
      // For login, we need to send credentials in the body
      // The session cookie will be set by the backend and automatically sent in subsequent requests
      const response = await apiClient.post('/auth/login', {
        username,
        password,
      }, {
        // Include credentials to allow setting the session cookie
        withCredentials: true,
      });

      // Store user info in localStorage (though session is maintained via cookies)
      if (response.data && response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  /**
   * Verify current session
   */
  async verifySession() {
    try {
      const response = await apiClient.get('/auth/verify');

      if (response.data && response.data.authenticated && response.data.user) {
        // Update user info in localStorage
        localStorage.setItem('user', JSON.stringify(response.data.user));
        return response.data;
      }

      return null;
    } catch (error) {
      // If verification fails, clear stored user info
      if (error.response?.status === 401) {
        this.logout();
      }
      return null;
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      await apiClient.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear stored user info
      localStorage.removeItem('user');
    }
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.getCurrentUser();
  }
}

export default new AuthService();