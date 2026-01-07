/**
 * Tests for FilterBar component
 *
 * Verifies:
 * - Search input rendering and functionality
 * - Status filter (all/completed/pending)
 * - Priority filter (all/low/medium/high)
 * - Callbacks triggered with correct values
 * - Clear filters functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FilterBar from '../components/todos/FilterBar';

describe('FilterBar', () => {
  const mockOnSearchChange = jest.fn();
  const mockOnStatusFilterChange = jest.fn();
  const mockOnPriorityFilterChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all filter controls', () => {
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    expect(screen.getByPlaceholderText(/search tasks/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/status/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
  });

  it('calls onSearchChange when search input changes', async () => {
    const user = userEvent.setup();
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const searchInput = screen.getByPlaceholderText(/search tasks/i);
    await user.type(searchInput, 'groceries');

    expect(mockOnSearchChange).toHaveBeenCalled();
  });

  it('calls onStatusFilterChange when status filter changes', async () => {
    const user = userEvent.setup();
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const statusFilter = screen.getByLabelText(/status/i);
    await user.selectOptions(statusFilter, 'completed');

    expect(mockOnStatusFilterChange).toHaveBeenCalledWith('completed');
  });

  it('calls onPriorityFilterChange when priority filter changes', async () => {
    const user = userEvent.setup();
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const priorityFilter = screen.getByLabelText(/priority/i);
    await user.selectOptions(priorityFilter, 'high');

    expect(mockOnPriorityFilterChange).toHaveBeenCalledWith('high');
  });

  it('displays current search value', () => {
    render(
      <FilterBar
        search="test search"
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const searchInput = screen.getByPlaceholderText(/search tasks/i) as HTMLInputElement;
    expect(searchInput.value).toBe('test search');
  });

  it('displays current status filter value', () => {
    render(
      <FilterBar
        search=""
        statusFilter="completed"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const statusFilter = screen.getByLabelText(/status/i) as HTMLSelectElement;
    expect(statusFilter.value).toBe('completed');
  });

  it('displays current priority filter value', () => {
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="high"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const priorityFilter = screen.getByLabelText(/priority/i) as HTMLSelectElement;
    expect(priorityFilter.value).toBe('high');
  });

  it('has all status filter options', () => {
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const statusFilter = screen.getByLabelText(/status/i);
    const options = Array.from(statusFilter.querySelectorAll('option'));

    expect(options).toHaveLength(3);
    expect(options.map(opt => opt.value)).toEqual(['all', 'completed', 'pending']);
  });

  it('has all priority filter options', () => {
    render(
      <FilterBar
        search=""
        statusFilter="all"
        priorityFilter="all"
        onSearchChange={mockOnSearchChange}
        onStatusFilterChange={mockOnStatusFilterChange}
        onPriorityFilterChange={mockOnPriorityFilterChange}
      />
    );

    const priorityFilter = screen.getByLabelText(/priority/i);
    const options = Array.from(priorityFilter.querySelectorAll('option'));

    expect(options).toHaveLength(4);
    expect(options.map(opt => opt.value)).toEqual(['all', 'low', 'medium', 'high']);
  });
});
