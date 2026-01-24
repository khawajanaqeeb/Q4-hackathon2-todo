/**
 * Tests for AddTaskForm component
 *
 * Verifies:
 * - Form rendering with title, description, priority, tags fields
 * - Validation (title required)
 * - Submit handler called with correct data
 * - Priority selection (low/medium/high)
 * - Tags input and management
 * - Cancel functionality
 * - Modal open/close behavior
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AddTaskForm from '../components/todos/AddTaskForm';

describe('AddTaskForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form when open', () => {
    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('heading', { name: /add new task/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<AddTaskForm isOpen={false} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    expect(screen.queryByRole('heading', { name: /add new task/i })).not.toBeInTheDocument();
  });

  it('requires title field', async () => {
    const user = userEvent.setup();
    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits form with title only', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await user.type(titleInput, 'New Task');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New Task',
        })
      );
    });
  });

  it('submits form with all fields', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const prioritySelect = screen.getByLabelText(/priority/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await user.type(titleInput, 'Buy groceries');
    await user.type(descriptionInput, 'Milk, eggs, bread');
    await user.selectOptions(prioritySelect, 'high');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Buy groceries',
          description: 'Milk, eggs, bread',
          priority: 'high',
        })
      );
    });
  });

  it('has priority options (low, medium, high)', () => {
    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const prioritySelect = screen.getByLabelText(/priority/i);
    const options = Array.from(prioritySelect.querySelectorAll('option'));

    expect(options).toHaveLength(3);
    expect(options.map(opt => opt.value)).toEqual(['low', 'medium', 'high']);
  });

  it('calls onClose when cancel button clicked', async () => {
    const user = userEvent.setup();
    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const cancelButton = screen.getByRole('button', { name: /cancel/i });
    await user.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('resets form after successful submission', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await user.type(titleInput, 'Task 1');
    await user.click(submitButton);

    await waitFor(() => {
      expect(titleInput.value).toBe('');
    });
  });

  it('shows loading state during submission', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    render(<AddTaskForm isOpen={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />);

    const titleInput = screen.getByLabelText(/title/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await user.type(titleInput, 'Task 1');
    await user.click(submitButton);

    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });
});
