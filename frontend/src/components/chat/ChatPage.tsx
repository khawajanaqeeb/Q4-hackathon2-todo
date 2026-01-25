import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import MainContent from './MainContent';

const ChatPage: React.FC = () => {
  const { theme } = useSelector((state: RootState) => state.ui);

  return (
    <div className={`flex flex-col h-full ${theme === 'dark' ? 'dark' : ''}`}>
      <MainContent />
    </div>
  );
};

export default ChatPage;