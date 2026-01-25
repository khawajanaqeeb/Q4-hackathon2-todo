import { useState, useEffect, useCallback } from 'react';
import { Message, Conversation, ChatMessageResponse } from '@/types';
import chatApi from '@/services/chatApi';
import websocket from '@/services/websocket';

interface UseChatProps {
  userId: string;
  conversationId?: string;
}

interface UseChatResult {
  messages: Message[];
  sendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  currentConversation: Conversation | null;
  setCurrentConversation: (conversation: Conversation | null) => void;
  isConnected: boolean;
}

const useChat = ({ userId, conversationId }: UseChatProps): UseChatResult => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    const handleConnect = () => setIsConnected(true);
    const handleDisconnect = () => setIsConnected(false);
    const handleError = (data: any) => setError(data.error?.message || 'Connection error');

    websocket.subscribe('connect', handleConnect);
    websocket.subscribe('disconnect', handleDisconnect);
    websocket.subscribe('error', handleError);

    websocket.connect().catch(err => {
      console.error('WebSocket connection failed:', err);
      setError('Failed to connect to chat service');
    });

    return () => {
      websocket.unsubscribe('connect', handleConnect);
      websocket.unsubscribe('disconnect', handleDisconnect);
      websocket.unsubscribe('error', handleError);
    };
  }, []);

  // Handle incoming messages from WebSocket
  useEffect(() => {
    const handleMessage = (data: any) => {
      if (data.type === 'new_message' || data.type === 'stream_update') {
        setMessages(prev => [...prev, data.message]);
      } else if (data.type === 'typing_indicator') {
        // Handle typing indicator updates if needed
      }
    };

    websocket.subscribe('message', handleMessage);

    return () => {
      websocket.unsubscribe('message', handleMessage);
    };
  }, []);

  // Load conversation history if conversationId is provided
  useEffect(() => {
    if (conversationId) {
      loadConversationHistory();
    }
  }, [conversationId]);

  const loadConversationHistory = async () => {
    if (!conversationId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await chatApi.getConversationMessages(userId, conversationId);
      const messageObjects = response.messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
      setMessages(messageObjects);
    } catch (err) {
      setError((err as Error).message);
      console.error('Failed to load conversation history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = useCallback(async (message: string) => {
    setIsLoading(true);
    setError(null);

    try {
      // Add the message to the UI immediately as 'sent'
      const newMessage: Message = {
        id: Date.now().toString(),
        content: message,
        sender: 'user',
        timestamp: new Date(),
        status: 'sent'
      };

      setMessages(prev => [...prev, newMessage]);

      // Send the message via API
      const response: ChatMessageResponse = await chatApi.sendMessage(userId, message, conversationId);

      // Update the message status to 'delivered'
      setMessages(prev =>
        prev.map(msg =>
          msg.id === newMessage.id ? { ...msg, status: 'delivered' } : msg
        )
      );

      // The AI response will come through WebSocket, handled by the effect above
    } catch (err) {
      setError((err as Error).message);
      console.error('Failed to send message:', err);

      // Update the message status to 'failed'
      setMessages(prev =>
        prev.map(msg =>
          msg.content === message && msg.sender === 'user' && msg.status === 'sent'
            ? { ...msg, status: 'failed' }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [userId, conversationId]);

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    currentConversation,
    setCurrentConversation,
    isConnected
  };
};

export default useChat;