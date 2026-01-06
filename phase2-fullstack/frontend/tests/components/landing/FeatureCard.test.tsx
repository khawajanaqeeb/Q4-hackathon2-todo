import React from 'react';
import { render, screen } from '@testing-library/react';
import { FeatureCard } from '@/components/landing/FeatureCard';

describe('FeatureCard Component', () => {
  const mockIcon = <div data-testid="mock-icon">🚀</div>;

  it('renders icon, title, and description', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Premium Features"
        description="Access to advanced productivity tools and analytics"
      />
    );

    expect(screen.getByTestId('mock-icon')).toBeInTheDocument();
    expect(screen.getByText(/premium features/i)).toBeInTheDocument();
    expect(screen.getByText(/advanced productivity tools/i)).toBeInTheDocument();
  });

  it('applies proper styling for icon container', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Test Feature"
        description="Test description"
      />
    );

    const iconContainer = screen.getByTestId('mock-icon').closest('div');
    expect(iconContainer).toHaveClass('w-12', 'h-12', 'flex', 'items-center', 'justify-center', 'rounded-lg', 'bg-accent-500/10', 'text-accent-500', 'mb-4');
  });

  it('applies proper typography classes', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Typography Test"
        description="Test description for typography"
      />
    );

    const title = screen.getByText(/typography test/i);
    const description = screen.getByText(/test description for typography/i);

    expect(title).toHaveClass('text-xl', 'font-semibold', 'text-neutral-100', 'mb-2');
    expect(description).toHaveClass('text-neutral-400');
  });

  it('adds hover effects when wrapped in a group', () => {
    render(
      <div className="group">
        <FeatureCard
          icon={mockIcon}
          title="Hover Test"
          description="Test hover effects"
        />
      </div>
    );

    const cardContainer = screen.getByText(/hover test/i).closest('div');
    expect(cardContainer).toHaveClass('group'); // Parent has group class for hover effects
  });

  it('applies custom className', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Custom Class"
        description="Test custom class"
        className="custom-feature-card"
      />
    );

    const card = screen.getByText(/custom class/i).closest('div');
    expect(card).toHaveClass('custom-feature-card');
  });

  it('renders with proper card styling', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Card Style Test"
        description="Test card styling"
      />
    );

    const cardContainer = screen.getByText(/card style test/i).closest('div');
    expect(cardContainer).toHaveClass('p-6', 'rounded-xl', 'border', 'bg-neutral-800/50', 'border-neutral-700');
  });

  it('renders with flex layout for content', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Layout Test"
        description="Test layout structure"
      />
    );

    const contentContainer = screen.getByText(/layout test/i).closest('div');
    const childDiv = contentContainer?.querySelector(':scope > div:nth-child(2)');
    expect(childDiv).toHaveClass('flex', 'flex-col', 'items-center', 'text-center');
  });

  it('handles long titles and descriptions gracefully', () => {
    const longTitle = 'This is a very long feature title that should wrap properly without breaking the layout';
    const longDescription = 'This is a lengthy description that explains the feature in detail with comprehensive information that might wrap to multiple lines';

    render(
      <FeatureCard
        icon={mockIcon}
        title={longTitle}
        description={longDescription}
      />
    );

    expect(screen.getByText(longTitle)).toBeInTheDocument();
    expect(screen.getByText(longDescription)).toBeInTheDocument();
  });

  it('maintains proper spacing between elements', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Spacing Test"
        description="Verify proper spacing"
      />
    );

    const iconContainer = screen.getByTestId('mock-icon').closest('div');
    const title = screen.getByText(/spacing test/i);

    // Check that icon container has mb-4 class for spacing below icon
    expect(iconContainer).toHaveClass('mb-4');
    // Check that title has mb-2 class for spacing below title
    expect(title).toHaveClass('mb-2');
  });

  it('passes additional props to container', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Props Test"
        description="Test additional props"
        data-testid="feature-card-test"
        aria-label="Test feature card"
      />
    );

    const card = screen.getByTestId('feature-card-test');
    expect(card).toHaveAttribute('aria-label', 'Test feature card');
  });

  it('renders with consistent icon styling regardless of icon type', () => {
    const differentIcon = <div data-testid="different-icon">💡</div>;

    render(
      <FeatureCard
        icon={differentIcon}
        title="Icon Test"
        description="Test different icons"
      />
    );

    const iconContainer = screen.getByTestId('different-icon').closest('div');
    expect(iconContainer).toHaveClass('w-12', 'h-12', 'flex', 'items-center', 'justify-center', 'rounded-lg', 'bg-accent-500/10', 'text-accent-500', 'mb-4');
  });

  it('uses semantic HTML structure', () => {
    render(
      <FeatureCard
        icon={mockIcon}
        title="Semantic Test"
        description="Test semantic structure"
      />
    );

    const title = screen.getByText(/semantic test/i);
    expect(title.tagName).toBe('H3'); // Should use heading for proper semantic structure

    const cardContainer = screen.getByText(/semantic test/i).closest('div');
    expect(cardContainer?.tagName).toBe('DIV'); // Container should be a div
  });
});