import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store';
import { hideNotification } from '@/store/slices/uiSlice';

interface NotificationSystemProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
}

const NotificationSystem: React.FC<NotificationSystemProps> = ({ position = 'top-right' }) => {
  const dispatch = useDispatch();
  const { notification } = useSelector((state: RootState) => state.ui);
  const [isVisible, setIsVisible] = useState(false);

  // Position classes
  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
  };

  // Style classes based on notification type
  const getTypeStyles = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-100 border-green-400 text-green-700';
      case 'error':
        return 'bg-red-100 border-red-400 text-red-700';
      case 'warning':
        return 'bg-yellow-100 border-yellow-400 text-yellow-700';
      case 'info':
      default:
        return 'bg-blue-100 border-blue-400 text-blue-700';
    }
  };

  useEffect(() => {
    if (notification.isVisible) {
      setIsVisible(true);
      // Auto-hide notification after duration
      const timer = setTimeout(() => {
        setIsVisible(false);
        // Dispatch hide notification after animation completes
        setTimeout(() => {
          dispatch(hideNotification());
        }, 300); // Match the transition duration
      }, notification.duration);

      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
    }
  }, [notification, dispatch]);

  if (!notification.isVisible && !isVisible) {
    return null;
  }

  return (
    <div
      className={`fixed z-50 max-w-md w-full transform transition-all duration-300 ease-in-out ${
        isVisible ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0'
      } ${positionClasses[position]}`}
    >
      <div
        className={`border rounded px-4 py-3 shadow-lg ${getTypeStyles(notification.type)}`}
        role="alert"
      >
        <div className="flex justify-between items-start">
          <div className="flex items-center">
            {/* Icon based on notification type */}
            <div className="mr-3">
              {notification.type === 'success' && (
                <svg className="fill-current h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM6.7 9.29L9 11.6l4.3-4.3 1.42 1.42L9 14.4 5.29 10.7l1.42-1.42z"/>
                </svg>
              )}
              {notification.type === 'error' && (
                <svg className="fill-current h-6 w-6 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm1.41-1.41A8 8 0 1 0 15.66 4.34 8 8 0 0 0 4.34 15.66zm9.9-8.49L11.41 10l2.83 2.83-1.41 1.41L10 11.41l-2.83 2.83-1.41-1.41L8.59 10 5.76 7.17l1.41-1.41L10 8.59l2.83-2.83 1.41 1.41z"/>
                </svg>
              )}
              {notification.type === 'warning' && (
                <svg className="fill-current h-6 w-6 text-yellow-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm12.73-1.41A8 8 0 1 0 4.34 4.34a8 8 0 0 0 11.32 11.32zM10 8v4a1 1 0 001 1h1v-6H9v2h1zm-1 7a1 1 0 100-2 1 1 0 000 2z"/>
                </svg>
              )}
              {notification.type === 'info' && (
                <svg className="fill-current h-6 w-6 text-blue-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                  <path d="M2.93 17.07A10 10 0 1 1 17.07 2.93 10 10 0 0 1 2.93 17.07zm1.41-1.41A8 8 0 1 0 15.66 4.34 8 8 0 0 0 4.34 15.66zm8.49-11.31a1 1 0 00-1.42 0L8 9.41l-1.06-1.06a1 1 0 00-1.42 1.42l2 2a1 1 0 001.42 0l4-4a1 1 0 000-1.42z"/>
                </svg>
              )}
            </div>
            <p className="font-bold">{notification.type.charAt(0).toUpperCase() + notification.type.slice(1)}</p>
          </div>
          <button
            onClick={() => {
              setIsVisible(false);
              setTimeout(() => {
                dispatch(hideNotification());
              }, 300);
            }}
            className="text-gray-600 hover:text-gray-800 focus:outline-none"
            aria-label="Close notification"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div className="mt-2">
          <p className="text-sm">{notification.message}</p>
        </div>
      </div>
    </div>
  );
};

export default NotificationSystem;