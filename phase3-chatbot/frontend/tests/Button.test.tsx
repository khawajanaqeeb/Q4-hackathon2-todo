/**
 * Tests for Button UI component
 *
 * Verifies:
 * - Button rendering with text/children
 * - Click handler
 * - Disabled state
 * - Loading state
 * - Variant styles (primary, secondary, danger)
 * - Size options
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Button from '../components/ui/Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);

    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const mockOnClick = jest.fn();

    render(<Button onClick={mockOnClick}>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    await user.click(button);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup();
    const mockOnClick = jest.fn();

    render(<Button onClick={mockOnClick} disabled={true}>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    await user.click(button);

    expect(mockOnClick).not.toHaveBeenCalled();
    expect(button).toBeDisabled();
  });

  it('shows loading state', () => {
    render(<Button loading={true}>Submit</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent(/loading|submitting/i);
  });

  it('applies primary variant styles by default', () => {
    render(<Button>Primary</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-blue-600');
  });

  it('applies secondary variant styles', () => {
    render(<Button variant="secondary">Secondary</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-gray-200');
  });

  it('applies danger variant styles', () => {
    render(<Button variant="danger">Delete</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-red-600');
  });

  it('supports different sizes', () => {
    const { rerender } = render(<Button size="small">Small</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-sm');

    rerender(<Button size="medium">Medium</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-base');

    rerender(<Button size="large">Large</Button>);
    expect(screen.getByRole('button')).toHaveClass('text-lg');
  });

  it('accepts custom className', () => {
    render(<Button className="custom-class">Button</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('custom-class');
  });

  it('supports button types', () => {
    render(<Button type="submit">Submit</Button>);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('type', 'submit');
  });

  it('prevents multiple clicks when loading', async () => {
    const user = userEvent.setup();
    const mockOnClick = jest.fn();

    render(<Button onClick={mockOnClick} loading={true}>Submit</Button>);

    const button = screen.getByRole('button');
    await user.click(button);
    await user.click(button);
    await user.click(button);

    expect(mockOnClick).not.toHaveBeenCalled();
  });
});
