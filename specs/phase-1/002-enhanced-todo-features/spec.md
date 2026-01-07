# Feature Specification: Enhanced Phase I - Advanced Console Todo with Rich Features

**Feature Branch**: `002-enhanced-todo-features`
**Created**: 2025-12-31
**Status**: Draft
**Base**: Extends Phase I specification with intermediate features
**Input**: "Enhance Phase 1 with priorities (high/medium/low), tags/categories (multiple tags per task), search tasks by keyword, filter by status/priority/tags, sort by priority/title/ID, display tasks in a table with 'Total Tasks: N' at the top, use rich library for beautiful tables (add to pyproject.toml via UV). Keep all original Basic features."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Tasks with Priority and Tags (Priority: P1)

A user wants to create tasks with priority levels and categorize them using tags for better organization.

**Why this priority**: This is the foundation for advanced task management. Users need to distinguish urgent work from routine tasks and group related items. Delivers immediate organizational value beyond basic task tracking.

**Independent Test**: Can be fully tested by launching the app, adding tasks with different priorities (high/medium/low) and multiple tags (e.g., "work", "urgent"), viewing the task list, and verifying priorities and tags display correctly with color-coding. Delivers an enhanced task tracker with organization capabilities.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** user adds task "Fix production bug" with priority HIGH and tags "work, urgent, backend", **Then** system creates task with ID 1, priority HIGH (displayed in red), tags ["work", "urgent", "backend"], and confirms success

2. **Given** the app is running, **When** user adds task "Read book" with priority LOW and no tags, **Then** system creates task with priority LOW (displayed in green) and empty tags list, confirms success

3. **Given** the app is running, **When** user adds task "Team meeting" without specifying priority, **Then** system creates task with default priority MEDIUM (displayed in yellow) and confirms success

---

### User Story 2 - View Tasks in Beautiful Table Format (Priority: P1)

A user wants to see all tasks in a professionally formatted table with total task count at the top for better readability.

**Why this priority**: Visual presentation is crucial for user experience. A well-formatted table with color-coding makes it easy to scan tasks, identify priorities, and understand task counts at a glance. This is a core improvement over basic text display.

**Independent Test**: Can be tested by adding multiple tasks with various priorities and tags, viewing the task list, and verifying the table displays with proper headers, columns (ID, Title, Description, Priority, Tags, Status), color-coded priorities, and "Total Tasks: N" summary at the top.

**Acceptance Scenarios**:

1. **Given** the app has 10 tasks, **When** user views all tasks, **Then** system displays "Total Tasks: 10" at the top, followed by a formatted table with columns: ID | Title | Description | Priority | Tags | Status

2. **Given** the app has tasks with mixed priorities, **When** user views tasks, **Then** HIGH priority tasks display in red text, MEDIUM in yellow, LOW in green, making priorities visually distinct

3. **Given** the app has no tasks, **When** user views tasks, **Then** system displays friendly message "📋 No tasks found. Add your first task to get started!"

---

### User Story 3 - Search Tasks by Keyword (Priority: P2)

A user wants to quickly find tasks by searching for keywords in titles or descriptions.

**Why this priority**: As task lists grow, users need efficient ways to locate specific tasks without scrolling through the entire list. Search is a fundamental productivity feature for any task management system.

**Independent Test**: Can be tested by creating tasks with various titles and descriptions, searching for specific keywords (case-insensitive), and verifying only matching tasks appear in results with match count displayed.

**Acceptance Scenarios**:

1. **Given** the app has 20 tasks including "Buy groceries" with description "Milk and bread", **When** user searches for "milk", **Then** system displays "✅ Found 1 task(s) matching 'milk'" and shows the matching task in table format

2. **Given** the app has tasks, **When** user searches for keyword "urgent" (lowercase), **Then** system finds all tasks with "urgent" or "URGENT" or "Urgent" in title or description (case-insensitive matching)

3. **Given** the app has 50 tasks, **When** user searches for "meeting" and finds 5 matches, **Then** system displays only the 5 matching tasks in table format with "Total Tasks: 5" at top

---

### User Story 4 - Filter Tasks by Criteria (Priority: P2)

