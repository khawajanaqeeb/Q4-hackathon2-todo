import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import TypingIndicator from './TypingIndicator';

const ChatContainer: React.FC = () => {
  const { theme } = useSelector((state: RootState) => state.ui);
  const { isConnected } = useSelector((state: RootState) => state.chat);

  return (
    <div
      className={`flex flex-col h-full ${
        theme === 'dark' ? 'bg-gray-800' : 'bg-white'
      }`}
      role="main"
      aria-label="Chat interface"
    >
      {/* Chat Header */}
      <div
        className={`p-4 border-b ${
          theme === 'dark'
            ? 'border-gray-700 bg-gray-900'
            : 'border-gray-200 bg-gray-50'
        }`}
      >
        <h2 className="text-lg font-semibold">Chat Assistant</h2>
        <div className="flex items-center mt-1">
          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            isConnected
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            <span className={`mr-1.5 h-2 w-2 rounded-full ${
              isConnected ? 'bg-green-400' : 'bg-yellow-400'
            }`} />
            {isConnected ? 'Online' : 'Connecting...'}
          </span>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList />
      </div>

      {/* Typing Indicator */}
      <div className="px-4 py-2">
        <TypingIndicator />
      </div>

      {/* Message Input */}
      <div className="border-t p-4">
        <MessageInput />
      </div>
    </div>
  );
};

export default ChatContainer;