// jest.setup.js
import '@testing-library/jest-dom';

// Mock ResizeObserver if not available
global.ResizeObserver = global.ResizeObserver || jest.fn().mockImplementation(() => ({
  disconnect: jest.fn(),
  observe: jest.fn(),
  unobserve: jest.fn(),
}));

// Mock Intersection Observer
global.IntersectionObserver = global.IntersectionObserver || jest.fn().mockImplementation(() => ({
  disconnect: jest.fn(),
  observe: jest.fn(),
  unobserve: jest.fn(),
}));