A user wants to filter tasks by completion status, priority level, or tags to focus on specific subsets.

**Why this priority**: Filtering allows users to focus on what matters right now - show only pending tasks, only high priority items, or only work-related tasks. Essential for managing large task lists efficiently.

**Independent Test**: Can be tested by creating tasks with various statuses, priorities, and tags, then filtering by each criterion and verifying only matching tasks appear with appropriate counts.

**Acceptance Scenarios**:

1. **Given** the app has 30 tasks (20 pending, 10 complete), **When** user filters by status "Pending", **Then** system displays "✅ Showing pending tasks:" with only the 20 pending tasks in table format

2. **Given** the app has tasks with mixed priorities, **When** user filters by priority HIGH, **Then** system shows only tasks with priority HIGH in red color with count at top

3. **Given** the app has tasks with various tags, **When** user filters by tag "work", **Then** system shows all tasks containing "work" tag (case-insensitive) with "✅ Showing tasks with tag 'work':" message

4. **Given** the app has tasks but none match filter, **When** user filters by tag "nonexistent", **Then** system displays "📌 No tasks match the selected filter."

---

### User Story 5 - Sort Tasks by Multiple Criteria (Priority: P3)

A user wants to sort tasks by priority (high to low), alphabetically by title, or by creation order (ID).

**Why this priority**: Sorting provides different views of the same data. Priority sorting shows urgent work first, alphabetical sorting helps find specific tasks, and ID sorting shows chronological order. Enhances usability but less critical than search/filter.

**Independent Test**: Can be tested by creating tasks in random order with various priorities and titles, then sorting by each criterion and verifying the correct sort order is displayed.

**Acceptance Scenarios**:

1. **Given** the app has 15 tasks with mixed priorities, **When** user sorts by priority, **Then** system displays tasks ordered: all HIGH priority first, then MEDIUM, then LOW, with message "✅ Tasks sorted by priority (High → Medium → Low):"

2. **Given** the app has tasks with titles "Zebra", "Apple", "Mango", **When** user sorts by title, **Then** system displays tasks in alphabetical order: Apple, Mango, Zebra with message "✅ Tasks sorted by title (A-Z):"

3. **Given** the app has tasks with IDs 1, 5, 3, 8, 2, **When** user sorts by ID, **Then** system displays tasks in creation order: 1, 2, 3, 5, 8 with message "✅ Tasks sorted by ID (creation order):"

---

### User Story 6 - Update Tasks with New Features (Priority: P3)

A user wants to modify task priorities and tags in addition to title and description when circumstances change.

**Why this priority**: After creating tasks with priorities and tags, users need flexibility to update these attributes. This completes the enhanced CRUD operations but is less critical than creation and viewing.

**Independent Test**: Can be tested by creating tasks, updating priorities and tags, viewing to verify changes persisted, and confirming other attributes remain unchanged.

**Acceptance Scenarios**:

1. **Given** task ID 5 has priority MEDIUM and tags ["personal"], **When** user updates to priority HIGH and tags ["personal", "urgent"], **Then** system updates both attributes, task displays in red with both tags, confirms "Task updated successfully!"

2. **Given** task ID 3 has tags ["work", "backend"], **When** user updates only priority to LOW (keeps existing tags), **Then** system updates priority to LOW (green) but tags remain ["work", "backend"]

3. **Given** task ID 7 exists, **When** user updates task but chooses not to change priority or tags (presses Enter), **Then** system keeps existing priority and tags unchanged, only updates fields user modified

---

### User Story 7 - Delete and Mark Complete with Enhanced Display (Priority: P4)

A user performs basic delete and mark complete operations and sees results in the enhanced table format.

**Why this priority**: These are existing features from Phase I, now integrated with the new table display. Ensures consistency across all operations with the enhanced UI.

**Independent Test**: Can be tested by performing delete and mark complete operations and verifying the enhanced table display shows updated states with proper color-coding and formatting.

**Acceptance Scenarios**:

1. **Given** the app has 25 tasks displayed in rich table format, **When** user deletes task ID 10, **Then** system removes task, displays updated table showing "Total Tasks: 24" and confirms "Task ID 10 deleted successfully!"

