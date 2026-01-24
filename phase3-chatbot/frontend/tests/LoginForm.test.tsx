/**
 * Tests for LoginForm component
 *
 * Verifies:
 * - Form rendering with email and password fields
 * - Validation (email format, required fields)
 * - Submit handler called with correct data
 * - Error message display
 * - Loading state
 * - Link to registration page
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from '../components/auth/LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form with all fields', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    expect(screen.getByRole('heading', { name: /sign in to your account/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows link to registration page', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    const registerLink = screen.getByRole('link', { name: /create a new account/i });
    expect(registerLink).toBeInTheDocument();
    expect(registerLink).toHaveAttribute('href', '/register');
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    // Enter invalid email
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('requires password field', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    // Enter email but no password
    await user.type(emailInput, 'test@example.com');
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('submits form with valid credentials', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(<LoginForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    // Enter valid credentials
    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'SecurePass123!');
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'SecurePass123!',
      });
    });
  });

  it('displays error message when provided', () => {
    const errorMessage = 'Invalid credentials';
    render(<LoginForm onSubmit={mockOnSubmit} error={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<LoginForm onSubmit={mockOnSubmit} loading={true} />);

    const submitButton = screen.getByRole('button', { name: /signing in/i });
    expect(submitButton).toBeDisabled();
  });

  it('disables form during submission', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 1000)));

    render(<LoginForm onSubmit={mockOnSubmit} />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /sign in/i });

    await user.type(emailInput, 'test@example.com');
    await user.type(passwordInput, 'SecurePass123!');
    await user.click(submitButton);

    // Button should be disabled during submission
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });
});
