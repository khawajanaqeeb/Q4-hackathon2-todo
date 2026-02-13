import { NextResponse } from 'next/server';

/**
 * Error response structure for API proxy
 * Maintains backward compatibility with existing frontend code
 */
export interface ApiError {
  error: string;      // User-facing error message (required)
  details?: string;   // Optional technical details for debugging
}

/**
 * Safely parse JSON from a Response object with error handling
 *
 * Implements two-tier validation:
 * 1. Check Content-Type header (warn if not JSON)
 * 2. Wrap .json() call in try-catch (handle malformed JSON)
 *
 * @param response - The fetch Response object from backend
 * @returns Parsed JSON data or throws error with details
 * @throws Error with descriptive message if parsing fails
 *
 * Related tasks: T005, FR-001, FR-003 from spec.md
 */
export async function safeJsonParse(response: Response): Promise<any> {
  // Get Content-Type header for validation
  const contentType = response.headers.get('content-type') || '';
  const isJsonContentType = contentType.includes('application/json') || contentType.includes('text/json');

  // Get response body as text first (allows logging on parse failure)
  const responseText = await response.text();

  // Log warning if Content-Type suggests non-JSON content
  if (!isJsonContentType && responseText.length > 0) {
    console.warn(
      `[API Proxy] Non-JSON Content-Type detected: ${contentType}`,
      `Status: ${response.status}`,
      `Body preview: ${responseText.substring(0, 500)}`
    );
  }

  // Attempt JSON parsing with error handling
  try {
    // If response is empty, return empty object
    if (!responseText || responseText.trim() === '') {
      return {};
    }

    return JSON.parse(responseText);
  } catch (parseError) {
    // Log the parsing error with context
    logBackendResponse(response, responseText);

    // Throw descriptive error for caller to handle
    throw new Error(
      `Failed to parse JSON response: ${parseError instanceof Error ? parseError.message : 'Unknown parse error'}`
    );
  }
}

/**
 * Create a standardized error response for the API proxy
 *
 * Returns NextResponse with consistent JSON error format:
 * { error: "user-facing message", details: "optional technical info" }
 *
 * @param message - User-friendly error message
 * @param statusCode - HTTP status code to return
 * @param details - Optional technical details for debugging
 * @returns NextResponse with standardized error format
 *
 * Related tasks: T006, FR-002, FR-007 from spec.md
 */
export function createErrorResponse(
  message: string,
  statusCode: number,
  details?: string
): NextResponse {
  const errorBody: ApiError = {
    error: message,
  };

  // Add details field only if provided (backward compatible)
  if (details) {
    errorBody.details = details;
  }

  return NextResponse.json(errorBody, { status: statusCode });
}

/**
 * Log backend response details for debugging
 *
 * Logs:
 * - HTTP status code
 * - Content-Type header
 * - First 500 characters of response body
 * - Request URL (if available)
 *
 * Uses console.error() for 5xx errors, console.warn() for 4xx errors
 *
 * @param response - The fetch Response object from backend
 * @param bodyPreview - Preview of response body (pre-truncated if needed)
 *
 * Related tasks: T007, FR-006, FR-008 from spec.md
 */
export function logBackendResponse(
  response: Response,
  bodyPreview: string
): void {
  const status = response.status;
  const contentType = response.headers.get('content-type') || 'unknown';
  const url = response.url || 'unknown';

  // Truncate body to 500 characters to prevent log overflow
  const truncatedBody = bodyPreview.substring(0, 500);
  const wasTruncated = bodyPreview.length > 500;

  const logMessage = [
    `[API Proxy] Backend response parse error:`,
    `  URL: ${url}`,
    `  Status: ${status}`,
    `  Content-Type: ${contentType}`,
    `  Body preview: ${truncatedBody}${wasTruncated ? '... (truncated)' : ''}`,
  ].join('\n');

  // Use error level for 5xx, warn level for 4xx and other errors
  if (status >= 500) {
    console.error(logMessage);
  } else {
    console.warn(logMessage);
  }
}