2. **Given** task ID 8 with priority HIGH is pending, **When** user marks it complete, **Then** task shows "✓ Complete" status in green while maintaining priority color (red) in priority column

3. **Given** multiple tasks, **When** user views list after any operation (add/update/delete/mark complete), **Then** system always displays professionally formatted table with Total Tasks count, color-coded priorities, and clear status symbols

---

### Edge Cases

- **Empty task list operations**: What happens when user tries to search, filter, or sort with no tasks? System should display appropriate message "📋 No tasks found. Add your first task to get started!" for view, and "📌 No tasks available to [operation]." for search/filter/sort.

- **Invalid priority input**: How does system handle priority input like "4", "medium" (text), or empty? System validates input, re-prompts with error "❌ Error: Please enter 1, 2, or 3", default to MEDIUM if user presses Enter without input.

- **Empty tags list**: What happens when user adds task without tags or clears tags on update? System accepts empty tags list as valid (stores empty list, displays "-" in tags column).

- **Tags with special characters**: How does system handle tags like "work/home", "urgent!", "café"? System accepts all UTF-8 characters in tags, stores and displays as-is.

- **Search with no results**: What happens when search keyword matches nothing? System displays "📋 No tasks found matching '[keyword]'" with empty table.

- **Filter with no matches**: What happens when filter criteria match no tasks? System displays "📌 No tasks match the selected filter." with empty table.

- **Very long tag names**: How does system display tags like "this-is-a-very-long-tag-name-exceeding-normal-length"? System truncates display in table (e.g., "this-is-a-very..") but stores full tag, shows full tag on detail view or update.

- **Duplicate tags**: What happens when user adds task with tags "work, work, urgent"? System accepts duplicates without deduplication (stores ["work", "work", "urgent"]) - user's intent preserved.

- **Case sensitivity in tags**: What happens when user has tags "Work", "work", "WORK"? System treats as case-insensitive for filtering (all match filter "work") but preserves original case in storage and display.

- **Rich library not installed**: What happens if rich library is missing? System detects import failure, displays warning "⚠️ Warning: 'rich' library not installed. Using basic table format. Install with: uv add rich" and falls back to basic formatted print().

- **Sorting empty list**: What happens when user tries to sort with no tasks? System displays "📌 No tasks to sort." and returns to menu.

- **Multiple filters/sorts**: Can user filter by priority HIGH then sort by title within those results? For Phase I enhancement, filters and sorts are independent operations (each displays full filtered/sorted list, not cumulative). Document this behavior.

## Requirements *(mandatory)*

### Functional Requirements

**Enhanced CRUD Operations:**

- **FR-001**: System MUST allow users to add new tasks with required title, optional description, optional priority (HIGH/MEDIUM/LOW, default MEDIUM), and optional tags (comma-separated list, default empty)

- **FR-002**: System MUST auto-generate unique, sequential integer IDs for each new task starting from 1 (unchanged from Phase I)

- **FR-003**: System MUST display all tasks in a formatted table using rich library with columns: ID | Title | Description | Priority | Tags | Status, and "Total Tasks: N" summary at the top

- **FR-004**: System MUST allow users to delete tasks by ID (unchanged from Phase I)

- **FR-005**: System MUST allow users to update task title, description, priority, and/or tags by specifying task ID

- **FR-006**: System MUST allow users to toggle task completion status (unchanged from Phase I)

**Priority Management:**

- **FR-019**: System MUST support three priority levels: HIGH, MEDIUM, LOW represented as enum

- **FR-020**: System MUST use MEDIUM as default priority when user doesn't specify one

- **FR-021**: System MUST validate priority input as 1 (HIGH), 2 (MEDIUM), or 3 (LOW) during interactive input

- **FR-022**: System MUST display priorities with color coding: HIGH in red, MEDIUM in yellow, LOW in green (when rich is available)

**Tags/Categories:**

- **FR-023**: System MUST allow users to add multiple tags per task as a list of strings

