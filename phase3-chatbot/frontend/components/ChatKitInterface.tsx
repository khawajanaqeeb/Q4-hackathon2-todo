'use client';

import React, { useState, useEffect } from 'react';
import { useChat } from 'openai-chatkit';

interface ChatKitInterfaceProps {
  userId: string;
}

const ChatKitInterface: React.FC<ChatKitInterfaceProps> = ({ userId }) => {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error
  } = useChat({
    api: `/api/auth/chat/${userId}`,
    body: {
      userId: userId
    },
    headers: {
      'Content-Type': 'application/json',
      'credentials': 'include'
    },
    onError: (error) => {
      console.error('Chat error:', error);
    }
  });

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto border rounded-lg shadow-sm bg-gray-800 text-white">
      {/* Chat Header */}
      <div className="bg-gray-900 px-4 py-3 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">AI Todo Assistant</h2>
        <p className="text-sm text-gray-400">Manage your tasks with natural language</p>
      </div>

      {/* Messages Container - Using ChatKit's message rendering */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[400px] bg-gray-900">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-white'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-200' : 'text-gray-300'}`}>
                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-white rounded-lg px-4 py-2 max-w-[80%]">
              <div className="flex items-center">
                <span>Thinking</span>
                <span className="ml-1 dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 text-red-300 p-3 border-t border-red-700">
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error.toString()}
            </div>
          </div>
        )}
      </div>

      {/* Input Form - Using ChatKit's form handling */}
      <form onSubmit={handleSubmit} className="border-t p-4 bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white bg-gray-700 placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white rounded-lg px-4 py-2 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2">
          Examples: "Add a task to buy groceries", "Show me my tasks", "Mark task 1 as complete"
        </p>
      </form>
    </div>
  );
};

export default ChatKitInterface;