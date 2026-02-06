import { NextRequest, NextResponse } from 'next/server';
import { authLogger, logAuthVerification } from '../lib/auth/logging';
import { isDevMode, getDevSafeguards } from '../lib/auth/config';
import { originTracker } from '../lib/auth/origin-tracker';
import { authStateManager } from '../lib/auth/state-manager';
import { handleAuthError } from '../lib/auth/error-handler';

// Define protected routes that require authentication
const protectedRoutes = ['/dashboard', '/profile', '/settings', '/api/chat'];

// Define public routes that don't require authentication
const publicRoutes = ['/', '/login', '/register', '/api/auth'];

// Routes that are specifically for authentication
const authRoutes = ['/login', '/register', '/api/auth'];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isProtectedRoute = protectedRoutes.some(route => pathname.startsWith(route));
  const isAuthRoute = authRoutes.some(route => pathname.startsWith(route));
  const isPublicRoute = publicRoutes.some(route => pathname.startsWith(route));

  // Log the request for debugging
  authLogger.debug(`Middleware processing request: ${request.method} ${pathname}`, {
    isProtectedRoute,
    isAuthRoute,
    isPublicRoute,
    userAgent: request.headers.get('user-agent'),
    referer: request.headers.get('referer')
  });

  // Record this request in the origin tracker
  const requestId = originTracker.recordVerification(
    'middleware',
    pathname,
    request.method,
    `Middleware processing for ${pathname}`
  );

  // Check for potential recursive loops, but exclude auth verification routes
  // since legitimate auth checks can happen frequently during page load
  if (!pathname.includes('/api/auth/verify') && originTracker.detectRecursiveLoops(5000, 10)) {
    authLogger.error('Potential authentication verification loop detected in middleware', {
      pathname,
      method: request.method,
      requestId
    });

    // Return a response that breaks the loop instead of continuing
    return NextResponse.json(
      {
        error: 'Authentication verification loop detected',
        message: 'Too many authentication checks detected, please refresh the page'
      },
      { status: 429 } // Too Many Requests
    );
  }

  // Get auth token from cookies
  const token = request.cookies.get('auth_token')?.value;

  // If this is an auth route, we don't need to check authentication
  if (isAuthRoute) {
    authLogger.debug(`Skipping auth check for auth route: ${pathname}`);

    // For auth routes, ensure we don't create recursive loops
    if (pathname.startsWith('/api/auth/verify')) {
      // Check if this is a recursive call by looking at headers
      const originalUrl = request.headers.get('x-original-url') || request.url;
      const forwardedFor = request.headers.get('x-forwarded-for');

      authLogger.debug(`Auth verification route called`, {
        pathname,
        originalUrl,
        forwardedFor,
        hasToken: !!token
      });

      // Add a header to track the original URL to help detect recursion
      const response = NextResponse.next();
      response.headers.set('x-original-url', originalUrl);
      return response;
    }

    return NextResponse.next();
  }

  // If this is a public route, allow access without authentication check
  if (isPublicRoute) {
    authLogger.debug(`Allowing access to public route: ${pathname}`);
    return NextResponse.next();
  }

  // For protected routes, check authentication
  if (isProtectedRoute) {
    authLogger.debug(`Checking authentication for protected route: ${pathname}`, {
      hasToken: !!token,
      tokenExists: !!request.cookies.get('auth_token')
    });

    // If no token, redirect to login
    if (!token) {
      authLogger.info(`No auth token found for protected route ${pathname}, redirecting to login`);

      // Create a redirect response to the login page
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('return', encodeURIComponent(request.url)); // Preserve original URL

      const response = NextResponse.redirect(loginUrl);

      // Add headers to help detect potential loops
      response.headers.set('x-auth-status', 'unauthenticated');
      response.headers.set('x-requested-path', pathname);

      return response;
    }

    // If we have a token, we still need to verify it's valid
    // But we need to be careful not to create recursive calls to the verify endpoint
    if (pathname.startsWith('/api/auth')) {
      // For auth-related API calls, just pass through
      // The actual verification will happen in the API route itself
      authLogger.debug(`Passing through auth-related API call: ${pathname}`);

      const response = NextResponse.next();
      response.headers.set('x-auth-status', 'checking');
      return response;
    }

    // For non-auth API routes or protected pages, we could potentially verify the token
    // But to avoid recursion, we'll just check for the existence of the token here
    // The actual verification happens in the API layer or client-side
    authLogger.debug(`Token exists for protected route, allowing access: ${pathname}`);

    const response = NextResponse.next();
    response.headers.set('x-auth-status', 'authenticated');
    return response;
  }

  // For any other routes, allow access but log for monitoring
  authLogger.debug(`Allowing access to non-protected route: ${pathname}`);

  const response = NextResponse.next();
  response.headers.set('x-auth-status', 'open-route');
  return response;
}

// Define which routes the middleware should apply to
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    {
      source: '/((?!api\\/auth\\/\\.\\.\\.path|_next\\/static|_next\\/image|favicon\\.ico|public\\/).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' }
      ]
    }
  ]
};