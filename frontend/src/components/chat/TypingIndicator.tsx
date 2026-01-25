import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

const TypingIndicator: React.FC = () => {
  const { isTypingIndicatorVisible } = useSelector((state: RootState) => state.ui);

  if (!isTypingIndicatorVisible) {
    return null;
  }

  return (
    <div
      className="flex items-center space-x-2 mb-2"
      role="status"
      aria-live="polite"
      aria-label="AI is typing"
    >
      <div className="bg-indigo-500 text-white p-2 rounded-full">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
      </div>
      <div className="flex items-center space-x-1">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
        </div>
        <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">AI is typing...</span>
      </div>
    </div>
  );
};

export default TypingIndicator;