- **FR-024**: System MUST accept comma-separated tag input and parse into list (e.g., "work, urgent, backend" → ["work", "urgent", "backend"])

- **FR-025**: System MUST allow empty tags list (no tags is a valid state)

- **FR-026**: System MUST display tags as comma-separated list in table, or "-" if no tags

- **FR-027**: System MUST preserve tag case but perform case-insensitive matching for filtering

**Search Functionality:**

- **FR-028**: System MUST allow users to search tasks by keyword in title or description

- **FR-029**: System MUST perform case-insensitive keyword matching

- **FR-030**: System MUST display search results in table format with count message "Found N task(s) matching '[keyword]'"

- **FR-031**: System MUST display appropriate message when no tasks match search keyword

**Filter Functionality:**

- **FR-032**: System MUST allow users to filter tasks by completion status (completed or pending)

- **FR-033**: System MUST allow users to filter tasks by priority level (HIGH, MEDIUM, or LOW)

- **FR-034**: System MUST allow users to filter tasks by tag (case-insensitive, exact tag match)

- **FR-035**: System MUST display filtered results in table format with descriptive message

- **FR-036**: System MUST display appropriate message when no tasks match filter criteria

**Sort Functionality:**

- **FR-037**: System MUST allow users to sort tasks by priority (HIGH → MEDIUM → LOW order)

- **FR-038**: System MUST allow users to sort tasks alphabetically by title (A-Z, case-insensitive)

- **FR-039**: System MUST allow users to sort tasks by ID (creation order, ascending)

- **FR-040**: System MUST display sorted results in table format with descriptive message

**Display and UI:**

- **FR-041**: System MUST use rich library for formatted table display when available

- **FR-042**: System MUST gracefully fall back to basic formatted print() if rich library is not installed

- **FR-043**: System MUST display "Total Tasks: N" count at the top of every task list view

- **FR-044**: System MUST display clear section headers for menu groupings (Task Management, Advanced Features, Exit)

- **FR-045**: System MUST provide menu options 1-9 for all operations (5 basic CRUD + 3 advanced features + exit)

**Validation and Error Handling (from Phase I, still apply):**

- **FR-007**: System MUST validate that task titles are non-empty when adding or updating tasks

- **FR-008**: System MUST validate that task IDs exist before performing update, delete, or mark complete operations

- **FR-009**: System MUST display clear error messages for invalid operations (non-existent IDs, empty titles, invalid input)

- **FR-010**: System MUST provide a command-line menu interface with numbered options for each operation

- **FR-011**: System MUST store all tasks in memory using Python dataclasses (Task dataclass with priority and tags fields)

- **FR-012**: System MUST maintain task data only during application runtime (data is lost on exit)

- **FR-013**: System MUST handle user input gracefully without crashing on unexpected input

- **FR-014**: System MUST provide a way to exit the application cleanly with confirmation

- **FR-015**: System MUST display completion status using clear visual indicators ("✓ Complete" in green or "○ Pending" in yellow)

### Non-Functional Requirements

- **NFR-001**: Response time for all operations MUST be under 1 second (unchanged)

- **NFR-002**: Application MUST run on Windows (WSL 2), macOS, and Linux systems with Python 3.13+ (unchanged)

- **NFR-003**: Code MUST include comprehensive type hints for all functions and classes (unchanged)

- **NFR-004**: Code MUST include Google-style docstrings for all public functions (unchanged)

- **NFR-005**: Code MUST achieve minimum 80% test coverage with pytest (unchanged)

- **NFR-006**: Code MUST follow PEP 8 style guidelines (unchanged)

- **NFR-007**: Application MUST provide clear, user-friendly prompts and messages (unchanged)

- **NFR-008**: Application MUST handle at least 1000 tasks without performance degradation (unchanged)

- **NFR-009**: Error messages MUST be actionable and guide users to correct their input (unchanged)

- **NFR-010**: Code MUST use constants and enums for all hardcoded values (Priority enum for priorities)

- **NFR-011**: Application MUST use modular architecture: models.py (dataclasses), services.py (business logic), cli.py (UI layer)

- **NFR-012**: Application MUST install rich library via UV package manager (add to pyproject.toml dependencies)

