// Learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom'

// Polyfill for Response and Request (needed for Next.js server components in tests)
import { TextEncoder, TextDecoder } from 'util'
global.TextEncoder = TextEncoder
global.TextDecoder = TextDecoder

// Mock Response if not available
if (typeof global.Response === 'undefined') {
  global.Response = class Response {
    constructor(body, init = {}) {
      this.body = body
      this.status = init.status || 200
      this.statusText = init.statusText || ''
      this.headers = new Map(Object.entries(init.headers || {}))
      this.ok = this.status >= 200 && this.status < 300
      this.url = init.url || ''
    }

    async text() {
      return typeof this.body === 'string' ? this.body : JSON.stringify(this.body)
    }

    async json() {
      const text = await this.text()
      return JSON.parse(text)
    }
  }
}

// Mock Headers if not available
if (typeof global.Headers === 'undefined') {
  global.Headers = class Headers extends Map {
    get(name) {
      return super.get(name.toLowerCase())
    }

    set(name, value) {
      return super.set(name.toLowerCase(), value)
    }

    has(name) {
      return super.has(name.toLowerCase())
    }
  }
}

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
      pathname: '/',
      query: {},
      asPath: '/',
    }
  },
  usePathname() {
    return '/'
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock window.localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}
global.localStorage = localStorageMock

// Mock fetch globally
global.fetch = jest.fn()
