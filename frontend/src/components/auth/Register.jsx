import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth';

const Register = () => {
  const [userData, setUserData] = useState({
    username: '',
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleChange = (e) => {
    setUserData({
      ...userData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await authService.register(userData.username, userData.email, userData.password);
      navigate('/login'); // Redirect to login after successful registration
    } catch (err) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="px-8 py-6 mt-4 text-left bg-white shadow-lg rounded-lg w-96">
        <h3 className="text-2xl font-bold text-center">Create an account</h3>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="mt-4">
            <div>
              <label className="block text-gray-700">Username</label>
              <input
                type="text"
                name="username"
                value={userData.username}
                onChange={handleChange}
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                required
              />
            </div>
            <div className="mt-4">
              <label className="block text-gray-700">Email</label>
              <input
                type="email"
                name="email"
                value={userData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                required
              />
            </div>
            <div className="mt-4">
              <label className="block text-gray-700">Password</label>
              <input
                type="password"
                name="password"
                value={userData.password}
                onChange={handleChange}
                className="w-full px-4 py-2 mt-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
                required
              />
            </div>
            <div className="flex items-center justify-between mt-4">
              <button
                type="submit"
                disabled={loading}
                className={`px-6 py-2 leading-5 text-white transition-colors duration-200 transform bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {loading ? 'Creating account...' : 'Register'}
              </button>
              <span
                className="text-sm text-blue-600 hover:underline cursor-pointer"
                onClick={() => navigate('/login')}
              >
                Login
              </span>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;