/**
 * Tests for TodoTable component
 *
 * Verifies:
 * - Table rendering with todos
 * - Empty state display
 * - Action buttons (toggle, edit, delete)
 * - Priority display with colors
 * - Tags display
 * - Completion status indicator
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TodoTable from '../components/todos/TodoTable';
import { Todo } from '../types/todo';

describe('TodoTable', () => {
  const mockOnToggle = jest.fn();
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockTodos: Todo[] = [
    {
      id: 1,
      title: 'Buy groceries',
      description: 'Milk, eggs, bread',
      priority: 'high',
      completed: false,
      tags: ['shopping', 'urgent'],
      user_id: 1,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    {
      id: 2,
      title: 'Complete project',
      description: 'Finish the todo app',
      priority: 'medium',
      completed: true,
      tags: ['work'],
      user_id: 1,
      created_at: '2026-01-02T00:00:00Z',
      updated_at: '2026-01-02T00:00:00Z',
    },
    {
      id: 3,
      title: 'Call dentist',
      description: null,
      priority: 'low',
      completed: false,
      tags: [],
      user_id: 1,
      created_at: '2026-01-03T00:00:00Z',
      updated_at: '2026-01-03T00:00:00Z',
    },
  ];

  it('renders table with todos', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Buy groceries')).toBeInTheDocument();
    expect(screen.getByText('Complete project')).toBeInTheDocument();
    expect(screen.getByText('Call dentist')).toBeInTheDocument();
  });

  it('displays empty state when no todos', () => {
    render(
      <TodoTable
        todos={[]}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/no tasks found/i)).toBeInTheDocument();
  });

  it('shows task descriptions when provided', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('Milk, eggs, bread')).toBeInTheDocument();
    expect(screen.getByText('Finish the todo app')).toBeInTheDocument();
  });

  it('displays priority badges', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText(/high/i)).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/low/i)).toBeInTheDocument();
  });

  it('displays tags when provided', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    expect(screen.getByText('shopping')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
    expect(screen.getByText('work')).toBeInTheDocument();
  });

  it('calls onToggle when toggle button clicked', async () => {
    const user = userEvent.setup();
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const toggleButtons = screen.getAllByRole('button', { name: /toggle/i });
    await user.click(toggleButtons[0]);

    expect(mockOnToggle).toHaveBeenCalledWith(1);
  });

  it('calls onEdit when edit button clicked', async () => {
    const user = userEvent.setup();
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    await user.click(editButtons[0]);

    expect(mockOnEdit).toHaveBeenCalledWith(mockTodos[0]);
  });

  it('calls onDelete when delete button clicked', async () => {
    const user = userEvent.setup();
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    await user.click(deleteButtons[0]);

    expect(mockOnDelete).toHaveBeenCalledWith(1);
  });

  it('shows completed todos with strikethrough', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const completedTask = screen.getByText('Complete project');
    expect(completedTask).toHaveClass('line-through');
  });

  it('renders correct number of rows', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const rows = screen.getAllByRole('row');
    // Header row + 3 data rows
    expect(rows).toHaveLength(4);
  });

  it('has action buttons for each todo', () => {
    render(
      <TodoTable
        todos={mockTodos}
        onToggle={mockOnToggle}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );

    const toggleButtons = screen.getAllByRole('button', { name: /toggle/i });
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });

    expect(toggleButtons).toHaveLength(3);
    expect(editButtons).toHaveLength(3);
    expect(deleteButtons).toHaveLength(3);
  });
});
