'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();

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
        {/* Back to website link and theme toggle */}
        <div className="flex justify-between items-center mb-6">
          <Link
            href="/"
            className={`${theme === 'dark' ? 'text-slate-200 hover:text-white' : 'text-slate-700 hover:text-slate-900'} text-sm flex items-center gap-2 transition-all duration-300 hover:translate-x-1 font-medium`}
            style={{
              background: theme === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(0, 0, 0, 0.05)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              padding: '8px 16px',
              borderRadius: '12px',
              border: theme === 'dark' 
                ? '1px solid rgba(255, 255, 255, 0.1)' 
                : '1px solid rgba(0, 0, 0, 0.1)',
              width: 'fit-content'
            }}
          >
            ← Back to website
          </Link>
          
          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl transition-all duration-300 hover:scale-110 border"
            style={{
              background: theme === 'dark' 
                ? 'rgba(255, 255, 255, 0.05)' 
                : 'rgba(0, 0, 0, 0.05)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              border: theme === 'dark' 
                ? '1px solid rgba(255, 255, 255, 0.1)' 
                : '1px solid rgba(0, 0, 0, 0.1)',
            }}
            aria-label="Toggle theme"
          >
            {theme === 'dark' ? (
              <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 006.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>

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
              <span className={`${theme === 'dark' ? 'text-blue-400' : 'text-blue-600'} text-sm font-semibold uppercase tracking-wider`}>Welcome Back</span>
            </div>
            <h1 className={`text-4xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'} mb-3`}>Account Login</h1>
            <p className={`${theme === 'dark' ? 'text-slate-200' : 'text-slate-600'} text-sm leading-relaxed`}>
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
              <p className={`${theme === 'dark' ? 'text-red-300' : 'text-red-600'} text-sm`}>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className={`block ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'} text-sm font-semibold mb-2 uppercase tracking-wider`}>
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
              <label className={`block ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'} text-sm font-semibold mb-2 uppercase tracking-wider`}>
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
                className={`w-4 h-4 rounded ${theme === 'dark' ? 'border-slate-500 bg-slate-800/50' : 'border-slate-400 bg-white'} text-blue-500`}
              />
              <label htmlFor="remember" className={`${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'} cursor-pointer text-xs font-medium`}>
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
            borderTop: theme === 'dark' 
              ? '1px solid rgba(255, 255, 255, 0.1)' 
              : '1px solid rgba(0, 0, 0, 0.1)'
          }}>
            <p className={`${theme === 'dark' ? 'text-slate-200' : 'text-slate-600'} text-sm`}>
              Don't have an account?{' '}
              <Link href="/register" className={`${theme === 'dark' ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'} font-semibold transition-colors duration-300`}>
                Create an account
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-center gap-6 text-xs uppercase tracking-wider font-medium">
          <span className={`${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>🔒 Secure SSL</span>
          <span className={`${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>📊 Data Encrypted</span>
          <span className={`${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>⚡ V2.4 Stable</span>
        </div>

        <div className="mt-4 text-center text-xs uppercase tracking-wider font-medium">
          <span className={`${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Bitcraft Institute © 2026</span>
        </div>
      </div>
    </div>
  );
}
