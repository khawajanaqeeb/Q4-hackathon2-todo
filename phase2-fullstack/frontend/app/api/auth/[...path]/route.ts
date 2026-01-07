import { NextRequest, NextResponse } from 'next/server';
import { safeJsonParse, createErrorResponse } from '../../../../lib/api-utils';

/**
 * UNIFIED AUTHENTICATION PROXY - SINGLE SOURCE OF TRUTH
 *
 * This is the ONLY auth route in the application.
 * Handles all authentication and API proxying through one clean interface.
 *
 * Routes handled:
 * - POST /api/auth/login -> proxies to backend, sets cookie on success
 * - POST /api/auth/register -> proxies to backend, sets cookie on success
 * - POST /api/auth/logout -> clears cookie, returns success
 * - POST /api/auth/refresh -> proxies to backend, updates cookie on success
 * - GET /api/auth/verify -> verifies token with backend
 * - ALL /api/auth/* -> proxies to backend with auth token
 */

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL;
const COOKIE_NAME = 'auth_token';
const COOKIE_MAX_AGE = 60 * 30; // 30 minutes

// Routes that don't require authentication
const PUBLIC_ROUTES = ['/login', '/register'];

// Routes that have special handling
const SPECIAL_ROUTES = {
  LOGOUT: '/logout',
  REFRESH: '/refresh',
  VERIFY: '/verify',
};

/**
 * Extract auth token from cookies or Authorization header
 */
function getAuthToken(request: NextRequest): string | null {
  return (
    request.cookies.get(COOKIE_NAME)?.value ||
    request.headers.get('Authorization')?.replace('Bearer ', '') ||
    null
  );
}

/**
 * Set auth cookie on response
 */
function setAuthCookie(response: NextResponse, token: string): void {
  response.cookies.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: COOKIE_MAX_AGE,
    path: '/',
    sameSite: 'strict',
  });
}

/**
 * Clear auth cookie on response
 */
function clearAuthCookie(response: NextResponse): void {
  response.cookies.set(COOKIE_NAME, '', {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    maxAge: 0,
    path: '/',
    sameSite: 'strict',
  });
}

/**
 * Check if route requires authentication
 */
function isPublicRoute(path: string): boolean {
  return PUBLIC_ROUTES.some(route => path === route || path.startsWith(route));
}

/**
 * Build backend URL from path and query params
 * Prepends /auth only for auth-specific routes (login, register, refresh, verify, logout)
 * Other routes (like /todos) go directly to their backend endpoints
 */
function buildBackendUrl(path: string, searchParams: string): string {
  // Auth-specific routes need /auth prefix
  const authRoutes = ['/login', '/register', '/refresh', '/verify', '/logout'];
  const isAuthRoute = authRoutes.some(route => path === route || path.startsWith(route + '/'));

  if (isAuthRoute) {
    return `${BACKEND_URL}/auth${path}${searchParams}`;
  }

  // All other routes (todos, etc.) go directly
  return `${BACKEND_URL}${path}${searchParams}`;
}

/**
 * Proxy request to backend
 */
async function proxyToBackend(
  method: string,
  url: string,
  token: string | null,
  body?: any
): Promise<Response> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options: RequestInit = {
    method,
    headers,
  };

  if (body && method !== 'GET' && method !== 'DELETE') {
    options.body = JSON.stringify(body);
  }

  return fetch(url, options);
}

/**
 * Handle GET requests
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // Special handling for verify route (can be empty path or /verify)
  if (!apiPath || apiPath === '/' || apiPath === SPECIAL_ROUTES.VERIFY) {
    const token = getAuthToken(request);
    if (!token) {
      return createErrorResponse('Unauthorized', 401);
    }

    try {
      const response = await proxyToBackend(
        'POST',
        buildBackendUrl('/verify', ''),
        token
      );

      if (response.ok) {
        const userData = await safeJsonParse(response);
        return NextResponse.json(userData);
      } else {
        return createErrorResponse('Invalid token', 401);
      }
    } catch (error) {
      console.error('Auth verification error:', error);
      return createErrorResponse(
        'Authentication service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // All other GET requests require authentication
  const token = getAuthToken(request);
  if (!token) {
    return createErrorResponse('Unauthorized', 401);
  }

  try {
    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend('GET', backendUrl, token);

    if (!backendResponse.ok) {
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}

/**
 * Handle POST requests
 */
