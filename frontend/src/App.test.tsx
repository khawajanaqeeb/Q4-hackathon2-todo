import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock the store provider and other dependencies
jest.mock('./store', () => ({
  store: {
    subscribe: jest.fn(),
    dispatch: jest.fn(),
    getState: jest.fn(() => ({
      chat: { messages: [], isConnected: true },
      ui: { theme: 'light', notification: { isVisible: false } },
      todo: { todos: {}, filter: 'all' }
    }))
  }
}));

// Mock the components that are used in App
jest.mock('./components/layout/Layout', () => {
  return {
    default: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="layout">{children}</div>
    )
  };
});

jest.mock('./components/chat/ChatPage', () => {
  return {
    default: () => <div data-testid="chat-page">Chat Page</div>
  };
});

jest.mock('./components/shared/NotificationSystem', () => {
  return {
    default: () => <div data-testid="notification-system">Notifications</div>
  };
});

jest.mock('./components/shared/ErrorBoundary', () => {
  return {
    default: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="error-boundary">{children}</div>
    )
  };
});

describe('App Component', () => {
  test('renders without crashing', () => {
    render(<App />);

    // Check if the main app container is rendered
    const appElement = screen.getByTestId('error-boundary');
    expect(appElement).toBeInTheDocument();

    // Check if the layout is rendered
    const layoutElement = screen.getByTestId('layout');
    expect(layoutElement).toBeInTheDocument();

    // Check if the chat page is rendered
    const chatPageElement = screen.getByTestId('chat-page');
    expect(chatPageElement).toBeInTheDocument();

    // Check if the notification system is rendered
    const notificationElement = screen.getByTestId('notification-system');
    expect(notificationElement).toBeInTheDocument();
  });
});