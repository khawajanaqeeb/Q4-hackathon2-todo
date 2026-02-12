import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { setInputText, setInputDisabled, resetInput } from '@/store/slices/uiSlice';
import { addMessage } from '@/store/slices/chatSlice';
import { Message } from '@/types';
import { v4 as uuidv4 } from 'uuid';

const MessageInput: React.FC = () => {
  const dispatch = useDispatch();
  const { inputText, isInputDisabled } = useSelector((state: RootState) => state.ui);
  const { currentConversationId } = useSelector((state: RootState) => state.chat);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Adjust textarea height based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [inputText]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const sendMessage = () => {
    if (inputText.trim() === '') return;

    // Create a new message object
    const newMessage: Message = {
      id: uuidv4(),
      content: inputText,
      sender: 'user',
      timestamp: new Date(),
      status: 'sent'
    };

    // Add the message to the store immediately (optimistic update)
    dispatch(addMessage({ conversationId: currentConversationId || 'default', message: newMessage }));

    // Disable input while sending
    dispatch(setInputDisabled(true));

    // Simulate sending message (in real app, this would call API)
    setTimeout(() => {
      // In a real implementation, we would send the message via API
      // and handle the response in the chat hook or service
      dispatch(resetInput());
      dispatch(setInputDisabled(false));
    }, 500);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Submit on Cmd/Ctrl + Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <form onSubmit={handleSubmit} role="form" aria-label="Send message">
      <div className="flex items-end space-x-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => dispatch(setInputText(e.target.value))}
            onKeyDown={handleKeyDown}
            disabled={isInputDisabled}
            placeholder="Type your message here..."
            className={`w-full resize-none py-2 px-3 rounded-lg border focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
              isInputDisabled
                ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
            }`}
            rows={1}
            aria-label="Message input"
            aria-disabled={isInputDisabled}
          />
        </div>
        <button
          type="submit"
          disabled={isInputDisabled || inputText.trim() === ''}
          className={`p-2 rounded-full ${
            inputText.trim() === ''
              ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
          aria-label="Send message"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      </div>
    </form>
  );
};

export default MessageInput;