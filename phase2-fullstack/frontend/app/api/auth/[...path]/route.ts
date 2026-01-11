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
const SPECIAL_ROUTES = {
  LOGOUT: '/logout',
  REFRESH: '/refresh',
  VERIFY: '/verify',
};

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
  const authRoutes = ['/login', '/register', '/refresh', '/verify', '/logout'];
  const isAuthRoute = authRoutes.some(route => path === route || path.startsWith(route + '/'));
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

  // Special handling for verify route (can be empty path or /verify)
  // Backend verify endpoint expects POST method, but frontend might call it as GET
  if (!apiPath || apiPath === '/' || apiPath === SPECIAL_ROUTES.VERIFY) {
    if (!token) {
      return createErrorResponse('Unauthorized', 401);
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
        return NextResponse.json(userData);
      } else {
        return createErrorResponse('Invalid token', 401);
      }
    } catch (error) {
      console.error('[Proxy] Auth verification error:', error);
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