// app/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to the chat page on component mount
    router.push('/chat');
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-800 mb-4">Redirecting to Chat...</h1>
        <p className="text-gray-600">If you are not redirected automatically, <a href="/chat" className="text-blue-500 hover:underline">click here</a>.</p>
      </div>
    </div>
  );
}