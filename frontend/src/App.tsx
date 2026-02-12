import React from 'react';
import { Provider } from 'react-redux';
import store from './store';
import Layout from './components/layout/Layout';
import ChatPage from './components/chat/ChatPage';
import NotificationSystem from './components/shared/NotificationSystem';
import ErrorBoundary from './components/shared/ErrorBoundary';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <ErrorBoundary>
        <div className="App">
          <Layout>
            <ChatPage />
            <NotificationSystem position="top-right" />
          </Layout>
        </div>
      </ErrorBoundary>
    </Provider>
  );
};

export default App;