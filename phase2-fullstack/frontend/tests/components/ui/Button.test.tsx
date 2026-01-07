import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button Component', () => {
  it('renders with default variant and size', () => {
    render(<Button>Click me</Button>);

    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-primary-500');
    expect(button).toHaveClass('h-10'); // md size
  });

  it('renders with different variants', () => {
    render(
      <>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="ghost">Ghost</Button>
      </>
    );

    expect(screen.getByRole('button', { name: /secondary/i })).toHaveClass('bg-neutral-700');
    expect(screen.getByRole('button', { name: /outline/i })).toHaveClass('border', 'border-primary-500');
    expect(screen.getByRole('button', { name: /ghost/i })).toHaveClass('bg-transparent');
  });

  it('renders with different sizes', () => {
    render(
      <>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
      </>
    );

    expect(screen.getByRole('button', { name: /small/i })).toHaveClass('h-8');
    expect(screen.getByRole('button', { name: /large/i })).toHaveClass('h-12');
  });

  it('disables the button when disabled prop is true', () => {
    render(<Button disabled>Disabled button</Button>);

    const button = screen.getByRole('button', { name: /disabled button/i });
    expect(button).toBeDisabled();
    expect(button).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('shows loading state with spinner', () => {
    render(<Button loading>Loading button</Button>);

    const button = screen.getByRole('button', { name: /loading button/i });
    expect(button).toBeDisabled(); // Loading state should disable the button
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByRole('img', { hidden: true })).toBeInTheDocument(); // Spinner SVG
  });

  it('handles click events', () => {
    const mockOnClick = jest.fn();
    render(<Button onClick={mockOnClick}>Clickable</Button>);

    const button = screen.getByRole('button', { name: /clickable/i });
    fireEvent.click(button);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('applies fullWidth class when specified', () => {
    render(<Button fullWidth>Full width</Button>);

    const button = screen.getByRole('button', { name: /full width/i });
    expect(button).toHaveClass('w-full');
  });

  it('passes additional className prop', () => {
    render(<Button className="custom-class">Custom</Button>);

    const button = screen.getByRole('button', { name: /custom/i });
    expect(button).toHaveClass('custom-class');
  });

  it('respects type attribute', () => {
    render(
      <>
        <Button type="submit">Submit</Button>
        <Button type="reset">Reset</Button>
      </>
    );

    expect(screen.getByRole('button', { name: /submit/i })).toHaveAttribute('type', 'submit');
    expect(screen.getByRole('button', { name: /reset/i })).toHaveAttribute('type', 'reset');
  });
});