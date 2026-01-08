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
    <div className="min-h-screen flex items-center justify-center p-4 relative">
      <div className="w-full max-w-md relative z-10">
        {/* Back to website link */}
        <Link
          href="/"
          className="text-slate-300 hover:text-white text-sm flex items-center gap-2 mb-6 transition-all duration-300 hover:translate-x-1"
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            WebkitBackdropFilter: 'blur(10px)',
            padding: '8px 16px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            width: 'fit-content'
          }}
        >
          ← Back to website
        </Link>

        {/* Login Card */}
        <div className="premium-card">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%)',
                boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)'
              }}>
                <span className="text-2xl">🔑</span>
              </div>
              <span className="text-blue-400 text-sm font-semibold uppercase tracking-wider">Welcome Back</span>
            </div>
            <h1 className="text-4xl font-bold text-white mb-3">Account Login</h1>
            <p className="text-slate-300 text-sm leading-relaxed">
              Enter your credentials to continue your high-performance workflow.
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl" style={{
              background: 'rgba(239, 68, 68, 0.1)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              border: '1px solid rgba(239, 68, 68, 0.3)'
            }}>
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-slate-300 text-sm font-semibold mb-2 uppercase tracking-wider">
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
              <label className="block text-slate-300 text-sm font-semibold mb-2 uppercase tracking-wider">
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
                className="w-4 h-4 rounded border-slate-500 bg-slate-800/50 text-blue-500"
              />
              <label htmlFor="remember" className="text-slate-300 cursor-pointer text-xs">
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

          <div className="mt-8 pt-6 text-center" style={{
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <p className="text-slate-300 text-sm">
              Don't have an account?{' '}
              <Link href="/register" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors duration-300">
                Create an account
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-center gap-6 text-xs text-slate-400 uppercase tracking-wider">
          <span>🔒 Secure SSL</span>
          <span>📊 Data Encrypted</span>
          <span>⚡ V2.4 Stable</span>
        </div>

        <div className="mt-4 text-center text-xs text-slate-500 uppercase tracking-wider">
          Bitcraft Institute © 2026
        </div>
      </div>
    </div>
  );
}
