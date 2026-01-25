import React, { useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { setScrollPosition } from '@/store/slices/uiSlice';
import MessageBubble from './MessageBubble';

const MessageList: React.FC = () => {
  const { messages } = useSelector((state: RootState) => state.chat);
  const { scrollPosition } = useSelector((state: RootState) => state.ui);
  const dispatch = useDispatch();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle scroll position changes
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.target as HTMLDivElement;
    dispatch(setScrollPosition(element.scrollTop));
  };

  return (
    <div
      className="overflow-y-auto max-h-[calc(100vh-200px)]"
      onScroll={handleScroll}
      role="log"
      aria-live="polite"
      aria-label="Chat messages"
    >
      <div className="space-y-4">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;