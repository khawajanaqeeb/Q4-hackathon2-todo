import { NextRequest, NextResponse } from 'next/server';
import { safeJsonParse, createErrorResponse } from '../../../../../lib/api-utils';

/**
 * Proxy route for authentication and API requests - replaces deprecated middleware.ts
 * Handles authentication checks and forwards API requests to the backend
 *
 * Modified: 2026-01-04 - Added safe JSON parsing to handle non-JSON backend responses
 * Related: Task T017, User Story 1 (P1), spec 003-fix-proxy-json-error
 */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // If this is an auth verification request (empty path)
  if (!apiPath || apiPath === '/') {
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
  } else {
    // This is an API request that needs to be forwarded to the backend
    // Extract token from cookies or authorization header
    const token = request.cookies.get('auth_token')?.value ||
                  request.headers.get('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
      // Forward the request to the backend with query params
      const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}${apiPath}${searchParams}`;
      const backendResponse = await fetch(backendUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      // Check if backend returned an error status
      if (!backendResponse.ok) {
        // Try to get error details from backend response
        let errorMessage = 'API request failed';
        let errorDetails: string | undefined;
        try {
          const errorData = await safeJsonParse(backendResponse);
          errorMessage = errorData.error || errorData.detail || errorMessage;
          errorDetails = errorData.details;
        } catch {
          // If we can't parse the error response, use status text
          errorMessage = backendResponse.statusText || errorMessage;
        }
        return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
      }

      // Use safe JSON parsing to handle non-JSON backend responses
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
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // If this is an auth verification request (empty path)
  if (!apiPath || apiPath === '/') {
    // Handle authentication verification
    const body = await request.json();
    const token = request.cookies.get('auth_token')?.value ||
                  request.headers.get('Authorization')?.replace('Bearer ', '');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify(body),
      });

      const data = await safeJsonParse(response);
      return NextResponse.json(data, { status: response.status });
    } catch (error) {
      console.error('Auth proxy error:', error);
      return createErrorResponse(
        'Authentication service unavailable',
        503,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  } else {
    // This is an API request that needs to be forwarded to the backend
    // Extract token from cookies or authorization header
    const token = request.cookies.get('auth_token')?.value ||
                  request.headers.get('Authorization')?.replace('Bearer ', '');

    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    try {
      // Get the request body
      const body = await request.json().catch(() => null);

      // Forward the request to the backend with query params
      const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}${apiPath}${searchParams}`;
      const backendResponse = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        ...(body && { body: JSON.stringify(body) }),
      });

      // Check if backend returned an error status
      if (!backendResponse.ok) {
        // Try to get error details from backend response
        let errorMessage = 'API request failed';
        let errorDetails: string | undefined;
        try {
          const errorData = await safeJsonParse(backendResponse);
          errorMessage = errorData.error || errorData.detail || errorMessage;
          errorDetails = errorData.details;
        } catch {
          // If we can't parse the error response, use status text
          errorMessage = backendResponse.statusText || errorMessage;
        }
        return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
      }

      // Use safe JSON parsing to handle non-JSON backend responses
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
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // Extract token from cookies or authorization header
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Get the request body
    const body = await request.json().catch(() => null);

    // Forward the request to the backend with query params
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}${apiPath}${searchParams}`;
    const backendResponse = await fetch(backendUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      ...(body && { body: JSON.stringify(body) }),
    });

    // Check if backend returned an error status
    if (!backendResponse.ok) {
      // Try to get error details from backend response
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        // If we can't parse the error response, use status text
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    // Use safe JSON parsing to handle non-JSON backend responses
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

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // Extract token from cookies or authorization header
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Forward the request to the backend with query params
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}${apiPath}${searchParams}`;
    const backendResponse = await fetch(backendUrl, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
    });

    // Check if backend returned an error status
    if (!backendResponse.ok) {
      // Try to get error details from backend response
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        // If we can't parse the error response, use status text
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    // Use safe JSON parsing to handle non-JSON backend responses
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

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  const params = await context.params;
  const apiPath = params.path ? `/${params.path.join('/')}` : '';
  const url = new URL(request.url);
  const searchParams = url.search;

  // Extract token from cookies or authorization header
  const token = request.cookies.get('auth_token')?.value ||
                request.headers.get('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // Get the request body
    const body = await request.json().catch(() => null);

    // Forward the request to the backend with query params
    const backendUrl = `${process.env.NEXT_PUBLIC_API_URL}${apiPath}${searchParams}`;
    const backendResponse = await fetch(backendUrl, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      ...(body && { body: JSON.stringify(body) }),
    });

    // Check if backend returned an error status
    if (!backendResponse.ok) {
      // Try to get error details from backend response
      let errorMessage = 'API request failed';
      let errorDetails: string | undefined;
      try {
        const errorData = await safeJsonParse(backendResponse);
        errorMessage = errorData.error || errorData.detail || errorMessage;
        errorDetails = errorData.details;
      } catch {
        // If we can't parse the error response, use status text
        errorMessage = backendResponse.statusText || errorMessage;
      }
      return createErrorResponse(errorMessage, backendResponse.status, errorDetails);
    }

    // Use safe JSON parsing to handle non-JSON backend responses
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