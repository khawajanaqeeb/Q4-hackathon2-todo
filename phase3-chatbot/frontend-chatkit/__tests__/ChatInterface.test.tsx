// __tests__/ChatInterface.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ChatInterface from '../components/ChatInterface';

describe('ChatInterface Component', () => {
  const mockProps = {
    backendUrl: 'http://localhost:8000',
    userIdentifier: '1',
    tokenProvider: jest.fn().mockResolvedValue('mock-token'),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders chat interface with input and message area', () => {
    render(<ChatInterface {...mockProps} />);

    // Check if the main chat container is rendered
    const chatContainer = screen.getByTestId('chat-container');
    expect(chatContainer).toBeInTheDocument();

    // Check if input area is present
    const inputArea = screen.getByPlaceholderText('Type your message here...');
    expect(inputArea).toBeInTheDocument();

    // Check if send button is present
    const sendButton = screen.getByText('Send');
    expect(sendButton).toBeInTheDocument();
  });

  test('allows user to type and send a message', async () => {
    render(<ChatInterface {...mockProps} />);

    const inputBox = screen.getByPlaceholderText('Type your message here...');
    const sendButton = screen.getByText('Send');

    // Type a message
    fireEvent.change(inputBox, { target: { value: 'Test message' } });

    // Click send button
    fireEvent.click(sendButton);

    // Wait for the message to be processed
    await waitFor(() => {
      expect(inputBox).toHaveValue('');
    });
  });

  test('displays welcome message when no messages exist', () => {
    render(<ChatInterface {...mockProps} />);

    const welcomeMessage = screen.getByText('Start chatting with the AI assistant to manage your todos!');
    expect(welcomeMessage).toBeInTheDocument();
  });

  test('shows user ID in debug display', () => {
    render(<ChatInterface {...mockProps} />);

    const debugDisplay = screen.getByText(/Debug: User ID - 1/);
    expect(debugDisplay).toBeInTheDocument();
  });
});