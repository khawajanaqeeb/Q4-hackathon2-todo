'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { todoAPI } from '../lib/api';
import { Todo } from '../types/todo';
import ChatInterface from '../components/ChatInterface';

export default function HomePage() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();

  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [newTask, setNewTask] = useState('');
  const [newDescription, setNewDescription] = useState('');
  const [newPriority, setNewPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [selectedTag, setSelectedTag] = useState('');
  const availableTags = ['work', 'personal', 'urgent', 'shopping', 'health', 'finance'];
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'completed'>('all');
  const [filterPriority, setFilterPriority] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'title'>('date');
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    if (user) {
      fetchTodos();
    }
  }, [user]);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await todoAPI.getTodos();
      setTodos(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to load tasks';
      console.error('Error fetching todos:', message);
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.trim()) return;

    try {
      const tags = selectedTag ? [selectedTag] : [];
      const newTodo = await todoAPI.createTodo({
        title: newTask,
        description: newDescription,
        priority: newPriority,
        tags: tags,
      });
      setTodos([newTodo, ...todos]);
      setNewTask('');
      setNewDescription('');
      setNewPriority('medium');
      setSelectedTag('');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add task';
      console.error('Error adding task:', message);
      setError(message);
    }
  };

  const getFilteredAndSortedTodos = () => {
    let filtered = [...todos];

    if (filterStatus === 'pending') {
      filtered = filtered.filter(t => !t.completed);
    } else if (filterStatus === 'completed') {
      filtered = filtered.filter(t => t.completed);
    }

    if (filterPriority !== 'all') {
      filtered = filtered.filter(t => t.priority === filterPriority);
    }

    filtered.sort((a, b) => {
      if (sortBy === 'priority') {
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      } else if (sortBy === 'title') {
        return a.title.localeCompare(b.title);
      } else {
        return b.created_at.localeCompare(a.created_at);
      }
    });

    return filtered;
  };

  const handleToggle = async (id: string) => {
    try {
      const updated = await todoAPI.toggleTodoCompletion(id);
      setTodos(todos.map(t => t.id === id ? updated : t));
    } catch (error) {
      console.error('Error toggling task:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this task?')) return;
    try {
      await todoAPI.deleteTodo(id);
      setTodos(todos.filter(t => t.id !== id));
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  const handleLogout = () => {
    logout();
    setTodos([]);
  };

  const getPriorityBadge = (priority: string) => {
    const badges = {
      high: 'bg-red-500/20 text-red-400 border-red-500/50',
      medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      low: 'bg-green-500/20 text-green-400 border-green-500/50'
    };
    return badges[priority as keyof typeof badges] || badges.medium;
  };

  return (
    <div className="min-h-screen transition-colors duration-300 relative">
      {/* Premium Header with Theme Toggle */}
      <header className={`border-b transition-colors duration-300 relative z-10 ${
        theme === 'dark'
          ? 'bg-slate-800/80 border-slate-700'
          : 'bg-white/90 border-slate-200'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-2xl">📋</span>
              </div>
              <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                Premium<span className="text-blue-500">Task</span>
              </h1>
            </div>
            <div className="flex items-center gap-4">
              {/* Theme Toggle Button */}
              <button
                onClick={toggleTheme}
                className={`p-2.5 rounded-xl transition-all duration-300 hover:scale-110 border ${
                  theme === 'dark'
                    ? 'bg-slate-700 border-slate-600 hover:bg-slate-600'
                    : 'bg-slate-100 border-slate-300 hover:bg-slate-200'
                }`}
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? (
                  <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-slate-700" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                )}
              </button>

              {user ? (
                <>
                  <button
                    onClick={() => setChatOpen(!chatOpen)}
                    className={`btn-primary mr-3 ${chatOpen ? 'ring-2 ring-blue-400' : ''}`}
                  >
                    {chatOpen ? 'Close Chat' : 'AI Chat'}
                  </button>
                  <span className={`text-sm ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'}`}>
                    <span className="font-medium">{user.username}</span>
                  </span>
                  <button
                    onClick={handleLogout}
                    className="btn-secondary"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link href="/login" className="btn-secondary">
                    Login
                  </Link>
                  <Link href="/register" className="btn-primary">
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      {user && (
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="stat-card">
              <div className={`text-xs font-semibold mb-1 uppercase tracking-wider ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>TOTAL TASKS</div>
              <div className={`text-2xl font-bold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>{todos.length}</div>
            </div>
            <div className="stat-card">
              <div className={`text-xs font-semibold mb-1 uppercase tracking-wider ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>IN PROGRESS</div>
              <div className="text-2xl font-bold text-orange-500">{todos.filter(t => !t.completed).length}</div>
            </div>
            <div className="stat-card">
              <div className={`text-xs font-semibold mb-1 uppercase tracking-wider ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>COMPLETED</div>
              <div className="text-2xl font-bold text-green-500">{todos.filter(t => t.completed).length}</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 pb-12">
        {!user ? (
          <div className="premium-card text-center py-16 max-w-2xl mx-auto">
            <h2 className={`text-5xl font-bold mb-4 leading-tight ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
              Transform Chaos Into
              <br />
              <span className="text-blue-500">Flawless Execution.</span>
            </h2>
            <p className={`text-lg mb-8 leading-relaxed ${theme === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
              The ultimate productivity powerhouse for elite performers. Military-grade security, blazing-fast sync, and laser-focused workflow automation.
            </p>
            <div className="flex justify-center gap-4">
              <Link href="/register" className="btn-primary">
                Get Started for Free
              </Link>
              <Link href="/login" className="btn-secondary">
                Sign In
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Add Task Form */}
            <div className="premium-card">
              <h3 className={`text-base font-semibold mb-3 flex items-center gap-2 ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>
                <span className="text-blue-500">✦</span>
                What's the next milestone?
              </h3>
              <form onSubmit={handleAddTask} className="space-y-3">
                <input
                  type="text"
                  value={newTask}
                  onChange={(e) => setNewTask(e.target.value)}
                  placeholder="Describe what needs to be done..."
                  required
                  className="input-dark"
                />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <select
                    value={newPriority}
                    onChange={(e) => setNewPriority(e.target.value as 'low' | 'medium' | 'high')}
                    className="input-dark"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                  <select
                    value={selectedTag}
                    onChange={(e) => setSelectedTag(e.target.value)}
                    className="input-dark"
                  >
                    <option value="">No Engineering discipline</option>
                    {availableTags.map(tag => (
                      <option key={tag} value={tag}>
                        {tag.charAt(0).toUpperCase() + tag.slice(1)}
                      </option>
                    ))}
                  </select>
                  <button type="submit" className="btn-primary">
                    Add Task →
                  </button>
                </div>
                <textarea
                  value={newDescription}
                  onChange={(e) => setNewDescription(e.target.value)}
                  placeholder="Add description (optional)..."
                  rows={2}
                  className="input-dark resize-none"
                />
              </form>
            </div>

            {/* Filter Controls */}
            <div className="premium-card">
              <div className="flex flex-wrap gap-3 items-center">
                <span className={`text-xs font-semibold uppercase tracking-wider ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Filters:</span>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value as 'all' | 'pending' | 'completed')}
                  className="input-dark px-3 py-2 text-xs w-auto"
                >
                  <option value="all">All Status</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                </select>
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value as 'all' | 'low' | 'medium' | 'high')}
                  className="input-dark px-3 py-2 text-xs w-auto"
                >
                  <option value="all">All Priorities</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'date' | 'priority' | 'title')}
                  className="input-dark px-3 py-2 text-xs w-auto"
                >
                  <option value="date">Sort by Date</option>
                  <option value="priority">Sort by Priority</option>
                  <option value="title">Sort by Title</option>
                </select>
              </div>
            </div>

            {/* Error Banner */}
            {error && (
              <div className="premium-card border border-red-500/30 bg-red-500/10">
                <div className="flex items-center justify-between">
                  <p className="text-red-400 text-sm">{error}</p>
                  <button onClick={fetchTodos} className="text-xs text-blue-400 hover:text-blue-300 underline">
                    Retry
                  </button>
                </div>
              </div>
            )}

            {/* Tasks List */}
            <div className="space-y-3">
              {loading ? (
                <div className="premium-card text-center py-12">
                  <div className="text-slate-400 animate-pulse">Loading tasks...</div>
                </div>
              ) : getFilteredAndSortedTodos().length === 0 ? (
                <div className="premium-card text-center py-12">
                  <div className="text-6xl mb-4 opacity-50">📭</div>
                  <p className={`text-xl font-semibold ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>No tasks found</p>
                  <p className="text-slate-500 mt-2">
                    {todos.length === 0 ? 'Create your first task above' : 'Try adjusting your filters'}
                  </p>
                </div>
              ) : (
                getFilteredAndSortedTodos().map((todo) => (
                  <div key={todo.id} className={todo.completed ? 'task-card-completed' : 'task-card'}>
                    <div className="flex items-start gap-4">
                      <input
                        type="checkbox"
                        checked={todo.completed}
                        onChange={() => handleToggle(todo.id)}
                        className={`w-5 h-5 mt-1 cursor-pointer rounded text-blue-500 focus:ring-blue-500 ${
                          theme === 'dark' ? 'border-slate-500 bg-slate-800/50' : 'border-slate-300 bg-white'
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className={`text-base font-semibold mb-2 ${
                          todo.completed
                            ? 'line-through text-slate-500'
                            : theme === 'dark' ? 'text-white' : 'text-slate-900'
                        }`}>
                          {todo.title}
                        </h4>
                        {todo.description && (
                          <p className={`text-sm mb-3 ${
                            todo.completed
                              ? 'line-through text-slate-500'
                              : theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
                          }`}>
                            {todo.description}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-2">
                          <span className={`px-3 py-1 rounded-md text-xs font-medium border ${getPriorityBadge(todo.priority)}`}>
                            {todo.priority.toUpperCase()}
                          </span>
                          {todo.tags && todo.tags.length > 0 && (
                            <span className="px-3 py-1 rounded-md text-xs font-medium bg-blue-500/20 text-blue-400 border border-blue-500/50">
                              {todo.tags.join(', ')}
                            </span>
                          )}
                          <span className={`px-3 py-1 rounded-md text-xs font-medium ${
                            todo.completed
                              ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                              : 'bg-orange-500/20 text-orange-400 border border-orange-500/50'
                          }`}>
                            {todo.completed ? 'Done' : 'In Progress'}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(todo.id)}
                        className="btn-danger text-sm"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Floating Chat Button (bottom-right) */}
      {user && !chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
          aria-label="Open AI Chat"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </button>
      )}

      {/* Slide-out Chat Panel (right side, 1/4 screen) */}
      {user && (
        <div
          className={`fixed top-0 right-0 h-full w-1/4 min-w-[320px] max-w-[400px] z-40 transform transition-transform duration-300 ease-in-out ${
            chatOpen ? 'translate-x-0' : 'translate-x-full'
          }`}
          style={{ boxShadow: chatOpen ? '-4px 0 24px rgba(0,0,0,0.4)' : 'none' }}
        >
          <div className="h-full flex flex-col bg-gray-900 border-l border-gray-700">
            {/* Chat Panel Header */}
            <div className="flex items-center justify-between px-4 py-3 bg-gray-800 border-b border-gray-700">
              <div>
                <h2 className="text-sm font-semibold text-white">AI Todo Assistant</h2>
                <p className="text-xs text-gray-400">Manage tasks with chat</p>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                className="p-1.5 rounded-lg hover:bg-gray-700 text-gray-400 hover:text-white transition-colors"
                aria-label="Close chat"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {/* Chat Interface */}
            <div className="flex-1 overflow-hidden">
              <ChatInterface userId={user.id} onTaskChange={fetchTodos} />
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className={`border-t mt-16 relative z-10 ${
        theme === 'dark'
          ? 'bg-slate-800/80 border-slate-700'
          : 'bg-white/90 border-slate-200'
      }`}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center text-sm">
            <div className={`flex gap-6 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
              <span>SECURE SSL</span>
              <span>DATA ENCRYPTED</span>
              <span>24/7 SUPPORT</span>
            </div>
            <div className={`font-semibold ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'}`}>
              BITCRAFT INSTITUTE &copy; 2026
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
