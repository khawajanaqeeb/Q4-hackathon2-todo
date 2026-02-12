import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import ChatContainer from './ChatContainer';
import TodoPanel from '../shared/TodoPanel';

const MainContent: React.FC = () => {
  const { theme } = useSelector((state: RootState) => state.ui);
  const [todoPanelVisible, setTodoPanelVisible] = useState(true);

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Chat Container - Takes 2/3 of width on desktop, full width on mobile */}
      <div className={`flex-1 ${todoPanelVisible ? 'lg:w-2/3' : 'w-full'}`}>
        <ChatContainer />
      </div>

      {/* Todo Panel - Visible on desktop, collapsible on smaller screens */}
      <div className={`lg:w-1/3 lg:block ${todoPanelVisible ? 'block' : 'hidden'}`}>
        <TodoPanel />
      </div>

      {/* Toggle button for Todo Panel on smaller screens */}
      <div className="lg:hidden fixed bottom-4 right-4 z-10">
        <button
          onClick={() => setTodoPanelVisible(!todoPanelVisible)}
          className={`p-2 rounded-full shadow-lg ${
            theme === 'dark'
              ? 'bg-gray-700 text-white'
              : 'bg-white text-gray-800'
          }`}
          aria-label={todoPanelVisible ? 'Hide todo panel' : 'Show todo panel'}
        >
          {todoPanelVisible ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default MainContent;