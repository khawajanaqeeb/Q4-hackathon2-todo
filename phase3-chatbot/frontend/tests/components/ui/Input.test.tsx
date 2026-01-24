import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/Input';

describe('Input Component', () => {
  it('renders with label and input field', () => {
    render(<Input label="Email" />);

    const label = screen.getByText(/email/i);
    const input = screen.getByRole('textbox');

    expect(label).toBeInTheDocument();
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('id', 'email');
  });

  it('renders with error message when error prop provided', () => {
    render(<Input label="Password" error="Password is required" />);

    const input = screen.getByRole('textbox');
    const error = screen.getByText(/password is required/i);

    expect(input).toBeInTheDocument();
    expect(error).toBeInTheDocument();
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'password-error');
  });

  it('renders with required asterisk when required prop is true', () => {
    render(<Input label="Username" required />);

    const label = screen.getByText(/username/i);
    const requiredAsterisk = screen.getByText('*', { selector: 'span' });

    expect(label).toBeInTheDocument();
    expect(requiredAsterisk).toBeInTheDocument();
    expect(requiredAsterisk).toHaveClass('text-error-500');
  });

  it('applies disabled state correctly', () => {
    render(<Input label="Disabled" disabled />);

    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('bg-neutral-900', 'text-neutral-600', 'cursor-not-allowed');
  });

  it('handles value changes', () => {
    const mockOnChange = jest.fn();
    render(<Input label="Name" value="" onChange={mockOnChange} />);

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'John Doe' } });

    expect(mockOnChange).toHaveBeenCalledTimes(1);
    expect(input).toHaveValue('John Doe');
  });

  it('generates correct ID when none provided', () => {
    render(<Input label="Full Name" />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('id', 'full-name');
  });

  it('uses provided ID when specified', () => {
    render(<Input label="Email" id="custom-email-id" />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('id', 'custom-email-id');
  });

  it('passes additional props to input element', () => {
    render(<Input label="Phone" placeholder="Enter phone number" maxLength={10} />);

    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('placeholder', 'Enter phone number');
    expect(input).toHaveAttribute('maxLength', '10');
  });

  it('renders with different types', () => {
    render(<Input label="Date" type="date" />);

    const input = screen.getByRole('textbox'); // Date inputs are still textbox role
    expect(input).toHaveAttribute('type', 'date');
  });

  it('applies custom className', () => {
    render(<Input label="Custom" className="custom-input-class" />);

    const input = screen.getByRole('textbox');
    expect(input.parentElement).toHaveClass('custom-input-class');
  });
});