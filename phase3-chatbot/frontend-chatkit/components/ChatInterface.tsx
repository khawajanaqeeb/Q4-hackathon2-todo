// components/ChatInterface.tsx
import React, { useState, useEffect } from 'react';

interface ChatInterfaceProps {
  backendUrl: string;
  userIdentifier: string;
  tokenProvider: () => Promise<string>;
  onMessage?: (message: any) => void;
  onError?: (error: any) => void;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status: 'sent' | 'delivered' | 'error';
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  backendUrl,
  userIdentifier,
  tokenProvider,
  onMessage,
  onError
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string>('');

  // Initialize with user identifier
  useEffect(() => {
    setUserId(userIdentifier);
  }, [userIdentifier]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
      status: 'sent'
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get token for authentication
      const token = await tokenProvider();

      // Send message to backend
      const response = await fetch(`${backendUrl}/api/${userIdentifier}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: inputValue
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add AI response to messages
      const aiMessage: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp),
        status: 'delivered'
      };

      setMessages(prev => [...prev, aiMessage]);

      // Call onMessage callback if provided
      if (onMessage) {
        onMessage(aiMessage);
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message to UI
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
        status: 'error'
      };

      setMessages(prev => [...prev, errorMessage]);

      // Call onError callback if provided
      if (onError) {
        onError(error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-white rounded-lg shadow-md overflow-hidden">
      {/* Debug user ID display */}
      <div className="bg-gray-100 p-2 text-sm text-gray-600 border-b">
        Debug: User ID - {userId}
      </div>

      {/* Chat messages container */}
      <div
        id="chat-container"
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 min-h-[400px]"
      >
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 italic">
            Start chatting with the AI assistant to manage your todos!
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                } ${
                  message.status === 'error' ? 'bg-red-200 text-red-800' : ''
                }`}
              >
                <div className="text-sm">{message.content}</div>
                <div className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-800 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
              <div className="text-sm">AI is thinking...</div>
            </div>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="border-t p-4 bg-white">
        <div className="flex items-center space-x-2">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-300 rounded-lg p-2 min-h-[60px] resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputValue.trim()}
            className={`px-4 py-2 rounded-lg text-white ${
              isLoading || !inputValue.trim()
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;