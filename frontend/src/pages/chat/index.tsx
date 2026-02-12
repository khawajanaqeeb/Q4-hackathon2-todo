// frontend/src/pages/chat/index.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ChatInterface from '../../components/chat/ChatInterface';
import ChatKitInterface from '../../components/chat/ChatKitInterface';
import Sidebar from '../../components/shared/Sidebar';
import { useNavigate } from 'react-router-dom';
import { FiMessageSquare, FiPlus, FiTrash2, FiArchive } from 'react-icons/fi';

interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

const ChatPage: React.FC = () => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [newConversationTitle, setNewConversationTitle] = useState('');

  // Load conversations when user is available
  useEffect(() => {
    if (!loading && !user) {
      // Redirect to login if not authenticated
      navigate('/login');
      return;
    }

    if (user) {
      loadConversations();
    }
  }, [user, loading, navigate]);

  const loadConversations = async () => {
    try {
      // In a real implementation, this would call the API to get user's conversations
      // For now, we'll simulate with mock data
      const mockConversations: Conversation[] = [
        {
          id: 'conv-1',
          title: 'Todo Management Discussion',
          createdAt: '2026-01-15T10:30:00Z',
          updatedAt: '2026-01-15T11:45:00Z',
          messageCount: 12
        },
        {
          id: 'conv-2',
          title: 'Shopping List Updates',
          createdAt: '2026-01-14T14:20:00Z',
          updatedAt: '2026-01-14T16:10:00Z',
          messageCount: 8
        },
        {
          id: 'conv-3',
          title: 'Work Tasks Review',
          createdAt: '2026-01-13T09:15:00Z',
          updatedAt: '2026-01-13T10:30:00Z',
          messageCount: 5
        }
      ];
      setConversations(mockConversations);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const handleCreateNewConversation = async () => {
    if (!newConversationTitle.trim()) return;

    try {
      // In a real implementation, this would call the API to create a new conversation
      // For now, we'll simulate the creation
      const newConversation: Conversation = {
        id: `conv-${Date.now()}`,
        title: newConversationTitle,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 0
      };

      setConversations(prev => [newConversation, ...prev]);
      setSelectedConversation(newConversation.id);
      setNewConversationTitle('');
      setSidebarOpen(false); // Close sidebar on new conversation
    } catch (error) {
      console.error('Error creating conversation:', error);
    }
  };

  const handleSelectConversation = (id: string) => {
    setSelectedConversation(id);
    setSidebarOpen(false);
  };

  const handleDeleteConversation = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        // In a real implementation, this would call the API to delete the conversation
        setConversations(prev => prev.filter(conv => conv.id !== id));
        if (selectedConversation === id) {
          setSelectedConversation(null);
        }
      } catch (error) {
        console.error('Error deleting conversation:', error);
      }
    }
  };

  const handleArchiveConversation = async (id: string) => {
    try {
      // In a real implementation, this would call the API to archive the conversation
      alert(`Conversation ${id} would be archived in a real implementation`);
    } catch (error) {
      console.error('Error archiving conversation:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Please log in to access the chat</h2>
          <button
            onClick={() => navigate('/login')}
            className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800">Conversations</h2>
          </div>

          <div className="p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={newConversationTitle}
                onChange={(e) => setNewConversationTitle(e.target.value)}
                placeholder="New conversation title"
                className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && handleCreateNewConversation()}
              />
              <button
                onClick={handleCreateNewConversation}
                className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-3 py-2 text-sm font-medium"
              >
                <FiPlus size={16} />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {conversations.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No conversations yet. Start a new one!
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {conversations.map((conversation) => (
                  <li
                    key={conversation.id}
                    className={`p-3 hover:bg-gray-50 cursor-pointer transition-colors ${
                      selectedConversation === conversation.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                    onClick={() => handleSelectConversation(conversation.id)}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-gray-900 truncate">{conversation.title}</h3>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(conversation.updatedAt).toLocaleDateString()} • {conversation.messageCount} messages
                        </p>
                      </div>
                      <div className="flex gap-1 ml-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleArchiveConversation(conversation.id);
                          }}
                          className="text-gray-400 hover:text-gray-600 p-1"
                          title="Archive conversation"
                        >
                          <FiArchive size={14} />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteConversation(conversation.id);
                          }}
                          className="text-gray-400 hover:text-red-600 p-1"
                          title="Delete conversation"
                        >
                          <FiTrash2 size={14} />
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <header className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="mr-3 text-gray-600 hover:text-gray-900 lg:hidden"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            )}
            <h1 className="text-xl font-semibold text-gray-800 flex items-center">
              <FiMessageSquare className="mr-2" />
              {selectedConversation
                ? conversations.find(c => c.id === selectedConversation)?.title || 'Chat'
                : 'Select a conversation or start a new one'}
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {user.name || user.email}
            </span>
            <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
              {user.name ? user.name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase()}
            </div>
          </div>
        </header>

        {/* Chat Interface */}
        <main className="flex-1 overflow-hidden">
          {selectedConversation ? (
            <ChatKitInterface
              userId={user.id}
              conversationId={selectedConversation}
              onMessageSend={(message) => {
                console.log('Message sent:', message);
              }}
              onConversationChange={(newConvId) => {
                setSelectedConversation(newConvId);
              }}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
              <FiMessageSquare className="h-16 w-16 text-gray-400 mb-4" />
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to the AI Todo Assistant!</h2>
              <p className="text-gray-600 max-w-md mb-6">
                Start a new conversation or select an existing one to manage your todos through natural language.
                Simply tell me what you want to do and I'll help you manage your tasks.
              </p>
              <button
                onClick={() => setSidebarOpen(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors"
              >
                Browse Conversations
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ChatPage;