export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // Special handling for logout
  if (apiPath === SPECIAL_ROUTES.LOGOUT) {
    const response = NextResponse.json({ message: 'Logged out successfully' });
    clearAuthCookie(response);
    return response;
  }

  // Get request body and content type
  const contentType = request.headers.get('content-type') || '';
  let body: any = null;

  // Handle different content types
  if (contentType.includes('application/x-www-form-urlencoded')) {
    // For form data, read as text to preserve format
    body = await request.text();
  } else if (contentType.includes('application/json')) {
    // For JSON, parse as JSON
    body = await request.json().catch(() => null);
  }

  // Special handling for login and register - proxy to backend and set cookie on success
  if (apiPath === '/login' || apiPath === '/register') {
    try {
      const backendUrl = buildBackendUrl(apiPath, searchParams);

      // For login (form data), send directly with form content type
      if (apiPath === '/login') {
        const backendResponse = await fetch(backendUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: body,
        });

        if (!backendResponse.ok) {
          let errorMessage = 'Authentication failed';
          let errorDetails: string | undefined;
          try {
            const errorData = await safeJsonParse(backendResponse);
            errorMessage = errorData.error || errorData.detail || errorMessage;
            errorDetails = errorData.details;
          } catch {
            errorMessage = backendResponse.statusText || errorMessage;
          }
          return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
        }

        const data = await safeJsonParse(backendResponse);

        // Extract token from response and set cookie
        const token = data.access_token || data.token;
        if (token) {
          const response = NextResponse.json(data, { status: backendResponse.status });
          setAuthCookie(response, token);
          return response;
        } else {
          return NextResponse.json(data, { status: backendResponse.status });
        }
      }

      // For register (JSON), use the proxy function
      const backendResponse = await proxyToBackend('POST', backendUrl, null, body);

      if (!backendResponse.ok) {
        let errorMessage = 'Authentication failed';
        let errorDetails: string | undefined;
        try {
          const errorData = await safeJsonParse(backendResponse);
          errorMessage = errorData.error || errorData.detail || errorMessage;
          errorDetails = errorData.details;
        } catch {
          errorMessage = backendResponse.statusText || errorMessage;
        }
        return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
      }

      const data = await safeJsonParse(backendResponse);

      // Extract token from response and set cookie
      const token = data.access_token || data.token;
      if (token) {
        const response = NextResponse.json(data, { status: backendResponse.status });
        setAuthCookie(response, token);
        return response;
      } else {
        // Return data even if no token (shouldn't happen but handle gracefully)
        return NextResponse.json(data, { status: backendResponse.status });
      }
    } catch (error) {
      console.error('Auth proxy error:', error);
      return createErrorResponse(
        'Authentication service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // Special handling for refresh - proxy to backend and update cookie on success
  if (apiPath === SPECIAL_ROUTES.REFRESH) {
    const token = getAuthToken(request);
    if (!token) {
      return createErrorResponse('Unauthorized', 401);
    }

    try {
      const backendUrl = buildBackendUrl(apiPath, searchParams);
      const backendResponse = await proxyToBackend('POST', backendUrl, token, body);

      if (!backendResponse.ok) {
        let errorMessage = 'Token refresh failed';
        let errorDetails: string | undefined;
        try {
          const errorData = await safeJsonParse(backendResponse);
          errorMessage = errorData.error || errorData.detail || errorMessage;
          errorDetails = errorData.details;
        } catch {
          errorMessage = backendResponse.statusText || errorMessage;
        }
        return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
      }

      const data = await safeJsonParse(backendResponse);

      // Update cookie with new token
      const newToken = data.access_token || data.token;
      const response = NextResponse.json(data, { status: backendResponse.status });
      if (newToken) {
        setAuthCookie(response, newToken);
      }
      return response;
    } catch (error) {
      console.error('Token refresh error:', error);
      return createErrorResponse(
        'Authentication service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  // All other POST requests require authentication
  const token = getAuthToken(request);
  if (!token) {
    return createErrorResponse('Unauthorized', 401);
  }

  try {
    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend('POST', backendUrl, token, body);

    if (!backendResponse.ok) {
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}

/**
 * Handle PUT requests
 */
export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  const token = getAuthToken(request);
  if (!token) {
    return createErrorResponse('Unauthorized', 401);
  }

  try {
    const body = await request.json().catch(() => null);
    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend('PUT', backendUrl, token, body);

    if (!backendResponse.ok) {
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}

/**
 * Handle DELETE requests
 */
export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  const token = getAuthToken(request);
  if (!token) {
    return createErrorResponse('Unauthorized', 401);
  }

  try {
    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend('DELETE', backendUrl, token);

    if (!backendResponse.ok) {
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}

/**
 * Handle PATCH requests
 */
export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  const token = getAuthToken(request);
  if (!token) {
    return createErrorResponse('Unauthorized', 401);
  }

  try {
    const body = await request.json().catch(() => null);
    const backendUrl = buildBackendUrl(apiPath, searchParams);
    const backendResponse = await proxyToBackend('PATCH', backendUrl, token, body);

    if (!backendResponse.ok) {
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    const data = await safeJsonParse(backendResponse);
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error('API proxy error:', error);
    return createErrorResponse(
      'API service unavailable',
      503,
      error instanceof Error ? error.message : 'Unknown error'
    );
  }
}
