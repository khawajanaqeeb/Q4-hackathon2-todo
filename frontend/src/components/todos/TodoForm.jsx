import React, { useState } from 'react';
import apiClient from '../../services/api';

const TodoForm = ({ onTodoAdded }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await apiClient.post('/todos', formData);
      onTodoAdded(response.data);
      setFormData({ title: '', description: '', priority: 'medium' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create todo');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <h3 className="text-lg font-medium text-gray-800 mb-3">Create New Todo</h3>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
            rows="2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
          <select
            name="priority"
            value={formData.priority}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-600"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div className="flex space-x-2">
          <button
            type="submit"
            disabled={loading}
            className={`px-4 py-2 rounded-md text-white ${loading ? 'bg-blue-400' : 'bg-blue-600'} hover:${loading ? 'bg-blue-400' : 'bg-blue-700'} focus:outline-none`}
          >
            {loading ? 'Creating...' : 'Create Todo'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TodoForm;