### Key Entities

- **Task**: Represents a single todo item with attributes:
  - `id` (int): Unique auto-generated identifier, sequential starting from 1
  - `title` (str): Required, non-empty description of the task
  - `description` (str): Optional, additional details about the task (can be empty)
  - `completed` (bool): Completion status, False by default, toggleable
  - `priority` (Priority enum): Task priority level (HIGH/MEDIUM/LOW), default MEDIUM
  - `tags` (list[str]): List of tag strings for categorization, default empty list

- **Priority** (Enum): Priority levels with values:
  - HIGH = "high"
  - MEDIUM = "medium"
  - LOW = "low"
  - Supports comparison for sorting (HIGH < MEDIUM < LOW)

- **TodoService**: Service class managing in-memory task storage and operations:
  - Stores tasks as list of Task dataclass instances
  - Provides CRUD operations: add, get_all, get_by_id, update, delete, mark_complete
  - Provides advanced operations: search, filter_by_status, filter_by_priority, filter_by_tag
  - Provides sort operations: sort_by_priority, sort_by_title, sort_by_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Basic Operations (Enhanced):**

- **SC-001**: Users can add a new task with title, priority, and tags in under 15 seconds

- **SC-002**: Users can view their complete task list in professional table format with color-coded priorities in under 2 seconds

- **SC-003**: Users can update any task's title, description, priority, and/or tags in under 20 seconds

- **SC-004**: Users can delete any task in under 10 seconds (unchanged)

- **SC-005**: Users can mark any task complete or pending in under 10 seconds (unchanged)

**Advanced Features:**

- **SC-011**: Users can search for tasks by keyword and see results in under 5 seconds

- **SC-012**: Users can filter tasks by status/priority/tags and see results in under 5 seconds

- **SC-013**: Users can sort tasks by priority/title/ID and see results in under 3 seconds

- **SC-014**: 100% of task lists display with "Total Tasks: N" count at the top

- **SC-015**: 100% of priority levels display with correct color coding (red/yellow/green) when rich library is installed

**Performance and Quality:**

- **SC-006**: Application handles up to 1000 tasks with all operations (including search/filter/sort) completing in under 1 second

- **SC-007**: 100% of invalid operations provide clear error messages without crashing (unchanged)

- **SC-008**: All operations (basic CRUD + search/filter/sort) are covered by automated tests with 80%+ code coverage

- **SC-009**: Users can distinguish complete vs pending tasks, and HIGH vs MEDIUM vs LOW priorities at a glance from the table view

- **SC-010**: Application startup and menu display occurs in under 2 seconds (unchanged)

**User Experience:**

- **SC-016**: Users can successfully use the application with or without rich library installed (fallback works correctly)

- **SC-017**: 95% of users can successfully add tasks with priorities and tags on first attempt without errors

- **SC-018**: Users can navigate the enhanced 9-option menu intuitively with numbered choices

## Assumptions

**From Phase I (still apply):**

- **A-001**: Users are comfortable with basic command-line interfaces and can follow numbered menu options

- **A-002**: Users understand that data is not persisted and will be lost when the application exits

- **A-003**: Users will run the application on systems with Python 3.13+ and UV package manager already installed

- **A-004**: Task IDs do not need to be reused after deletion (sequential IDs can have gaps)

- **A-005**: A single user operates the application at a time (no concurrent access)

- **A-006**: Users will input task titles, descriptions, and tags in UTF-8 compatible text

- **A-007**: The maximum reasonable number of tasks is under 10,000

**New Assumptions for Enhanced Features:**

- **A-011**: Users understand that priorities are visual indicators only (HIGH/MEDIUM/LOW) and don't trigger automatic notifications or alerts

- **A-012**: Users can identify colors (or will use text labels if colorblind) - both color and text labels are provided

- **A-013**: Users understand that tags are simple labels, not hierarchical categories or folders

- **A-014**: Search matches partial strings (e.g., "gro" matches "groceries"), not full-word only

