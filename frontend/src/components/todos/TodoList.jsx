import React, { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import TodoItem from './TodoItem';
import TodoForm from './TodoForm';

const TodoList = () => {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchTodos();
  }, []);

  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/todos');
      setTodos(response.data);
    } catch (error) {
      console.error('Error fetching todos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTodoAdded = (newTodo) => {
    setTodos([newTodo, ...todos]);
    setShowForm(false);
  };

  const handleTodoUpdated = (updatedTodo) => {
    setTodos(todos.map(todo =>
      todo.id === updatedTodo.id ? updatedTodo : todo
    ));
  };

  const handleTodoDeleted = (deletedTodoId) => {
    setTodos(todos.filter(todo => todo.id !== deletedTodoId));
  };

  const handleToggleComplete = async (todo) => {
    try {
      const response = await apiClient.patch(`/todos/${todo.id}/complete`, {
        completed: !todo.completed
      });

      setTodos(todos.map(t =>
        t.id === todo.id ? { ...t, completed: !todo.completed } : t
      ));
    } catch (error) {
      console.error('Error toggling todo completion:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-xl">Loading todos...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">My Todos</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none"
        >
          {showForm ? 'Cancel' : '+ Add Todo'}
        </button>
      </div>

      {showForm && (
        <div className="mb-6">
          <TodoForm onTodoAdded={handleTodoAdded} />
        </div>
      )}

      {todos.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No todos yet. Add one to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {todos.map(todo => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggleComplete={handleToggleComplete}
              onUpdate={handleTodoUpdated}
              onDelete={handleTodoDeleted}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TodoList;