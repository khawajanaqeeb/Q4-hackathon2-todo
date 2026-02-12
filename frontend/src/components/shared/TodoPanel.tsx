import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '@/store';
import { TodoItem, TodoPriority } from '@/types';
import { addTodo, updateTodo, deleteTodo, toggleTodoCompletion, setFilter } from '@/store/slices/todoSlice';
import { v4 as uuidv4 } from 'uuid';

const TodoPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { todos, filter, loading, error } = useSelector((state: RootState) => state.todo);
  const { theme } = useSelector((state: RootState) => state.ui);

  const [newTodoTitle, setNewTodoTitle] = useState('');
  const [newTodoDescription, setNewTodoDescription] = useState('');
  const [newTodoPriority, setNewTodoPriority] = useState<TodoPriority>('medium');

  const filteredTodos = Object.values(todos).filter(todo => {
    if (filter === 'completed') return todo.completed;
    if (filter === 'active') return !todo.completed;
    return true; // 'all'
  });

  const handleAddTodo = () => {
    if (newTodoTitle.trim() === '') return;

    const newTodo: TodoItem = {
      id: uuidv4(),
      title: newTodoTitle,
      description: newTodoDescription,
      completed: false,
      priority: newTodoPriority,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    dispatch(addTodo(newTodo));
    setNewTodoTitle('');
    setNewTodoDescription('');
    setNewTodoPriority('medium');
  };

  const handleToggleTodo = (id: string) => {
    dispatch(toggleTodoCompletion(id));
  };

  const handleDeleteTodo = (id: string) => {
    dispatch(deleteTodo(id));
  };

  const handlePriorityChange = (id: string, priority: TodoPriority) => {
    const todo = todos[id];
    if (todo) {
      const updatedTodo: TodoItem = {
        ...todo,
        priority,
        updatedAt: new Date(),
      };
      dispatch(updateTodo(updatedTodo));
    }
  };

  return (
    <div
      className={`h-full flex flex-col ${
        theme === 'dark' ? 'bg-gray-800' : 'bg-white'
      }`}
      role="region"
      aria-label="Todo panel"
    >
      <div
        className={`p-4 border-b ${
          theme === 'dark'
            ? 'border-gray-700 bg-gray-900'
            : 'border-gray-200 bg-gray-50'
        }`}
      >
        <h2 className="text-lg font-semibold">Todo List</h2>
      </div>

      <div className="p-4 flex-1 overflow-y-auto">
        {/* Add new todo form */}
        <div className="mb-6">
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={newTodoTitle}
              onChange={(e) => setNewTodoTitle(e.target.value)}
              placeholder="Add a new task..."
              className={`flex-1 p-2 rounded border ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-white'
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
              aria-label="New todo title"
            />
            <select
              value={newTodoPriority}
              onChange={(e) => setNewTodoPriority(e.target.value as TodoPriority)}
              className={`p-2 rounded border ${
                theme === 'dark'
                  ? 'bg-gray-700 border-gray-600 text-white'
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
              aria-label="Todo priority"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
            <button
              onClick={handleAddTodo}
              disabled={!newTodoTitle.trim()}
              className={`p-2 rounded ${
                !newTodoTitle.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
              aria-label="Add todo"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
          <textarea
            value={newTodoDescription}
            onChange={(e) => setNewTodoDescription(e.target.value)}
            placeholder="Description (optional)"
            className={`w-full p-2 rounded border ${
              theme === 'dark'
                ? 'bg-gray-700 border-gray-600 text-white'
                : 'bg-white border-gray-300 text-gray-900'
            }`}
            rows={2}
            aria-label="New todo description"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex space-x-2 mb-4">
          {(['all', 'active', 'completed'] as const).map((f) => (
            <button
              key={f}
              onClick={() => dispatch(setFilter(f))}
              className={`px-3 py-1 rounded-full text-sm ${
                filter === f
                  ? 'bg-indigo-600 text-white'
                  : theme === 'dark'
                  ? 'bg-gray-700 text-gray-300'
                  : 'bg-gray-200 text-gray-700'
              }`}
              aria-pressed={filter === f}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        {/* Todo list */}
        <div className="space-y-2">
          {loading && (
            <div className={`p-4 text-center ${
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            }`}>
              Loading todos...
            </div>
          )}

          {error && (
            <div className="text-red-500 p-2 bg-red-100 rounded">
              Error: {error}
            </div>
          )}

          {filteredTodos.length === 0 ? (
            <p className={`p-4 text-center ${
              theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
            }`}>
              {filter === 'completed'
                ? 'No completed tasks yet'
                : filter === 'active'
                  ? 'No active tasks'
                  : 'No tasks yet'}
            </p>
          ) : (
            filteredTodos.map((todo) => (
              <div
                key={todo.id}
                className={`p-3 rounded-lg border flex items-start ${
                  theme === 'dark'
                    ? 'border-gray-700 bg-gray-700'
                    : 'border-gray-200 bg-gray-50'
                } ${todo.completed ? 'opacity-75' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={todo.completed}
                  onChange={() => handleToggleTodo(todo.id)}
                  className="mt-1 mr-2"
                  aria-label={`Mark "${todo.title}" as ${todo.completed ? 'incomplete' : 'complete'}`}
                />

                <div className="flex-1">
                  <div className="flex justify-between">
                    <span className={`${todo.completed ? 'line-through' : ''}`}>
                      {todo.title}
                    </span>

                    <div className="flex space-x-2">
                      <select
                        value={todo.priority}
                        onChange={(e) => handlePriorityChange(todo.id, e.target.value as TodoPriority)}
                        className={`text-xs p-1 rounded ${
                          theme === 'dark'
                            ? 'bg-gray-600 text-white'
                            : 'bg-white text-gray-900'
                        }`}
                        aria-label={`Change priority for "${todo.title}"`}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                      </select>

                      <button
                        onClick={() => handleDeleteTodo(todo.id)}
                        className="text-red-500 hover:text-red-700"
                        aria-label={`Delete "${todo.title}"`}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                          <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  </div>

                  {todo.description && (
                    <p className={`text-sm mt-1 ${
                      theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
                    }`}>
                      {todo.description}
                    </p>
                  )}

                  <p className={`text-xs mt-1 ${
                    theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    Created: {new Date(todo.createdAt).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default TodoPanel;