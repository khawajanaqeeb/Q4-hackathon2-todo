import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Select } from '@/components/ui/Select';

const mockOptions = [
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

describe('Select Component', () => {
  it('renders with label and placeholder', () => {
    render(<Select label="Priority" options={mockOptions} placeholder="Select priority..." />);

    const label = screen.getByText(/priority/i);
    const placeholder = screen.getByText(/select priority\.\.\./i);

    expect(label).toBeInTheDocument();
    expect(placeholder).toBeInTheDocument();
  });

  it('renders with selected value', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        value="high"
        onChange={jest.fn()}
      />
    );

    expect(screen.getByText(/high/i)).toBeInTheDocument();
  });

  it('opens dropdown when clicked', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.click(selectButton);

    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getByText(/high/i)).toBeInTheDocument();
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    expect(screen.getByText(/low/i)).toBeInTheDocument();
  });

  it('calls onChange when option is selected', async () => {
    const mockOnChange = jest.fn();
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={mockOnChange}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.click(selectButton);

    const option = screen.getByText(/medium/i);
    fireEvent.click(option);

    await waitFor(() => {
      expect(mockOnChange).toHaveBeenCalledWith('medium');
    });
  });

  it('closes dropdown when clicking outside', () => {
    render(
      <>
        <Select
          label="Priority"
          options={mockOptions}
          onChange={jest.fn()}
        />
        <button>Outside button</button>
      </>
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.click(selectButton);

    expect(screen.getByRole('listbox')).toBeInTheDocument();

    const outsideButton = screen.getByRole('button', { name: /outside/i });
    fireEvent.click(outsideButton);

    expect(() => screen.getByRole('listbox')).toThrow();
  });

  it('disables dropdown when disabled prop is true', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        disabled
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    expect(selectButton).toBeDisabled();
    expect(selectButton).toHaveClass('bg-neutral-900', 'text-neutral-600', 'cursor-not-allowed');

    fireEvent.click(selectButton);
    expect(() => screen.getByRole('listbox')).toThrow();
  });

  it('renders with proper accessibility attributes', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        value="high"
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    expect(selectButton).toHaveAttribute('aria-haspopup', 'listbox');
    expect(selectButton).toHaveAttribute('aria-expanded', 'false');
    expect(selectButton).toHaveAttribute('id', expect.stringContaining('priority'));

    // When opened, aria-expanded should be true
    fireEvent.click(selectButton);
    expect(selectButton).toHaveAttribute('aria-expanded', 'true');
  });

  it('shows proper focus states', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    selectButton.focus();

    expect(selectButton).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-accent-500', 'focus:border-accent-500');
  });

  it('handles keyboard navigation', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.focus(selectButton);
    fireEvent.keyDown(selectButton, { key: 'ArrowDown' });

    // After pressing arrow down, dropdown should open
    expect(screen.getByRole('listbox')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={jest.fn()}
        className="custom-select-class"
      />
    );

    const selectContainer = screen.getByText(/select/i).closest('div');
    expect(selectContainer).toHaveClass('custom-select-class');
  });

  it('renders dropdown options with proper hover states', async () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.click(selectButton);

    const option = screen.getByText(/high/i);
    fireEvent.mouseEnter(option);

    await waitFor(() => {
      expect(option).toHaveClass('bg-neutral-700/50');
    });
  });

  it('shows selected option with different styling', async () => {
    render(
      <Select
        label="Priority"
        options={mockOptions}
        value="medium"
        onChange={jest.fn()}
      />
    );

    const selectButton = screen.getByRole('button', { name: /select/i });
    fireEvent.click(selectButton);

    const selectedOption = screen.getByText(/medium/i);
    await waitFor(() => {
      expect(selectedOption).toHaveClass('bg-neutral-700/30');
    });
  });
});