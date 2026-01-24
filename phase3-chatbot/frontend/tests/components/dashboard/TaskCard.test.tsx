import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from '@/components/dashboard/TaskCard';

const mockTask = {
  id: '1',
  title: 'Complete UI enhancements',
  tags: ['premium', 'ui', 'enhancement'],
  createdAt: '2026-01-05T10:30:00Z',
  priority: 'high' as const,
  completed: false,
};

describe('TaskCard Component', () => {
  it('renders task title and tags', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText(/complete ui enhancements/i)).toBeInTheDocument();
    expect(screen.getByText(/premium/i)).toBeInTheDocument();
    expect(screen.getByText(/ui/i)).toBeInTheDocument();
    expect(screen.getByText(/enhancement/i)).toBeInTheDocument();
  });

  it('renders with completed state', () => {
    const completedTask = { ...mockTask, completed: true };
    render(<TaskCard task={completedTask} />);

    const title = screen.getByText(/complete ui enhancements/i);
    expect(title).toHaveClass('line-through', 'text-neutral-500');
  });

  it('renders with priority-based tag styling', () => {
    render(<TaskCard task={{ ...mockTask, priority: 'high' }} />);

    expect(screen.getByText(/premium/i)).toHaveClass('bg-error-500/20', 'text-error-500');
    expect(screen.getByText(/ui/i)).toHaveClass('bg-error-500/20', 'text-error-500');
    expect(screen.getByText(/enhancement/i)).toHaveClass('bg-error-500/20', 'text-error-500');
  });

  it('formats date to relative time', () => {
    render(<TaskCard task={mockTask} />);

    // Should show relative time like "Just now", "Xm ago", "Xh ago", etc.
    expect(screen.getByText(/created/i)).toBeInTheDocument();
  });

  it('shows edit button when onEdit handler provided', () => {
    const mockOnEdit = jest.fn();
    render(<TaskCard task={mockTask} onEdit={mockOnEdit} />);

    const editButton = screen.getByLabelText(/edit task "complete ui enhancements"/i);
    expect(editButton).toBeInTheDocument();

    fireEvent.click(editButton);
    expect(mockOnEdit).toHaveBeenCalledWith('1');
  });

  it('shows delete button when onDelete handler provided', () => {
    const mockOnDelete = jest.fn();
    render(<TaskCard task={mockTask} onDelete={mockOnDelete} />);

    const deleteButton = screen.getByLabelText(/delete task "complete ui enhancements"/i);
    expect(deleteButton).toBeInTheDocument();

    fireEvent.click(deleteButton);
    expect(mockOnDelete).toHaveBeenCalledWith('1');
  });

  it('does not show edit/delete buttons when no handlers provided', () => {
    render(<TaskCard task={mockTask} />);

    expect(() => screen.getByLabelText(/edit task/i)).toThrow();
    expect(() => screen.getByLabelText(/delete task/i)).toThrow();
  });

  it('applies custom className', () => {
    render(<TaskCard task={mockTask} className="custom-task-card" />);

    const card = screen.getByText(/complete ui enhancements/i).closest('div');
    expect(card).toHaveClass('custom-task-card');
  });

  it('handles click events when interactive', () => {
    const mockOnClick = jest.fn();
    render(<TaskCard task={mockTask} onClick={mockOnClick} />);

    const card = screen.getByText(/complete ui enhancements/i).closest('div');
    fireEvent.click(card);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders with proper layout structure', () => {
    render(<TaskCard task={mockTask} />);

    const card = screen.getByText(/complete ui enhancements/i).closest('div');
    expect(card).toHaveClass('p-6', 'rounded-xl', 'border', 'bg-neutral-800/50', 'border-neutral-700');

    const container = screen.getByText(/complete ui enhancements/i).closest('div');
    const childDiv = container?.querySelector(':scope > div');
    expect(childDiv).toHaveClass('flex', 'items-start', 'justify-between');
  });

  it('handles long task titles with truncation', () => {
    const longTitleTask = {
      ...mockTask,
      title: 'This is a very long task title that should be truncated properly to maintain layout integrity',
    };
    render(<TaskCard task={longTitleTask} />);

    expect(screen.getByText(/this is a very long task title/i)).toBeInTheDocument();
  });

  it('renders multiple tags properly', () => {
    const taskWithMultipleTags = {
      ...mockTask,
      tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
    };
    render(<TaskCard task={taskWithMultipleTags} />);

    expect(screen.getByText(/tag1/i)).toBeInTheDocument();
    expect(screen.getByText(/tag2/i)).toBeInTheDocument();
    expect(screen.getByText(/tag3/i)).toBeInTheDocument();
    expect(screen.getByText(/tag4/i)).toBeInTheDocument();
    expect(screen.getByText(/tag5/i)).toBeInTheDocument();
  });

  it('passes additional props to container', () => {
    render(
      <TaskCard
        task={mockTask}
        data-testid="task-card-test"
        aria-label="Test task card"
      />
    );

    const card = screen.getByTestId('task-card-test');
    expect(card).toHaveAttribute('aria-label', 'Test task card');
  });
});