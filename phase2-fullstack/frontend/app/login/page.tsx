'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back to website link */}
        <Link href="/" className="text-slate-400 hover:text-white text-sm flex items-center gap-2 mb-6">
          ← Back to website
        </Link>

        {/* Login Card */}
        <div className="premium-card">
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">🔑</span>
              </div>
              <span className="text-blue-500 text-sm font-medium uppercase tracking-wider">Welcome Back</span>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Account Login</h1>
            <p className="text-slate-400 text-sm">
              Enter your credentials to continue your high-performance workflow.
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@email.com"
                className="input-dark"
              />
            </div>

            <div>
              <label className="block text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="input-dark"
              />
            </div>

            <div className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                id="remember"
                className="w-4 h-4 rounded border-slate-600 bg-slate-900 text-blue-600"
              />
              <label htmlFor="remember" className="text-slate-400 cursor-pointer">
                SECURE AND ENCRYPTED MACHINE BASED SESSIONS
              </label>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'SIGNING IN...' : 'SIGN IN TO PORTAL →'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800 text-center">
            <p className="text-slate-400 text-sm">
              Don't have an account?{' '}
              <Link href="/register" className="text-blue-500 hover:text-blue-400 font-medium">
                Create an account
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-center gap-6 text-xs text-slate-600 uppercase tracking-wider">
          <span>🔒 Secure SSL</span>
          <span>📊 Data Encrypted</span>
          <span>⚡ V2.4 Stable</span>
        </div>

        <div className="mt-4 text-center text-xs text-slate-700 uppercase tracking-wider">
          Bitcraft Institute © 2026
        </div>
      </div>
    </div>
  );
}
