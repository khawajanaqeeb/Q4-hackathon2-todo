import { NextRequest, NextResponse } from 'next/server';
import { safeJsonParse, createErrorResponse } from '../../../../lib/api-utils';

/**
 * UNIFIED AUTHENTICATION PROXY
 * Handles all auth and backend API proxying.
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL!;
const COOKIE_NAME = 'auth_token';
const COOKIE_MAX_AGE = 60 * 30; // 30 minutes

const PUBLIC_ROUTES = ['/login', '/register'];
const AUTH_ROUTES = ['/login', '/register', '/logout', '/refresh', '/verify'];
const SPECIAL_ROUTES = {
  LOGOUT: '/logout',
  REFRESH: '/refresh',
  VERIFY: '/verify',
};

// Request counter to detect potential loops
const requestCounts = new Map<string, { count: number; timestamp: number }>();

// Function to increment and check request count for a specific path
function incrementRequestCount(path: string, maxAttempts: number = 5): boolean {
  const key = `${path}_${new Date().toISOString().split('T')[0]}`; // Daily count
  const now = Date.now();

  const current = requestCounts.get(key);
  if (current) {
    // Reset count if it's been more than 10 minutes since last request (for development)
    // This allows more flexibility during development when pages are reloaded frequently
    if (now - current.timestamp > 600000) { // 10 minutes instead of 5 minutes
      requestCounts.set(key, { count: 1, timestamp: now });
      return true;
    }

    if (current.count >= maxAttempts) {
      console.warn(`[Proxy] Maximum verification attempts (${maxAttempts}) reached for path: ${path}`);
      return false; // Too many attempts
    }

    requestCounts.set(key, { count: current.count + 1, timestamp: now });
  } else {
    requestCounts.set(key, { count: 1, timestamp: now });
  }

  return true;
}

// Function to get current request count
function getRequestCount(path: string): number {
  const key = `${path}_${new Date().toISOString().split('T')[0]}`;
  const current = requestCounts.get(key);
  return current ? current.count : 0;
}

/**
 * Extract auth token from cookies or header
 */
function getAuthToken(request: NextRequest): string | null {
  const tokenFromCookie = request.cookies.get(COOKIE_NAME)?.value || null;
  const tokenFromHeader = request.headers.get('Authorization')?.replace('Bearer ', '') || null;

  return tokenFromCookie || tokenFromHeader;
}

/**
 * Set auth cookie
 */
function setAuthCookie(response: NextResponse, token: string) {
  response.cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: COOKIE_MAX_AGE,
    path: '/',
    sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
  });
}

/**
 * Clear auth cookie
 */
function clearAuthCookie(response: NextResponse) {
  response.cookies.set(COOKIE_NAME, '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 0,
    path: '/',
    sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
  });
}

/**
 * Build backend URL
 */
function buildBackendUrl(path: string, searchParams: string): string {
  const isAuthRoute = AUTH_ROUTES.some(route => path === route || path.startsWith(route + '/'));
  const queryString = searchParams ? searchParams : '';

  return isAuthRoute
    ? `${BACKEND_URL}/auth${path}${queryString}`
    : `${BACKEND_URL}${path}${queryString}`;
}

/**
 * Proxy request to backend with Authorization header
 */
async function proxyToBackend(
  method: string,
  url: string,
  token: string | null,
  body?: any
): Promise<Response> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };

  const options: RequestInit = {
    method,
    headers,
    redirect: 'manual' // Prevent automatic redirects to maintain auth headers
  };
  if (body && !['GET', 'DELETE'].includes(method)) options.body = JSON.stringify(body);

  return fetch(url, options);
}

/**
 * Main handler for all methods
 */
