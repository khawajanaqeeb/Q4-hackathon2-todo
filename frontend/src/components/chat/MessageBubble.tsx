import React from 'react';
import { Message } from '@/types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === 'user';
  const statusIcon = getStatusIcon(message.status);

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      aria-live={isUser ? 'off' : 'polite'} // Only announce AI messages
      role="article"
      aria-roledescription="chat message"
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
          isUser
            ? 'bg-indigo-600 text-white rounded-tr-none'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-tl-none'
        }`}
      >
        <div className="flex items-start space-x-2">
          {!isUser && (
            <div className="flex-shrink-0 pt-1">
              <div className="bg-indigo-500 text-white p-1 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
            </div>
          )}

          <div className="flex-1">
            <div className="text-sm whitespace-pre-wrap break-words">
              {message.content}
            </div>

            <div className={`flex items-center mt-1 text-xs ${
              isUser ? 'text-indigo-200' : 'text-gray-500 dark:text-gray-400'
            }`}>
              <span>{formatTime(message.timestamp)}</span>

              {isUser && (
                <span className="ml-2 flex items-center">
                  {statusIcon}
                </span>
              )}
            </div>
          </div>

          {isUser && (
            <div className="flex-shrink-0 pt-1">
              <div className="bg-indigo-800 text-white p-1 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Helper function to get status icon
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'sent':
      return (
        <span title="Sent">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </span>
      );
    case 'delivered':
      return (
        <span title="Delivered">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </span>
      );
    case 'read':
      return (
        <span title="Read">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-blue-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </span>
      );
    case 'failed':
      return (
        <span title="Failed">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </span>
      );
    default:
      return null;
  }
};

// Helper function to format time
const formatTime = (date: Date): string => {
  const time = new Date(date);
  return time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

export default MessageBubble;