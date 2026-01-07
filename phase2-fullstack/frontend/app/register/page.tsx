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
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Back to website link */}
        <Link href="/" className="text-slate-400 hover:text-white text-sm flex items-center gap-2 mb-6">
          ← Back to website
        </Link>

        {/* Register Card */}
        <div className="premium-card">
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">🚀</span>
              </div>
              <span className="text-blue-500 text-sm font-medium uppercase tracking-wider">Start Your Journey</span>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
            <p className="text-slate-400 text-sm">
              Join the elite circle of high-performers today.
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
              <label className="block text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">
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

            <div>
              <label className="block text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">
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

            <div className="text-xs text-slate-500 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
              BY CLICKING "CREATE WORKSPACE" YOU ARE AGREEING TO OUR{' '}
              <span className="text-blue-500 cursor-pointer hover:text-blue-400">TERMS OF SERVICE</span>
              {' '}AND{' '}
              <span className="text-blue-500 cursor-pointer hover:text-blue-400">PRIVACY POLICY</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'CREATING WORKSPACE...' : 'CREATE WORKSPACE →'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800 text-center">
            <p className="text-slate-400 text-sm">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-500 hover:text-blue-400 font-medium">
                Sign in instead
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 flex justify-center gap-6 text-xs text-slate-600 uppercase tracking-wider">
          <span>🔒 SOC2 Certified</span>
          <span>📊 ISO Certified</span>
          <span>⚡ 24/7 Support</span>
        </div>

        <div className="mt-4 text-center text-xs text-slate-700 uppercase tracking-wider">
          Bitcraft Institute © 2026
        </div>
      </div>
    </div>
  );
}
