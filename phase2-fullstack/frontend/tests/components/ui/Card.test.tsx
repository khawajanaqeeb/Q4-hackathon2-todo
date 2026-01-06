import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from '@/components/ui/Card';

describe('Card Component', () => {
  it('renders children correctly', () => {
    render(
      <Card>
        <h1>Test Card Content</h1>
      </Card>
    );

    expect(screen.getByText(/test card content/i)).toBeInTheDocument();
  });

  it('renders with default variant and padding', () => {
    render(<Card>Default card</Card>);

    const card = screen.getByText(/default card/i).closest('div');
    expect(card).toHaveClass('bg-neutral-800', 'border', 'border-neutral-700');
    expect(card).toHaveClass('p-6'); // Default padding
  });

  it('renders with different variants', () => {
    render(
      <>
        <Card variant="elevated">Elevated card</Card>
        <Card variant="interactive">Interactive card</Card>
      </>
    );

    const elevatedCard = screen.getByText(/elevated card/i).closest('div');
    const interactiveCard = screen.getByText(/interactive card/i).closest('div');

    expect(elevatedCard).toHaveClass('shadow-md', 'hover:shadow-lg');
    expect(interactiveCard).toHaveClass('shadow-md', 'hover:shadow-lg', 'cursor-pointer', 'hover:bg-neutral-700/50');
  });

  it('renders with different padding sizes', () => {
    render(
      <>
        <Card padding="sm">Small card</Card>
        <Card padding="lg">Large card</Card>
      </>
    );

    const smallCard = screen.getByText(/small card/i).closest('div');
    const largeCard = screen.getByText(/large card/i).closest('div');

    expect(smallCard).toHaveClass('p-4'); // sm padding
    expect(largeCard).toHaveClass('p-8'); // lg padding
  });

  it('applies custom className', () => {
    render(<Card className="custom-card-class">Custom card</Card>);

    const card = screen.getByText(/custom card/i).closest('div');
    expect(card).toHaveClass('custom-card-class');
  });

  it('handles click events when interactive', () => {
    const mockOnClick = jest.fn();
    render(
      <Card variant="interactive" onClick={mockOnClick}>
        Clickable card
      </Card>
    );

    const card = screen.getByText(/clickable card/i).closest('div');
    expect(card).toHaveClass('cursor-pointer');
  });

  it('renders with focus states', () => {
    render(<Card>Focusable card</Card>);

    const card = screen.getByText(/focusable card/i).closest('div');
    expect(card).toHaveClass('focus:outline-none', 'focus:ring-2', 'focus:ring-accent-500', 'focus:ring-offset-2', 'focus:ring-offset-neutral-900');
  });

  it('passes additional props', () => {
    render(
      <Card data-testid="test-card" aria-label="test card">
        Test card
      </Card>
    );

    const card = screen.getByTestId('test-card');
    expect(card).toHaveAttribute('aria-label', 'test card');
  });

  it('maintains proper border-radius and transition classes', () => {
    render(<Card>Styled card</Card>);

    const card = screen.getByText(/styled card/i).closest('div');
    expect(card).toHaveClass('rounded-xl', 'transition-all', 'duration-base');
  });

  it('allows variant and padding combination', () => {
    render(
      <Card variant="elevated" padding="sm">
        Elevated small card
      </Card>
    );

    const card = screen.getByText(/elevated small card/i).closest('div');
    expect(card).toHaveClass('bg-neutral-800', 'border', 'border-neutral-700', 'shadow-md', 'hover:shadow-lg', 'p-4');
  });

  it('renders without padding prop when using default', () => {
    render(<Card>Default padding card</Card>);

    const card = screen.getByText(/default padding card/i).closest('div');
    expect(card).toHaveClass('p-6'); // Default padding
  });
});