'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import Link from 'next/link';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const router = useRouter();
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await register(name, email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Failed to register');
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
          className="text-slate-200 hover:text-white text-sm flex items-center gap-2 mb-6 transition-all duration-300 hover:translate-x-1 font-medium"
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

        {/* Register Card */}
        <div className="premium-card">
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.8) 0%, rgba(139, 92, 246, 0.8) 100%)',
                boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)'
              }}>
                <span className="text-2xl">🚀</span>
              </div>
              <span className="text-blue-400 text-sm font-semibold uppercase tracking-wider">Start Your Journey</span>
            </div>
            <h1 className="text-4xl font-bold text-white mb-3">Create Account</h1>
            <p className="text-slate-200 text-sm leading-relaxed">
              Join the elite circle of high-performers today.
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
              <label className="block text-slate-200 text-sm font-semibold mb-2 uppercase tracking-wider">
                Business Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="name@company.com"
                className="input-dark"
              />
            </div>

            <div>
              <label className="block text-slate-200 text-sm font-semibold mb-2 uppercase tracking-wider">
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                placeholder="John Doe"
                className="input-dark"
              />
            </div>

            <div>
              <label className="block text-slate-200 text-sm font-semibold mb-2 uppercase tracking-wider">
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

            <div>
              <label className="block text-slate-200 text-sm font-semibold mb-2 uppercase tracking-wider">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="input-dark"
              />
            </div>

            <div className="text-xs p-4 rounded-xl font-medium" style={{
              background: 'rgba(255, 255, 255, 0.03)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'rgba(255, 255, 255, 0.7)'
            }}>
              BY CLICKING "CREATE WORKSPACE" YOU ARE AGREEING TO OUR{' '}
              <span className="text-blue-400 cursor-pointer hover:text-blue-300 transition-colors duration-300 font-semibold">TERMS OF SERVICE</span>
              {' '}AND{' '}
              <span className="text-blue-400 cursor-pointer hover:text-blue-300 transition-colors duration-300 font-semibold">PRIVACY POLICY</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'CREATING WORKSPACE...' : 'CREATE WORKSPACE →'}
            </button>
          </form>

          <div className="mt-8 pt-6 text-center" style={{
            borderTop: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <p className="text-slate-200 text-sm">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300 font-semibold transition-colors duration-300">
                Sign in instead
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-center gap-6 text-xs text-slate-300 uppercase tracking-wider font-medium">
          <span>🔒 SOC2 Certified</span>
          <span>📊 ISO Certified</span>
          <span>⚡ 24/7 Support</span>
        </div>

        <div className="mt-4 text-center text-xs text-slate-400 uppercase tracking-wider font-medium">
          Bitcraft Institute © 2026
        </div>
      </div>
    </div>
  );
}
