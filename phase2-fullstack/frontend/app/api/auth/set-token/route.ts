import { NextRequest, NextResponse } from 'next/server';

/**
 * Set authentication token as httpOnly cookie
 * This endpoint is called after successful login to store the JWT token securely
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { access_token } = body;

    if (!access_token) {
      return NextResponse.json(
        { error: 'Access token is required' },
        { status: 400 }
      );
    }

    // Create response and set the auth cookie
    const response = NextResponse.json({ success: true });

    response.cookies.set('auth_token', access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 30, // 30 minutes (matches backend ACCESS_TOKEN_EXPIRE_MINUTES)
      path: '/',
      sameSite: 'strict',
    });

    return response;
  } catch (error) {
    console.error('Set token error:', error);
    return NextResponse.json(
      { error: 'Failed to set token' },
      { status: 500 }
    );
  }
}
