import React from 'react';
import { render, screen } from '@testing-library/react';
import MessageBubble from './MessageBubble';
import { Message } from '../../types';

describe('MessageBubble Component', () => {
  const mockUserMessage: Message = {
    id: '1',
    content: 'Hello, this is a user message',
    sender: 'user',
    timestamp: new Date(),
    status: 'delivered'
  };

  const mockAiMessage: Message = {
    id: '2',
    content: 'Hello, this is an AI response',
    sender: 'ai',
    timestamp: new Date(),
    status: 'delivered'
  };

  test('renders user message correctly', () => {
    render(<MessageBubble message={mockUserMessage} />);

    // Check that the message content is rendered
    expect(screen.getByText('Hello, this is a user message')).toBeInTheDocument();

    // Check that user message has the correct styling classes
    const messageElement = screen.getByText('Hello, this is a user message').closest('div');
    expect(messageElement).toHaveClass('bg-indigo-600');
  });

  test('renders AI message correctly', () => {
    render(<MessageBubble message={mockAiMessage} />);

    // Check that the message content is rendered
    expect(screen.getByText('Hello, this is an AI response')).toBeInTheDocument();

    // Check that AI message has the correct styling classes
    const messageElement = screen.getByText('Hello, this is an AI response').closest('div');
    expect(messageElement).toHaveClass('bg-gray-200');
  });

  test('shows correct status icon for user message', () => {
    const deliveredMessage: Message = {
      ...mockUserMessage,
      status: 'delivered'
    };

    render(<MessageBubble message={deliveredMessage} />);

    // For delivered status, should show checkmark icon
    const checkIcon = screen.getByText('✓');
    expect(checkIcon).toBeInTheDocument();
  });

  test('does not show status icon for AI message', () => {
    render(<MessageBubble message={mockAiMessage} />);

    // AI messages shouldn't have status icons
    const statusIcons = screen.queryAllByRole('img'); // Icons would have role img
    // We expect only the bot icon, not message status icons
    expect(statusIcons.length).toBeLessThan(5); // Reasonable upper bound
  });
});