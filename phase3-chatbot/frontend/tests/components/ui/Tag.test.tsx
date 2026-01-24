import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Tag } from '@/components/ui/Tag';

describe('Tag Component', () => {
  it('renders with label text', () => {
    render(<Tag label="Work" />);

    const tag = screen.getByText(/work/i);
    expect(tag).toBeInTheDocument();
    expect(tag.tagName).toBe('SPAN');
  });

  it('renders with different variants', () => {
    render(
      <>
        <Tag label="Default" variant="default" />
        <Tag label="Success" variant="success" />
        <Tag label="Warning" variant="warning" />
        <Tag label="Error" variant="error" />
        <Tag label="Accent" variant="accent" />
      </>
    );

    expect(screen.getByText(/default/i)).toHaveClass('bg-neutral-700', 'text-neutral-200');
    expect(screen.getByText(/success/i)).toHaveClass('bg-success-500/20', 'text-success-500');
    expect(screen.getByText(/warning/i)).toHaveClass('bg-warning-500/20', 'text-warning-500');
    expect(screen.getByText(/error/i)).toHaveClass('bg-error-500/20', 'text-error-500');
    expect(screen.getByText(/accent/i)).toHaveClass('bg-accent-500/20', 'text-accent-500');
  });

  it('renders with different sizes', () => {
    render(
      <>
        <Tag label="Small" size="sm" />
        <Tag label="Medium" size="md" />
      </>
    );

    expect(screen.getByText(/small/i)).toHaveClass('text-xs', 'px-2', 'py-1');
    expect(screen.getByText(/medium/i)).toHaveClass('text-sm', 'px-3', 'py-1.5');
  });

  it('shows removable icon when removable prop is true', () => {
    render(<Tag label="Removable" removable />);

    const tag = screen.getByText(/removable/i);
    const removeButton = screen.getByLabelText(/remove removable tag/i);

    expect(removeButton).toBeInTheDocument();
    expect(removeButton).toHaveClass('ml-1.5', 'flex-shrink-0', 'h-4', 'w-4');
  });

  it('calls onRemove when remove button is clicked', () => {
    const mockOnRemove = jest.fn();
    render(<Tag label="Removable" removable onRemove={mockOnRemove} />);

    const removeButton = screen.getByLabelText(/remove removable tag/i);
    fireEvent.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalledTimes(1);
  });

  it('does not call onRemove when not removable', () => {
    const mockOnRemove = jest.fn();
    render(<Tag label="Not Removable" onRemove={mockOnRemove} />);

    expect(() => screen.getByLabelText(/remove not removable tag/i)).toThrow();
    expect(mockOnRemove).not.toHaveBeenCalled();
  });

  it('stops event propagation when remove button is clicked', () => {
    const mockOnRemove = jest.fn();
    const mockParentClick = jest.fn();

    render(
      <div onClick={mockParentClick}>
        <Tag label="Prop Stop" removable onRemove={mockOnRemove} />
      </div>
    );

    const removeButton = screen.getByLabelText(/remove prop stop tag/i);
    fireEvent.click(removeButton);

    expect(mockOnRemove).toHaveBeenCalledTimes(1);
    expect(mockParentClick).not.toHaveBeenCalled();
  });

  it('applies custom className', () => {
    render(<Tag label="Custom" className="custom-tag-class" />);

    const tag = screen.getByText(/custom/i);
    expect(tag).toHaveClass('custom-tag-class');
  });

  it('renders with proper font weight', () => {
    render(<Tag label="Bold" />);

    const tag = screen.getByText(/bold/i);
    expect(tag).toHaveClass('font-medium');
  });

  it('handles click events when interactive', () => {
    const mockOnClick = jest.fn();
    render(<Tag label="Clickable" onClick={mockOnClick} />);

    const tag = screen.getByText(/clickable/i);
    fireEvent.click(tag);

    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('renders with consistent styling classes', () => {
    render(<Tag label="Consistent" />);

    const tag = screen.getByText(/consistent/i);
    expect(tag).toHaveClass('inline-flex', 'items-center', 'rounded-full', 'whitespace-nowrap');
    expect(tag).toHaveClass('transition-colors', 'duration-base');
  });
});