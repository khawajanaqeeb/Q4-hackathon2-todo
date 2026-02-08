import React, { useState, useRef, useEffect } from 'react';
import { MainContainer, ChatContainer, MessageList, Message, MessageInput, TypingIndicator } from '@chatscope/chat-ui-kit-react';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import apiClient from '../../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      message: "Hello! I'm your todo assistant. You can ask me to create, list, or update your todos.",
      sender: "System",
      type: "system"
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      message: message,
      sender: "You",
      type: "sent"
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Get current user ID from localStorage
      const userStr = localStorage.getItem('user');
      if (!userStr) {
        throw new Error('User not authenticated');
      }
      
      const user = JSON.parse(userStr);
      const userId = user.id;

      // Send the message to the backend using the correct endpoint
      // Since the API client already has /api as base URL, the endpoint is /api/chat/{userId}
      const response = await apiClient.post(`/chat/${userId}`, {
        messages: [{ role: "user", content: message }],
        conversation: currentConversationId ? { id: currentConversationId } : null
      });

      // Update conversation ID if it's the first message
      if (!currentConversationId && response.data.conversation) {
        setCurrentConversationId(response.data.conversation.id);
      }

      // Add bot response to the chat
      const botMessage = {
        id: Date.now() + 1,
        message: response.data.messages[0]?.content || "I received your message.",
        sender: "Todo Assistant",
        type: "received"
      };

      setMessages(prev => [...prev, botMessage]);

      // Process any actions returned by the chatbot
      if (response.data.actions && response.data.actions.length > 0) {
        for (const action of response.data.actions) {
          if (action.type === 'create_todo' && action.data) {
            const todoMessage = {
              id: Date.now() + 2,
              message: `Created todo: "${action.data.title}"`,
              sender: "System",
              type: "system"
            };
            setMessages(prev => [...prev, todoMessage]);
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        message: "Sorry, I encountered an error processing your request.",
        sender: "System",
        type: "system"
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ position: "relative", height: "500px", margin: "20px" }}>
      <MainContainer>
        <ChatContainer>
          <MessageList>
            {messages.map((msg) => (
              <Message
                key={msg.id}
                model={{
                  message: msg.message,
                  sender: msg.sender,
                  direction: msg.type === 'sent' ? 'outgoing' : 'incoming',
                  position: 'normal'
                }}
              />
            ))}
            {isLoading && (
              <Message
                model={{
                  message: "Thinking...",
                  sender: "Todo Assistant",
                  direction: 'incoming',
                  position: 'normal'
                }}
              >
                <TypingIndicator content="Todo Assistant is typing" />
              </Message>
            )}
            <div ref={messagesEndRef} />
          </MessageList>
          <MessageInput
            placeholder="Type a message here (e.g., 'Create a todo to buy groceries')"
            onSend={handleSendMessage}
            value={inputValue}
            onChange={(val) => setInputValue(val)}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
};

export default ChatInterface;