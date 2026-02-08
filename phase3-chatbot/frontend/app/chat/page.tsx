'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

// Chat is now embedded in the main page as a slide-out panel.
// This page redirects to home for backward compatibility.
export default function ChatPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/');
  }, [router]);

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-xl">Redirecting...</div>
    </div>
  );
}
