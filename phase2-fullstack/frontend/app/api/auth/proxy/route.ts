import { NextRequest, NextResponse } from 'next/server';

/**
 * Root proxy route for authentication verification (no path)
 * This handles GET /api/auth/proxy which is used for user verification
 */
export async function GET(request: NextRequest) {
  // Extract token from cookies or authorization header
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Verify the token with the backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const userData = await response.json();
      return NextResponse.json(userData);
    } else {
      return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
    }
  } catch (error) {
    console.error('Auth verification error:', error);
    return NextResponse.json({ error: 'Authentication service unavailable' }, { status: 503 });
  }
}

export async function POST(request: NextRequest) {
  // Handle authentication verification
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Auth proxy error:', error);
    return NextResponse.json({ error: 'Authentication service unavailable' }, { status: 503 });
  }
}
