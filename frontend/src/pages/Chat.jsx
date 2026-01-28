import React from 'react';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Todo Chat Assistant</h1>
      <p className="text-gray-600 mb-6">Interact with the chatbot to manage your todos:</p>
      <ul className="text-gray-600 mb-6 list-disc pl-6">
        <li>Ask to create a new todo: "Create a todo to buy groceries"</li>
        <li>List your todos: "Show my todos"</li>
        <li>Mark a todo as complete: "Complete the grocery shopping"</li>
        <li>Ask about any of your existing todos</li>
      </ul>
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <ChatInterface />
      </div>
    </div>
  );
};

export default ChatPage;