- **A-015**: Filters and sorts are independent operations, not cumulative (can't filter by priority then sort the filtered results in one operation)

- **A-016**: Users will install rich library via UV as instructed, or accept basic table fallback

- **A-017**: Default priority MEDIUM is acceptable when users don't specify (no mandatory priority selection)

- **A-018**: No pagination needed - all search/filter/sort results display in single view (reasonable for under 10,000 tasks)

## Out of Scope

**Phase I Exclusions (from original, still excluded):**

- ❌ Persistence (file storage, database, saving between sessions)
- ❌ Authentication (user accounts, login, passwords)
- ❌ Web Interface (browser UI, REST API, web server)
- ❌ Multi-user (user management, shared tasks, collaboration)
- ❌ Import/Export (file import, export to other formats)
- ❌ Undo/Redo (operation history)
- ❌ Task Dependencies (subtasks, relationships, dependencies)
- ❌ Notifications (email alerts, push notifications, reminders)
- ❌ Themes/Customization (UI customization beyond rich library, color schemes, config files)

**Additional Exclusions for Enhanced Phase:**

- ❌ **Due Dates**: No date/time tracking, no deadlines, no calendar integration
- ❌ **Recurring Tasks**: No repeating tasks, no schedules
- ❌ **Task Notes/Attachments**: No file attachments, no rich text formatting, no embedded images
- ❌ **Advanced Search**: No regex search, no Boolean operators (AND/OR/NOT), no saved searches
- ❌ **Combined Filters**: No chaining filters (e.g., filter by priority AND tag simultaneously)
- ❌ **Custom Sort Orders**: No multi-level sorting (e.g., sort by priority then title)
- ❌ **Tag Autocomplete**: No tag suggestions, no tag management UI
- ❌ **Bulk Operations**: No multi-select, no batch update/delete
- ❌ **Task Templates**: No saved task templates or presets
- ❌ **Statistics/Reports**: No analytics, no charts, no progress tracking

## Dependencies

**From Phase I:**

- **Python 3.13+**: Required runtime environment
- **UV Package Manager**: Required for dependency management and project setup
- **pytest**: Required for automated testing (installed via UV)
- **pytest-cov**: Required for coverage reporting (installed via UV)
- **Operating System**: Windows with WSL 2, macOS, or Linux

**New for Enhanced Phase:**

- **rich library**: Required for beautiful table formatting and color output
  - Installation: `uv add rich`
  - Version: Latest stable (≥13.0.0)
  - Purpose: Table rendering, color output, text formatting
  - Fallback: Application works without it (basic table formatting)

## Constraints

**Technology Stack:**

- MUST use Python 3.13+ only
- MUST use UV package manager
- MUST use pytest for testing
- MUST use rich library for table display (with graceful fallback)
- MUST use Python dataclasses for Task entity (not dicts)
- MUST use Python Enum for Priority

**Architecture:**

- MUST follow three-layer architecture:
  - models.py: Task dataclass and Priority enum
  - services.py: TodoService class with all business logic
  - cli.py: User interface and menu system

**Storage:**

- MUST use in-memory storage only (list of Task dataclasses)
- MUST NOT use external storage (no files, no databases)

**Interface:**

- MUST be command-line interface only
- MUST provide numbered menu (1-9 options)
- MUST use rich library for display when available

**Features:**

- MUST implement all 5 basic CRUD operations from Phase I
- MUST add priorities, tags, search, filter, sort as specified
- MUST NOT add features beyond this specification

**Code Quality:**

- MUST achieve 80% minimum code coverage
- MUST follow PEP 8 style guidelines
- MUST include type hints on all functions
- MUST include Google-style docstrings

## Risks

**From Phase I (still apply):**

- **R-001**: Data loss on exit may surprise users
  - **Mitigation**: Display clear exit confirmation warning

- **R-003**: Invalid input could cause crashes
  - **Mitigation**: Comprehensive input validation and error handling

- **R-004**: Test coverage below 80%
  - **Mitigation**: Write tests for all new features, verify coverage

**New Risks for Enhanced Features:**

- **R-006**: Rich library dependency may not be installed
  - **Mitigation**: Graceful fallback to basic formatting, clear installation instructions

- **R-007**: Color-coding may not be visible to colorblind users
  - **Mitigation**: Always include text labels in addition to colors (e.g., "HIGH" text + red color)

- **R-008**: Large tag lists may overflow table columns
  - **Mitigation**: Truncate display in table (show "tag1, tag2, ..." with ".." for overflow), full tags visible in update view

- **R-009**: Search/filter/sort on very large task lists (5000+ tasks) may have performance issues
  - **Mitigation**: Test with large datasets, optimize search/filter algorithms, document practical limits

- **R-010**: Users may expect cumulative filters (filter then sort results) but only independent operations are supported
  - **Mitigation**: Document this limitation clearly in README, consider for future phase

## Deliverables

For Enhanced Phase I completion:

1. **Source Code**:
   - `phase1-console/src/models.py` - Task dataclass and Priority enum
   - `phase1-console/src/services.py` - TodoService with all CRUD + advanced operations
   - `phase1-console/src/cli.py` - Enhanced CLI with 9-option menu and rich table display

2. **Tests**:
   - `phase1-console/tests/test_models.py` - Test Task dataclass and Priority enum
   - `phase1-console/tests/test_services.py` - Test all TodoService methods
   - `phase1-console/tests/test_cli.py` - Test CLI input/output functions
   - Coverage report showing 80%+ coverage

3. **Configuration**:
   - Updated `pyproject.toml` with rich library dependency
   - All dev dependencies (pytest, pytest-cov, ruff, mypy)

4. **Documentation**:
   - Updated README.md with new features, installation (including rich), usage examples for all 9 features
   - This spec.md in `specs/002-enhanced-todo-features/`

5. **Demo**: Video or screenshots demonstrating:
   - Adding tasks with priorities and tags
   - Viewing tasks in beautiful table with color-coding
   - Searching, filtering, and sorting tasks
   - All features working together

## Acceptance Criteria

The Enhanced Phase I implementation is considered complete when:

**All Phase I Basic Features Still Work:**

1. ✅ All 5 basic features (add, delete, update, view, mark complete) remain fully functional
2. ✅ All original functional requirements (FR-001 through FR-015) still met
3. ✅ All original non-functional requirements (NFR-001 through NFR-010) still met

**New Enhanced Features:**

4. ✅ Priority system fully implemented (HIGH/MEDIUM/LOW with color-coding)
5. ✅ Tags/categories fully implemented (multiple tags per task, comma-separated input)
6. ✅ Search by keyword fully functional (case-insensitive, searches title and description)
7. ✅ Filter by status/priority/tags fully functional
8. ✅ Sort by priority/title/ID fully functional
9. ✅ Rich table display implemented with "Total Tasks: N" at top
10. ✅ All new functional requirements (FR-019 through FR-045) implemented
11. ✅ Rich library added to pyproject.toml and installs via UV
12. ✅ Graceful fallback when rich library not available

**Code Quality:**

13. ✅ Three-layer architecture implemented (models.py, services.py, cli.py)
14. ✅ Task dataclass replaces dict-based storage
15. ✅ Priority enum implemented with comparison methods
16. ✅ All new functions have type hints and Google-style docstrings
17. ✅ Test coverage 80% or higher including new features
18. ✅ All tests pass without failures
19. ✅ Code follows PEP 8 style guidelines

**User Experience:**

20. ✅ All 9 menu options accessible and clearly labeled
21. ✅ Color-coded priorities visible when rich installed
22. ✅ "Total Tasks: N" displays at top of all task views
23. ✅ All user stories have passing acceptance scenarios
24. ✅ All edge cases handled gracefully

**Documentation:**

25. ✅ README updated with new features and usage examples
26. ✅ Installation instructions include `uv add rich`
27. ✅ All new features demonstrated in demo video/screenshots

---

**Next Steps**:
- ✅ Specification complete - ready for `/sp.clarify` or `/sp.plan`
- Use `/sp.clarify` if any requirements need stakeholder input
- Use `/sp.plan` to create architectural plan for implementation
- Then `/sp.tasks` to break down into atomic implementation tasks
- Then `/sp.implement` with `hackathon-cli-builder` agent to generate all code layers
