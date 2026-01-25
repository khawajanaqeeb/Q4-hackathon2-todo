import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { TodoItem, TodoPriority } from '@/types';

interface TodoState {
  todos: Record<string, TodoItem>;
  loading: boolean;
  error: string | null;
  filter: 'all' | 'active' | 'completed';
}

const initialState: TodoState = {
  todos: {},
  loading: false,
  error: null,
  filter: 'all',
};

const todoSlice = createSlice({
  name: 'todo',
  initialState,
  reducers: {
    // Loading and error actions
    setLoading(state, action: PayloadAction<boolean>) {
      state.loading = action.payload;
    },

    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
    },

    // Todo management actions
    addTodo(state, action: PayloadAction<TodoItem>) {
      state.todos[action.payload.id] = action.payload;
    },

    updateTodo(state, action: PayloadAction<TodoItem>) {
      const id = action.payload.id;
      if (state.todos[id]) {
        state.todos[id] = { ...state.todos[id], ...action.payload };
      }
    },

    deleteTodo(state, action: PayloadAction<string>) {
      const id = action.payload;
      delete state.todos[id];
    },

    toggleTodoCompletion(state, action: PayloadAction<string>) {
      const id = action.payload;
      if (state.todos[id]) {
        state.todos[id].completed = !state.todos[id].completed;
        state.todos[id].updatedAt = new Date();
      }
    },

    setTodos(state, action: PayloadAction<TodoItem[]>) {
      state.todos = {};
      action.payload.forEach(todo => {
        state.todos[todo.id] = todo;
      });
    },

    // Filter actions
    setFilter(state, action: PayloadAction<'all' | 'active' | 'completed'>) {
      state.filter = action.payload;
    },

    // Bulk operations
    clearCompleted(state) {
      Object.keys(state.todos).forEach(id => {
        if (state.todos[id].completed) {
          delete state.todos[id];
        }
      });
    },

    // Reset state
    resetTodoState(state) {
      state.todos = {};
      state.loading = false;
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setError,
  addTodo,
  updateTodo,
  deleteTodo,
  toggleTodoCompletion,
  setTodos,
  setFilter,
  clearCompleted,
  resetTodoState,
} = todoSlice.actions;

export default todoSlice.reducer;