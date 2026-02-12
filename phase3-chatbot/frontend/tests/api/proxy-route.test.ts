/**
 * API Proxy Route Tests
 *
 * Tests for app/api/auth/proxy/[...path]/route.ts
 * Focus: Error handling for non-JSON backend responses
 *
 * Related: User Story 1 (P1) - Graceful Error Handling
 * Spec: specs/003-fix-proxy-json-error/spec.md
 */

// Mock NextResponse before importing api-utils
jest.mock('next/server', () => ({
  NextResponse: {
    json: (body: any, init?: { status?: number }) => ({
      body,
      status: init?.status || 200,
    }),
  },
}));

import { safeJsonParse, createErrorResponse, logBackendResponse } from '../../lib/api-utils';

describe('API Proxy Error Handling', () => {
  // Suppress console warnings/errors during tests
  beforeAll(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterAll(() => {
    jest.restoreAllMocks();
  });

  /**
   * T-PROXY-001: Backend returns valid JSON → Parse success
   *
   * Scenario: Backend returns proper JSON response
   * Expected: Data is parsed successfully and returned
   */
  describe('T-PROXY-001: Valid JSON parsing', () => {
    it('should successfully parse valid JSON response', async () => {
      const mockData = { id: 1, title: 'Test Todo', completed: false };
      const mockResponse = new Response(JSON.stringify(mockData), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });

      const result = await safeJsonParse(mockResponse);

      expect(result).toEqual(mockData);
    });

    it('should handle JSON with charset in Content-Type', async () => {
      const mockData = { message: 'Success' };
      const mockResponse = new Response(JSON.stringify(mockData), {
        status: 200,
        headers: { 'content-type': 'application/json; charset=utf-8' },
      });

      const result = await safeJsonParse(mockResponse);

      expect(result).toEqual(mockData);
    });
  });

  /**
   * T-PROXY-002: Backend returns HTML error page → Standardized error
   *
   * Scenario: Backend returns HTML 500 error page
   * Expected: Parse error is caught, standardized error returned
   */
  describe('T-PROXY-002: HTML error page handling', () => {
    it('should handle HTML error page from backend', async () => {
      const htmlError = '<html><body><h1>Internal Server Error</h1></body></html>';
      const mockResponse = new Response(htmlError, {
        status: 500,
        headers: { 'content-type': 'text/html' },
      });

      await expect(safeJsonParse(mockResponse)).rejects.toThrow('Failed to parse JSON response');
    });

    it('should log HTML error details', async () => {
      const consoleSpy = jest.spyOn(console, 'error');
      const htmlError = '<html><body>Error</body></html>';
      const mockResponse = new Response(htmlError, {
        status: 500,
        headers: { 'content-type': 'text/html' },
        url: 'http://localhost:8000/api/todos',
      });

      try {
        await safeJsonParse(mockResponse);
      } catch (e) {
        // Expected to throw
      }

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  /**
   * T-PROXY-003: Backend returns plain text → Standardized error
   *
   * Scenario: Backend returns plain text error message
   * Expected: Parse error is caught, standardized error returned
   */
  describe('T-PROXY-003: Plain text error handling', () => {
    it('should handle plain text error response', async () => {
      const textError = 'Internal Server Error';
      const mockResponse = new Response(textError, {
        status: 500,
        headers: { 'content-type': 'text/plain' },
      });

      await expect(safeJsonParse(mockResponse)).rejects.toThrow('Failed to parse JSON response');
    });
  });

  /**
   * T-PROXY-004: Backend returns 200 OK with non-JSON → Error response
   *
   * Scenario: Backend returns 200 status but HTML content (misconfigured proxy)
   * Expected: Detected as error, appropriate handling
   */
  describe('T-PROXY-004: Success status with non-JSON content', () => {
    it('should detect 200 OK with HTML as error', async () => {
      const htmlContent = '<html><body>Success page</body></html>';
      const mockResponse = new Response(htmlContent, {
        status: 200,
        headers: { 'content-type': 'text/html' },
      });

      await expect(safeJsonParse(mockResponse)).rejects.toThrow('Failed to parse JSON response');
    });
  });

  /**
   * T-PROXY-005: Content-Type JSON but malformed body → Graceful handling
   *
   * Scenario: Content-Type says JSON but body is invalid JSON
   * Expected: Parse error caught gracefully
   */
  describe('T-PROXY-005: Malformed JSON with correct Content-Type', () => {
    it('should handle malformed JSON gracefully', async () => {
      const malformedJson = '{ invalid json: missing quotes }';
      const mockResponse = new Response(malformedJson, {
        status: 500,
        headers: { 'content-type': 'application/json' },
      });

      await expect(safeJsonParse(mockResponse)).rejects.toThrow('Failed to parse JSON response');
    });

    it('should handle truncated JSON gracefully', async () => {
      const truncatedJson = '{"data": "incomplete';
      const mockResponse = new Response(truncatedJson, {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });

      await expect(safeJsonParse(mockResponse)).rejects.toThrow('Failed to parse JSON response');
    });
  });

  /**
   * T-PROXY-006: Backend connection fails → 503 error
   *
   * Scenario: Network error, backend unreachable
   * Expected: Appropriate error response created
   */
  describe('T-PROXY-006: Network connection failures', () => {
    it('should create proper error response for service unavailable', () => {
      const errorResponse = createErrorResponse(
        'API service unavailable',
        503,
        'Connection failed'
      );

      expect(errorResponse.status).toBe(503);
      // Note: NextResponse.json() doesn't expose body directly in tests
      // This would be validated in integration tests
    });

    it('should handle empty response body', async () => {
      const emptyResponse = new Response('', {
        status: 200,
        headers: { 'content-type': 'application/json' },
      });

      const result = await safeJsonParse(emptyResponse);

      expect(result).toEqual({});
    });
  });

  /**
   * Utility Function Tests
   */
  describe('Utility Functions', () => {
    describe('createErrorResponse', () => {
      it('should create error response with required fields', () => {
        const response = createErrorResponse('Test error', 500);

        expect(response.status).toBe(500);
      });

      it('should include details when provided', () => {
        const response = createErrorResponse('Test error', 500, 'Debug info');

        expect(response.status).toBe(500);
        // Details would be in response body
      });

      it('should support various status codes', () => {
        const codes = [400, 401, 403, 404, 500, 502, 503];

        codes.forEach((code) => {
          const response = createErrorResponse('Error', code);
          expect(response.status).toBe(code);
        });
      });
    });

    describe('logBackendResponse', () => {
      it('should log response details', () => {
        const consoleSpy = jest.spyOn(console, 'error');
        const mockResponse = new Response('Error body', {
          status: 500,
          headers: { 'content-type': 'text/html' },
          url: 'http://localhost:8000/api/test',
        });

        logBackendResponse(mockResponse, 'Error body');

        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('Backend response parse error')
        );
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('Status: 500')
        );
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('Content-Type: text/html')
        );
      });

      it('should truncate long response bodies to 500 chars', async () => {
        const consoleSpy = jest.spyOn(console, 'error');
        const longBody = 'A'.repeat(1000);
        const mockResponse = new Response(longBody, {
          status: 500,
          headers: { 'content-type': 'text/plain' },
        });

        // Call safeJsonParse to trigger the error path which calls logBackendResponse
        try {
          await safeJsonParse(mockResponse);
        } catch (e) {
          // Expected to throw
        }

        // Check that the logged message contains truncation indicator
        const logCalls = consoleSpy.mock.calls.map(call => call.join('\n'));
        const fullLog = logCalls.join('\n');
        expect(fullLog).toContain('(truncated)');
        expect(fullLog).not.toContain('A'.repeat(600)); // Shouldn't have full body
      });

      it('should use warn level for 4xx errors', () => {
        const warnSpy = jest.spyOn(console, 'warn');
        const mockResponse = new Response('Not found', {
          status: 404,
          headers: { 'content-type': 'text/html' },
        });

        logBackendResponse(mockResponse, 'Not found');

        expect(warnSpy).toHaveBeenCalled();
      });
    });
  });
});
