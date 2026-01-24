import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Hero } from '@/components/landing/Hero';

describe('Hero Component', () => {
  it('renders headline and subheadline', () => {
    render(
      <Hero
        headline="Premium Task Management"
        subheadline="Enhanced productivity with elegant design"
        primaryCTA="Get Started Free"
        onPrimaryCTA={jest.fn()}
      />
    );

    expect(screen.getByText(/premium task management/i)).toBeInTheDocument();
    expect(screen.getByText(/enhanced productivity/i)).toBeInTheDocument();
  });

  it('renders primary CTA button', () => {
    const mockOnPrimaryCTA = jest.fn();
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Primary Action"
        onPrimaryCTA={mockOnPrimaryCTA}
      />
    );

    const primaryButton = screen.getByRole('button', { name: /primary action/i });
    expect(primaryButton).toBeInTheDocument();
    expect(primaryButton).toHaveClass('bg-primary-500', 'text-white', 'hover:bg-primary-600');
  });

  it('renders secondary CTA button when provided', () => {
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Primary"
        onPrimaryCTA={jest.fn()}
        secondaryCTA="Secondary"
        onSecondaryCTA={jest.fn()}
      />
    );

    const secondaryButton = screen.getByRole('button', { name: /secondary/i });
    expect(secondaryButton).toBeInTheDocument();
    expect(secondaryButton).toHaveClass('bg-transparent', 'text-primary-500', 'border', 'border-primary-500');
  });

  it('does not render secondary CTA when not provided', () => {
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Primary"
        onPrimaryCTA={jest.fn()}
      />
    );

    expect(() => screen.getByRole('button', { name: /secondary/i })).toThrow();
  });

  it('calls primary CTA handler when primary button clicked', () => {
    const mockOnPrimaryCTA = jest.fn();
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Click Me"
        onPrimaryCTA={mockOnPrimaryCTA}
      />
    );

    const button = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(button);

    expect(mockOnPrimaryCTA).toHaveBeenCalledTimes(1);
  });

  it('calls secondary CTA handler when secondary button clicked', () => {
    const mockOnSecondaryCTA = jest.fn();
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Primary"
        onPrimaryCTA={jest.fn()}
        secondaryCTA="Secondary"
        onSecondaryCTA={mockOnSecondaryCTA}
      />
    );

    const secondaryButton = screen.getByRole('button', { name: /secondary/i });
    fireEvent.click(secondaryButton);

    expect(mockOnSecondaryCTA).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    render(
      <Hero
        headline="Custom Hero"
        primaryCTA="Action"
        onPrimaryCTA={jest.fn()}
        className="custom-hero-class"
      />
    );

    const container = screen.getByText(/custom hero/i).closest('div');
    expect(container).toHaveClass('custom-hero-class');
  });

  it('renders with proper typography hierarchy', () => {
    render(
      <Hero
        headline="Large Headline"
        subheadline="Smaller subheadline"
        primaryCTA="CTA"
        onPrimaryCTA={jest.fn()}
      />
    );

    const headline = screen.getByText(/large headline/i);
    expect(headline.tagName).toBe('H1');
    expect(headline).toHaveClass('text-4xl', 'md:text-6xl', 'font-bold', 'text-neutral-100');

    const subheadline = screen.getByText(/smaller subheadline/i);
    expect(subheadline).toHaveClass('text-xl', 'text-neutral-400');
  });

  it('centers content with proper spacing', () => {
    render(
      <Hero
        headline="Centered Hero"
        subheadline="Properly spaced"
        primaryCTA="Action"
        onPrimaryCTA={jest.fn()}
      />
    );

    const container = screen.getByText(/centered hero/i).closest('div');
    expect(container).toHaveClass('text-center', 'py-20', 'md:py-28');
  });

  it('handles button disabled states properly', () => {
    const mockOnPrimaryCTA = jest.fn();
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Action"
        onPrimaryCTA={mockOnPrimaryCTA}
      />
    );

    const button = screen.getByRole('button', { name: /action/i });
    expect(button).not.toBeDisabled();

    // Test that the button calls the handler when clicked
    fireEvent.click(button);
    expect(mockOnPrimaryCTA).toHaveBeenCalledTimes(1);
  });

  it('renders with proper animation classes', () => {
    render(
      <Hero
        headline="Animated Hero"
        subheadline="Fade-in text"
        primaryCTA="Get Started"
        onPrimaryCTA={jest.fn()}
      />
    );

    const headline = screen.getByText(/animated hero/i);
    expect(headline).toHaveClass('animate-fade-in');

    const subheadline = screen.getByText(/fade-in text/i);
    expect(subheadline).toHaveClass('animate-fade-in');
  });

  it('passes additional props to container', () => {
    render(
      <Hero
        headline="Test Hero"
        primaryCTA="Action"
        onPrimaryCTA={jest.fn()}
        data-testid="hero-test"
        aria-label="Test hero section"
      />
    );

    const container = screen.getByTestId('hero-test');
    expect(container).toHaveAttribute('aria-label', 'Test hero section');
  });
});