async function handleRequest(
  method: string,
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search ? url.search : '';
  const token = getAuthToken(request);

  // Log for debugging
  if (!token && !PUBLIC_ROUTES.includes(apiPath)) {
    console.warn(`[Proxy] No auth token found for ${method} ${apiPath}`);
  }

  // Handle public routes: login/register
  if (PUBLIC_ROUTES.includes(apiPath)) {
    try {
      const backendUrl = buildBackendUrl(apiPath, searchParams);
      const contentType = request.headers.get('content-type') || '';
      let body: any = null;

      if (contentType.includes('application/json')) body = await request.json().catch(() => null);
      else if (contentType.includes('application/x-www-form-urlencoded')) body = await request.text();

      const backendResponse =
        apiPath === '/login' && contentType.includes('application/x-www-form-urlencoded')
          ? await fetch(backendUrl, { method, headers: { 'Content-Type': contentType }, body })
          : await proxyToBackend(method, backendUrl, null, body);

      if (!backendResponse.ok) {
        const errorData = await safeJsonParse(backendResponse).catch(() => null);
        const message = errorData?.error || errorData?.detail || 'Authentication failed';
        return createErrorResponse(message, backendResponse.status);
      }

      const data = await safeJsonParse(backendResponse);
      const response = NextResponse.json(data, { status: backendResponse.status });

      // Set cookie if token exists
      const tokenFromData = data.access_token || data.token;
      if (tokenFromData) setAuthCookie(response, tokenFromData);

      return response;
    } catch (error) {
      console.error('[Proxy] Public route error:', error);
      return createErrorResponse('Authentication service unavailable', 503);
    }
  }

  // Special handling for logout route
  if (apiPath === SPECIAL_ROUTES.LOGOUT) {
    try {
      const response = NextResponse.json({ message: 'Logged out successfully' });
      clearAuthCookie(response);
      return response;
    } catch (error) {
      console.error('[Proxy] Logout error:', error);
      return createErrorResponse(
        'Logout service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // Special handling for refresh route
  if (apiPath === SPECIAL_ROUTES.REFRESH) {
    if (!token) {
      return createErrorResponse('Unauthorized', 401);
    }

    try {
      const backendUrl = buildBackendUrl('/refresh', searchParams);
      const contentType = request.headers.get('content-type') || '';
      let body: any = null;

      if (contentType.includes('application/json')) body = await request.json().catch(() => null);
      else if (contentType.includes('application/x-www-form-urlencoded')) body = await request.text();

      const backendResponse = await proxyToBackend('POST', backendUrl, token, body);

      if (backendResponse.ok) {
        const refreshData = await safeJsonParse(backendResponse);
        const newToken = refreshData.access_token || refreshData.token;

        if (newToken) {
          const response = NextResponse.json(refreshData);
          setAuthCookie(response, newToken);
          return response;
        }

        return NextResponse.json(refreshData);
      } else {
        return createErrorResponse('Token refresh failed', 401);
      }
    } catch (error) {
      console.error('[Proxy] Token refresh error:', error);
      return createErrorResponse(
        'Token refresh service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // Special handling for verify route (can be empty path or /verify)
  // Backend verify endpoint expects POST method, but frontend might call it as GET
  if (!apiPath || apiPath === '/' || apiPath === SPECIAL_ROUTES.VERIFY) {
    if (!token) {
      console.warn(`[Proxy] No auth token found for ${method} ${apiPath}`);
      return createErrorResponse('Unauthorized', 401);
    }

    // Check if we've exceeded the maximum verification attempts to prevent loops
    // Only apply the counter if the token exists (otherwise it's just a normal unauthorized request)
    // For verification endpoint specifically, allow more attempts since it's a legitimate auth check
    const isVerifyEndpoint = apiPath === '/' || apiPath === SPECIAL_ROUTES.VERIFY;
    const maxAttempts = isVerifyEndpoint ? 20 : 10; // Higher limit for verify endpoint

    if (!incrementRequestCount(apiPath, maxAttempts)) {
      console.error(`[Proxy] Blocking potential verification loop for path: ${apiPath}`);
      return createErrorResponse('Too many verification attempts', 429); // Too Many Requests
    }

    try {
      const backendUrl = buildBackendUrl('/verify', '');
      const backendResponse = await proxyToBackend(
        'POST',  // Always use POST for verify endpoint (backend expects it)
        backendUrl,
        token
      );

      if (backendResponse.ok) {
        const userData = await safeJsonParse(backendResponse);
        // Reset counter on successful verification
        const key = `${apiPath}_${new Date().toISOString().split('T')[0]}`; // Daily count key
        requestCounts.delete(key);

        // Add headers to help prevent recursive calls
        const response = NextResponse.json(userData);
        response.headers.set('X-Auth-Verified', 'true');
        response.headers.set('X-Auth-Timestamp', new Date().toISOString());

        return response;
      } else {
        // If the backend returns a 401, it means the token is invalid
        // Don't retry - just return the 401 to the client
        if (backendResponse.status === 401) {
          console.debug(`[Proxy] Token verification failed (401) for path: ${apiPath}`);

          // Add headers to indicate the failure reason
          const response = NextResponse.json(
            { error: 'Invalid or expired token', message: 'Token verification failed' },
            { status: 401 }
          );
          response.headers.set('X-Auth-Verified', 'false');
          response.headers.set('X-Auth-Failure-Reason', 'invalid-token');

          return response;
        } else {
          // For other status codes, return the appropriate error
          const errorData = await safeJsonParse(backendResponse).catch(() => null);
          const message = errorData?.error || errorData?.detail || 'Token verification failed';

          console.warn(`[Proxy] Token verification error (status: ${backendResponse.status}) for path: ${apiPath}`, message);

          return createErrorResponse(message, backendResponse.status);
        }
      }
    } catch (error) {
      console.error('[Proxy] Auth verification error:', error);

      // Don't retry on network errors - return appropriate error
      return createErrorResponse(
        'Authentication service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // Require token for other non-public routes
  if (!token) return createErrorResponse('Unauthorized', 401);

  try {
    let body: any = null;
    const contentType = request.headers.get('content-type') || '';
    if (['POST', 'PUT', 'PATCH'].includes(method)) {
      if (contentType.includes('application/json')) body = await request.json().catch(() => null);
      else if (contentType.includes('application/x-www-form-urlencoded')) body = await request.text();
    }

    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend(method, backendUrl, token, body);

    // Handle redirects manually to preserve authorization headers
    if (backendResponse.status >= 300 && backendResponse.status < 400) {
      const redirectUrl = backendResponse.headers.get('Location');
      if (redirectUrl) {
        // Follow the redirect with the same authorization token
        const redirectedResponse = await proxyToBackend(method, redirectUrl, token, body);

        // Check if the redirected response is also a redirect (avoid infinite loops)
        if (redirectedResponse.status >= 300 && redirectedResponse.status < 400) {
          const secondRedirectUrl = redirectedResponse.headers.get('Location');
          if (secondRedirectUrl && secondRedirectUrl !== redirectUrl) {
            const finalResponse = await proxyToBackend(method, secondRedirectUrl, token, body);
            if (!finalResponse.ok) {
              const errorData = await safeJsonParse(finalResponse).catch(() => null);
              const message = errorData?.error || errorData?.detail || 'API request failed';
              return createErrorResponse(message, finalResponse.status);
            }
            const data = await safeJsonParse(finalResponse);
            return NextResponse.json(data, { status: finalResponse.status });
          }
        }

        if (!redirectedResponse.ok) {
          const errorData = await safeJsonParse(redirectedResponse).catch(() => null);
          const message = errorData?.error || errorData?.detail || 'API request failed';
          return createErrorResponse(message, redirectedResponse.status);
        }
        const data = await safeJsonParse(redirectedResponse);
        return NextResponse.json(data, { status: redirectedResponse.status });
      }
    }

    if (!backendResponse.ok) {
      const errorData = await safeJsonParse(backendResponse).catch(() => null);
      const message = errorData?.error || errorData?.detail || 'API request failed';
      return createErrorResponse(message, backendResponse.status);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error(`[Proxy] ${method} ${apiPath} error:`, error);
    return createErrorResponse('API service unavailable', 503);
  }
}

/**
 * Export handlers for each method
 */
export const GET = (req: NextRequest, ctx: any) => handleRequest('GET', req, ctx);
export const POST = (req: NextRequest, ctx: any) => handleRequest('POST', req, ctx);
export const PUT = (req: NextRequest, ctx: any) => handleRequest('PUT', req, ctx);
export const PATCH = (req: NextRequest, ctx: any) => handleRequest('PATCH', req, ctx);
export const DELETE = (req: NextRequest, ctx: any) => handleRequest('DELETE', req, ctx);