import { NextRequest, NextResponse } from 'next/server';

/**
 * Logout route for clearing authentication
 * Clears the auth cookie and invalidates the session
 */
export async function POST(request: NextRequest) {
  try {
    // Clear the auth cookie by setting it to expire immediately
    const response = NextResponse.json({ message: 'Logged out successfully' });
    response.cookies.set('auth_token', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 0, // This expires the cookie immediately
      path: '/',
      sameSite: 'strict',
    });

    return response;
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json({ error: 'Logout failed' }, { status: 500 });
  }
}