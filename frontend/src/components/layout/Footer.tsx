import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';

const Footer: React.FC = () => {
  const { isConnected } = useSelector((state: RootState) => state.chat);

  return (
    <footer
      className="p-4 text-sm"
      role="contentinfo"
    >
      <div className="container mx-auto flex justify-between items-center">
        <div>
          <p>&copy; {new Date().getFullYear()} Todo Chat Assistant. All rights reserved.</p>
        </div>
        <div className="flex items-center space-x-2">
          <span>Status:</span>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            isConnected
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            <span className={`mr-1.5 h-1.5 w-1.5 rounded-full ${
              isConnected ? 'bg-green-400' : 'bg-red-400'
            }`} />
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;