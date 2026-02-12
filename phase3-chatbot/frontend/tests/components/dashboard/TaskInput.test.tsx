import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskInput } from '@/components/dashboard/TaskInput';

describe('TaskInput Component', () => {
  it('renders with input field and priority/classification controls', () => {
    render(<TaskInput onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/what's the next milestone\?/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/classification/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument();
  });

  it('calls onSubmit when form is submitted', () => {
    const mockOnSubmit = jest.fn();
    render(<TaskInput onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'New task' } });

    const addButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(addButton);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'New task',
      priority: 'medium', // default value
      classification: '', // default value
    });
  });

  it('updates state when input values change', () => {
    render(<TaskInput onSubmit={jest.fn()} />);

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'Updated task title' } });
    expect(input).toHaveValue('Updated task title');

    const prioritySelect = screen.getByLabelText(/priority/i);
    fireEvent.change(prioritySelect, { target: { value: 'high' } });
    expect(prioritySelect).toHaveValue('high');

    const classificationInput = screen.getByLabelText(/classification/i);
    fireEvent.change(classificationInput, { target: { value: 'Work' } });
    expect(classificationInput).toHaveValue('Work');
  });

  it('shows loading state with spinner when loading prop is true', () => {
    render(<TaskInput onSubmit={jest.fn()} loading={true} />);

    const submitButton = screen.getByRole('button', { name: /add task/i });
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/creating\.\.\./i)).toBeInTheDocument();
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument(); // Spinner
  });

  it('disables submit button when input is empty', () => {
    render(<TaskInput onSubmit={jest.fn()} />);

    const submitButton = screen.getByRole('button', { name: /add task/i });
    expect(submitButton).toBeDisabled();

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'Non-empty task' } });

    expect(submitButton).not.toBeDisabled();
  });

  it('resets form after successful submission', () => {
    const mockOnSubmit = jest.fn();
    render(<TaskInput onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'New task' } });

    const prioritySelect = screen.getByLabelText(/priority/i);
    fireEvent.change(prioritySelect, { target: { value: 'high' } });

    const classificationInput = screen.getByLabelText(/classification/i);
    fireEvent.change(classificationInput, { target: { value: 'Urgent' } });

    const addButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(addButton);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'New task',
      priority: 'high',
      classification: 'Urgent',
    });

    // After submission, the form should be reset
    expect(input).toHaveValue('');
    expect(prioritySelect).toHaveValue('medium'); // Reset to default
    expect(classificationInput).toHaveValue(''); // Reset to default
  });

  it('applies custom className', () => {
    render(<TaskInput onSubmit={jest.fn()} className="custom-task-input" />);

    const container = screen.getByText(/what's the next milestone\?/i).closest('div');
    expect(container).toHaveClass('custom-task-input');
  });

  it('handles form submission with Enter key', () => {
    const mockOnSubmit = jest.fn();
    render(<TaskInput onSubmit={mockOnSubmit} />);

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'Task with enter' } });

    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', char: '\r' });

    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'Task with enter',
      priority: 'medium',
      classification: '',
    });
  });

  it('renders with proper form structure', () => {
    render(<TaskInput onSubmit={jest.fn()} />);

    const container = screen.getByText(/what's the next milestone\?/i).closest('div');
    expect(container).toHaveClass('p-6', 'rounded-xl', 'border', 'bg-neutral-800/50', 'border-neutral-700');

    const form = screen.getByRole('form');
    expect(form).toBeInTheDocument();
    expect(form).toHaveClass('space-y-4');
  });

  it('displays proper accessibility attributes', () => {
    render(<TaskInput onSubmit={jest.fn()} />);

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    expect(input).toHaveAttribute('type', 'text');
    expect(input).toHaveAttribute('placeholder', 'Enter the next milestone...');

    const prioritySelect = screen.getByLabelText(/priority/i);
    expect(prioritySelect).toHaveAttribute('id', expect.stringContaining('task-priority'));

    const classificationInput = screen.getByLabelText(/classification/i);
    expect(classificationInput).toHaveAttribute('id', expect.stringContaining('task-classification'));
  });

  it('handles different priority selections', () => {
    const mockOnSubmit = jest.fn();
    render(<TaskInput onSubmit={mockOnSubmit} />);

    const prioritySelect = screen.getByLabelText(/priority/i);
    fireEvent.change(prioritySelect, { target: { value: 'low' } });

    const input = screen.getByLabelText(/what's the next milestone\?/i);
    fireEvent.change(input, { target: { value: 'Low priority task' } });

    const addButton = screen.getByRole('button', { name: /add task/i });
    fireEvent.click(addButton);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'Low priority task',
      priority: 'low',
      classification: '',
    });
  });

  it('passes additional props to container', () => {
    render(
      <TaskInput
        onSubmit={jest.fn()}
        data-testid="task-input-test"
        aria-label="Test task input form"
      />
    );

    const container = screen.getByTestId('task-input-test');
    expect(container).toHaveAttribute('aria-label', 'Test task input form');
  });
});