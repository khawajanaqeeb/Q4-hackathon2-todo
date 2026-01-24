import React from 'react';
import { render, screen } from '@testing-library/react';
import { StatsCard } from '@/components/dashboard/StatsCard';

describe('StatsCard Component', () => {
  it('renders with label and value', () => {
    render(<StatsCard label="Total Tasks" value={42} />);

    expect(screen.getByText(/total tasks/i)).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders with icon when provided', () => {
    const mockIcon = <div data-testid="mock-icon">📊</div>;
    render(<StatsCard label="Completed" value={24} icon={mockIcon} />);

    const icon = screen.getByTestId('mock-icon');
    expect(icon).toBeInTheDocument();
    expect(icon).toHaveTextContent('📊');
  });

  it('renders with different variants', () => {
    render(
      <>
        <StatsCard label="Default" value={10} variant="default" />
        <StatsCard label="Primary" value={20} variant="primary" />
        <StatsCard label="Success" value={30} variant="success" />
        <StatsCard label="Warning" value={40} variant="warning" />
        <StatsCard label="Error" value={50} variant="error" />
      </>
    );

    expect(screen.getByText(/default/i).closest('div')).toHaveClass('bg-neutral-800/50', 'border', 'border-neutral-700');
    expect(screen.getByText(/primary/i).closest('div')).toHaveClass('bg-primary-500/10', 'border', 'border-primary-500/30');
    expect(screen.getByText(/success/i).closest('div')).toHaveClass('bg-success-500/10', 'border', 'border-success-500/30');
    expect(screen.getByText(/warning/i).closest('div')).toHaveClass('bg-warning-500/10', 'border', 'border-warning-500/30');
    expect(screen.getByText(/error/i).closest('div')).toHaveClass('bg-error-500/10', 'border', 'border-error-500/30');
  });

  it('renders different value types (number and string)', () => {
    render(
      <>
        <StatsCard label="Count" value={123} />
        <StatsCard label="Status" value="Active" />
      </>
    );

    expect(screen.getByText('123')).toBeInTheDocument();
    expect(screen.getByText(/active/i)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<StatsCard label="Custom" value={5} className="custom-stats-class" />);

    const card = screen.getByText(/custom/i).closest('div');
    expect(card).toHaveClass('custom-stats-class');
  });

  it('renders with proper typography classes', () => {
    render(<StatsCard label="Tasks" value={7} />);

    const label = screen.getByText(/tasks/i);
    const value = screen.getByText('7');

    expect(label).toHaveClass('text-sm', 'font-medium', 'text-neutral-400');
    expect(value).toHaveClass('text-3xl', 'font-bold', 'text-neutral-100');
  });

  it('renders icon in correct position with proper styling', () => {
    const mockIcon = <div data-testid="stats-icon">📈</div>;
    render(<StatsCard label="Growth" value={15} icon={mockIcon} />);

    const iconContainer = screen.getByTestId('stats-icon').closest('div');
    expect(iconContainer).toHaveClass('p-3', 'bg-neutral-700/50', 'rounded-lg');
  });

  it('handles large numbers properly', () => {
    render(<StatsCard label="Visitors" value={1234567} />);

    expect(screen.getByText('1234567')).toBeInTheDocument();
  });

  it('renders with proper layout structure', () => {
    render(<StatsCard label="Performance" value={98.5} />);

    const card = screen.getByText(/performance/i).closest('div');
    expect(card).toHaveClass('p-6', 'rounded-xl', 'border', 'transition-all', 'duration-base');

    const container = screen.getByText(/performance/i).closest('div');
    const childDiv = container?.querySelector(':scope > div');
    expect(childDiv).toHaveClass('flex', 'items-center', 'justify-between');
  });

  it('renders with hover effects', () => {
    render(<StatsCard label="Hover Test" value={10} />);

    const card = screen.getByText(/hover test/i).closest('div');
    expect(card).toHaveClass('hover:shadow-md', 'hover:border-neutral-600');
  });

  it('passes additional props to container', () => {
    render(
      <StatsCard
        label="Test Card"
        value={5}
        data-testid="stats-card-test"
        aria-label="Test stats card"
      />
    );

    const card = screen.getByTestId('stats-card-test');
    expect(card).toHaveAttribute('aria-label', 'Test stats card');
  });
});