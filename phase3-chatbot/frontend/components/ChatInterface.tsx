import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  userId: string;
}

// Define the response type from the backend API
interface ChatApiResponse {
  message: string;
  conversation_id: string;
  timestamp: string;
  action_taken: string;
  confirmation_message: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ userId }) => {
  const { user } = useAuth();
  const [inputValue, setInputValue] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Helper function to safely parse dates from backend
  const parseSafeDate = (dateString: string): Date => {
    try {
      // First try to parse as ISO string
      const parsedDate = new Date(dateString);
      // Check if the date is valid
      if (isNaN(parsedDate.getTime())) {
        // If invalid, fall back to current time
        return new Date();
      }
      return parsedDate;
    } catch (error) {
      // If any error occurs, fall back to current time
      return new Date();
    }
  };

  // Function to send message to backend API
  const sendMessageToBackend = async (message: string): Promise<ChatApiResponse> => {
    try {
      // Using the unified auth proxy for chat API
      const response = await fetch(`/api/chat/${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(user?.token && { Authorization: `Bearer ${user.token}` })
        },
        body: JSON.stringify({
          message: message,
          conversation_id: currentConversationId
        }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
        console.error('API Error:', response.status, errorData);
        throw new Error(`API Error: ${response.status}, ${JSON.stringify(errorData)}`);
      }

      const data: ChatApiResponse = await response.json();

      // Update the current conversation ID if a new one was created
      if (data.conversation_id && !currentConversationId) {
        setCurrentConversationId(data.conversation_id);
      }

      return data;
    } catch (error) {
      console.error('Error sending message to backend:', error);
      throw error;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Send message to backend and get response
      const response = await sendMessageToBackend(inputValue);

      // Add AI response
      const aiMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.confirmation_message || response.message,
        timestamp: parseSafeDate(response.timestamp),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto border rounded-lg shadow-sm bg-gray-800 text-white">
      {/* Chat Header */}
      <div className="bg-gray-900 px-4 py-3 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white">AI Todo Assistant</h2>
        <p className="text-sm text-gray-400">Manage your tasks with natural language</p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[400px] bg-gray-900">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-400">
            <div className="mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <p>Start a conversation by typing a message below.</p>
            <p className="mt-1">Try: "Add a task to buy groceries" or "Show me my tasks"</p>
          </div>
        ) : (
          messages.map((message) => (
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
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))
        )}

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

        <div ref={messagesEndRef} />
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/30 text-red-300 p-3 border-t border-red-700">
          <div className="flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="border-t p-4 bg-gray-800">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your message here..."
            className="flex-1 border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-white bg-gray-700 placeholder-gray-400"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
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

export default ChatInterface;