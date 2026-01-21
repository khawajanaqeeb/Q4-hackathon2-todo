// app/chat/page.tsx
'use client';

import React, { useState, useEffect } from 'react';
import useAuth from '../../hooks/useAuth';
import ChatInterface from '../../components/ChatInterface';

const ChatPage = () => {
  const { isLoggedIn, user, token, isLoading, requireAuth } = useAuth();
  const [backendUrl, setBackendUrl] = useState('');

  useEffect(() => {
    // Verify authentication on page load
    if (!isLoading && !isLoggedIn) {
      requireAuth('/chat');
    }

    // Set backend URL from environment
    setBackendUrl(process.env.NEXT_PUBLIC_CHAT_ENDPOINT_BASE_URL || 'http://localhost:8000');
  }, [isLoggedIn, isLoading, requireAuth]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-xl">Checking authentication...</div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-xl">Redirecting to login...</div>
      </div>
    );
  }

  // Function to provide token to ChatInterface
  const getToken = async (): Promise<string> => {
    return token || '';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">Todo AI Assistant</h1>
        <p className="text-center text-gray-600 mb-8">
          Chat with your AI assistant to manage your todos naturally
        </p>

        {user && (
          <ChatInterface
            backendUrl={backendUrl}
            userIdentifier={user.id.toString()}
            tokenProvider={getToken}
            onMessage={(message) => {
              console.log('New message:', message);
            }}
            onError={(error) => {
              console.error('Chat error:', error);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default ChatPage;