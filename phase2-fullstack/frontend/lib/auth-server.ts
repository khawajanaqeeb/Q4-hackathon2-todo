'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

/**
 * Server-side authentication utility functions
 * Used for protecting routes at the server level
 */

export async function requireAuth(): Promise<{ user: any }> {
  // Get the auth token from cookies
  const cookieStore = await cookies();
  const token = cookieStore.get('auth_token')?.value;

  if (!token) {
    // Redirect to login if no token exists
    redirect('/login');
  }

  try {
    // Verify the token with the backend via the proxy route
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/proxy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Cookie': `auth_token=${token}`,
      },
    });

    if (response.ok) {
      const userData = await response.json();
      return { user: userData };
    } else {
      // Redirect to login if token is invalid
      redirect('/login');
    }
  } catch (error) {
    console.error('Server auth verification error:', error);
    // Redirect to login on error
    redirect('/login');
  }
}

export async function checkAuth(): Promise<{ user: any } | null> {
  // Get the auth token from cookies
  const cookieStore = await cookies();
  const token = cookieStore.get('auth_token')?.value;

  if (!token) {
    return null;
  }

  try {
    // Verify the token with the backend via the proxy route
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/proxy`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Cookie': `auth_token=${token}`,
      },
    });

    if (response.ok) {
      const userData = await response.json();
      return { user: userData };
    } else {
      return null;
    }
  } catch (error) {
    console.error('Server auth check error:', error);
    return null;
  }
}