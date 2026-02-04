'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import ChatInterface from '../../components/ChatInterface';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
      return;
    }

    if (user) {
      setUserId(user.id);
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-xl">Redirecting to login...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">AI Todo Assistant</h1>
          <p className="text-gray-400">Manage your tasks with natural language commands</p>
        </header>

        <main className="max-w-4xl mx-auto">
          {userId ? (
            <ChatInterface userId={userId} />
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-400">Loading chat interface...</p>
            </div>
          )}
        </main>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Your conversations are securely stored and processed</p>
        </footer>
      </div>
    </div>
  );
}