# Component API Contracts

**Date**: 2026-01-05
**Feature**: Premium UI/UX Enhancement System
**Phase**: Phase 1 - Design & Contracts

This document defines the public API (props, variants, behavior) for each UI component in the Premium UI Enhancement system. These contracts serve as specifications for implementation via `/sp.tasks` and `/sp.implement`.

---

## Core UI Components (`components/ui/`)

### Button Component

**File**: `phase2-fullstack/frontend/components/ui/Button.tsx`

**Purpose**: Standardized button component with 4 variants (primary, secondary, outline, ghost) for consistent interactive elements across the application.

#### TypeScript Interface

```typescript
interface ButtonProps {
  /**
   * Visual style variant
   * @default 'primary'
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';

  /**
   * Button size
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg';

  /**
   * Whether button is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether button is in loading state (shows spinner)
   * @default false
   */
  loading?: boolean;

  /**
   * Whether button should take full width of container
   * @default false
   */
  fullWidth?: boolean;

  /**
   * Button content
   */
  children: React.ReactNode;

  /**
   * Click handler
   */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;

  /**
   * HTML button type
   * @default 'button'
   */
  type?: 'button' | 'submit' | 'reset';

  /**
   * Additional Tailwind classes for customization
   */
  className?: string;
}
```

#### Variant Specifications

| Variant | Background | Text Color | Border | Hover Effect |
|---------|------------|------------|--------|--------------|
| `primary` | `bg-primary-500` | `text-white` | None | `bg-primary-600` (darker) |
| `secondary` | `bg-neutral-700` | `text-white` | None | `bg-neutral-600` (lighter) |
| `outline` | `transparent` | `text-primary-500` | `border-primary-500` | `bg-primary-500/10` (subtle fill) |
| `ghost` | `transparent` | `text-neutral-300` | None | `bg-neutral-800` (subtle bg) |

#### Size Specifications

| Size | Padding | Font Size | Height |
|------|---------|-----------|--------|
| `sm` | `px-3 py-1.5` | `text-sm` | `h-8` |
| `md` | `px-4 py-2` | `text-base` | `h-10` |
| `lg` | `px-6 py-3` | `text-lg` | `h-12` |

#### Behavior Specifications

- **Hover State**:
  - Transition duration: 200ms (`transition-colors duration-base`)
  - Background color or opacity change based on variant
  - Cursor: `cursor-pointer`

- **Active/Pressed State**:
  - Slightly darker appearance: `active:scale-[0.98]`
  - Transform duration: 150ms (`transition-transform duration-fast`)

- **Disabled State**:
  - Reduced opacity: `opacity-50`
  - Cursor: `cursor-not-allowed`
  - No hover effects
  - onClick disabled

- **Loading State**:
  - Show spinner icon (use Heroicons `ArrowPathIcon` with `animate-spin`)
  - Disable onClick
  - Maintain button dimensions (don't collapse)
  - Text becomes invisible but space preserved

#### Accessibility Requirements

- **Keyboard Navigation**: Focusable via Tab key
- **Focus Indicator**: Visible focus ring `ring-2 ring-accent-500 ring-offset-2 ring-offset-neutral-900`
- **ARIA Attributes**: `aria-disabled="true"` when disabled, `aria-busy="true"` when loading
- **Touch Target**: Minimum 44x44px touch area (met by size='md' default)

#### Usage Examples

```tsx
// Primary button (default)
<Button onClick={handleSubmit}>Submit</Button>

// Outline button with loading state
<Button variant="outline" loading={isLoading}>Save</Button>

// Full-width secondary button
<Button variant="secondary" fullWidth>Cancel</Button>

// Small ghost button
<Button variant="ghost" size="sm" onClick={handleClose}>Close</Button>
```

---

### Input Component

**File**: `phase2-fullstack/frontend/components/ui/Input.tsx`

**Purpose**: Standardized text input with label, error state, and accessibility features for form fields.

#### TypeScript Interface

```typescript
interface InputProps {
  /**
   * Label text (required for accessibility)
   */
  label: string;

  /**
   * Input type
   * @default 'text'
   */
  type?: 'text' | 'email' | 'password' | 'number';

  /**
   * Placeholder text
   */
  placeholder?: string;

  /**
   * Controlled input value
   */
  value?: string;

  /**
   * Change handler
   */
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;

  /**
   * Error message (if present, displays below input in error color)
   */
  error?: string;

  /**
   * Whether input is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether input is required
   * @default false
   */
  required?: boolean;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Layout Specifications

- **Label Position**: Above input (traditional, NOT floating)
- **Spacing**: `space-y-2` between label and input
- **Input Height**: `h-12` (48px) for comfortable touch target
- **Input Padding**: `px-4 py-3`

#### Style Specifications

**Normal State**:
```
bg-neutral-800
border border-neutral-700
text-neutral-100
rounded-md
```

**Focus State**:
```
ring-2 ring-accent-500
border-accent-500
outline-none
transition-all duration-base
```

**Error State**:
```
border-error-500
ring-error-500 (on focus)
```

**Disabled State**:
```
bg-neutral-900
text-neutral-600
cursor-not-allowed
opacity-60
```

#### Error Message Display

- **Position**: Below input (`mt-1`)
- **Color**: `text-error-500`
- **Icon**: `ExclamationCircleIcon` from Heroicons (16px, inline before text)
- **Font Size**: `text-sm`

#### Accessibility Requirements

- **Label Association**: `<label htmlFor={id}>` linked to `<input id={id}>`
- **Required Indicator**: Add `*` to label text if required=true
- **Error Announcement**: `aria-invalid="true"` and `aria-describedby={errorId}` when error present
- **Focus Visible**: Clear focus ring (ring-2 ring-accent-500)

#### Usage Examples

```tsx
// Basic text input
<Input
  label="Full Name"
  placeholder="John Doe"
  value={name}
  onChange={(e) => setName(e.target.value)}
/>

// Email input with error
<Input
  label="Email Address"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={emailError}
  required
/>

// Password input
<Input
  label="Password"
  type="password"
  value={password}
  onChange={(e) => setPassword(e.target.value)}
  required
/>
```

---

### Card Component

**File**: `phase2-fullstack/frontend/components/ui/Card.tsx`

**Purpose**: Container component with consistent styling, shadows, and optional hover effects.

#### TypeScript Interface

```typescript
interface CardProps {
  /**
   * Card content
   */
  children: React.ReactNode;

  /**
   * Visual variant
   * @default 'default'
   */
  variant?: 'default' | 'hover' | 'interactive';

  /**
   * Padding size
   * @default 'md'
   */
  padding?: 'sm' | 'md' | 'lg';

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Variant Specifications

| Variant | Description | Hover Effect | Cursor |
|---------|-------------|--------------|--------|
| `default` | Static card, no interaction | None | `cursor-default` |
| `hover` | Elevates on hover | Shadow md → lg, translate-y -1px | `cursor-default` |
| `interactive` | Clickable card | Shadow md → lg, translate-y -1px, scale 1.02 | `cursor-pointer` |

#### Base Styles

```
bg-neutral-800
border border-neutral-700
rounded-lg (12px border radius)
shadow-md (default)
transition-all duration-base (200ms)
```

#### Padding Specifications

| Size | Padding Class |
|------|---------------|
| `sm` | `p-4` (16px) |
| `md` | `p-6` (24px) |
| `lg` | `p-8` (32px) |

#### Hover Behavior (variant='hover' or 'interactive')

```
hover:shadow-lg
hover:-translate-y-1
hover:border-neutral-600
```

Additional for `interactive`:
```
hover:scale-[1.02]
active:scale-[0.99]
```

#### Usage Examples

```tsx
// Default static card
<Card>
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</Card>

// Hoverable card with small padding
<Card variant="hover" padding="sm">
  <StatsCard label="Total Tasks" value={42} />
</Card>

// Interactive clickable card
<Card variant="interactive" onClick={handleClick}>
  <TaskPreview task={task} />
</Card>
```

---

### Tag Component

**File**: `phase2-fullstack/frontend/components/ui/Tag.tsx`

**Purpose**: Pill-shaped label for categories, tags, and status indicators with color-coded variants.

#### TypeScript Interface

```typescript
interface TagProps {
  /**
   * Tag label text
   */
  label: string;

  /**
   * Color variant
   * @default 'default'
   */
  variant?: 'default' | 'success' | 'warning' | 'error';

  /**
   * Tag size
   * @default 'md'
   */
  size?: 'sm' | 'md';

  /**
   * Whether tag shows remove button (X icon)
   * @default false
   */
  removable?: boolean;

  /**
   * Callback when remove button clicked
   */
  onRemove?: () => void;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Variant Specifications

| Variant | Background | Text Color | Border |
|---------|------------|------------|--------|
| `default` | `bg-neutral-700` | `text-neutral-200` | None |
| `success` | `bg-success-500/20` | `text-success-500` | None |
| `warning` | `bg-warning-500/20` | `text-warning-500` | None |
| `error` | `bg-error-500/20` | `text-error-500` | None |

#### Size Specifications

| Size | Padding | Font Size | Height |
|------|---------|-----------|--------|
| `sm` | `px-2 py-1` | `text-xs` | Auto (compact) |
| `md` | `px-3 py-1.5` | `text-sm` | Auto |

#### Base Styles

```
rounded-full (pill shape)
inline-flex items-center gap-1
font-medium
transition-colors duration-base
```

#### Hover Behavior

- Slightly brighter background: `hover:bg-{variant}-500/30` (for semantic colors) or `hover:bg-neutral-600` (for default)
- Cursor: `cursor-default` (unless removable, then `cursor-pointer` on X icon)

#### Removable Tag Behavior

- Show `XMarkIcon` from Heroicons (14px for sm, 16px for md)
- X icon appears on right side with small gap (`gap-1`)
- X icon clickable area: minimum 24x24px (padding applied)
- X icon hover: `hover:text-{variant}-400` or `hover:text-neutral-300`

#### Usage Examples

```tsx
// Default tag
<Tag label="Work" />

// Success tag (completed status)
<Tag label="Completed" variant="success" />

// Removable warning tag
<Tag label="Urgent" variant="warning" removable onRemove={handleRemove} />

// Small default tag
<Tag label="Personal" size="sm" />
```

---

### Select Component

**File**: `phase2-fullstack/frontend/components/ui/Select.tsx`

**Purpose**: Dropdown select input with keyboard navigation and accessibility features.

#### TypeScript Interface

```typescript
interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps {
  /**
   * Optional label above select
   */
  label?: string;

  /**
   * Array of options
   */
  options: SelectOption[];

  /**
   * Currently selected value
   */
  value?: string;

  /**
   * Change handler
   */
  onChange?: (value: string) => void;

  /**
   * Placeholder text when no selection
   */
  placeholder?: string;

  /**
   * Whether select is disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Layout & Styles

**Select Trigger** (button that opens dropdown):
```
bg-neutral-800
border border-neutral-700
rounded-md
px-4 py-3
h-12
flex items-center justify-between
text-neutral-100
hover:border-neutral-600
focus:ring-2 focus:ring-accent-500
```

**Dropdown Menu**:
```
Absolute positioning (below trigger)
bg-neutral-800
border border-neutral-700
rounded-md
shadow-lg
max-h-60 (240px) with overflow-y-auto
animate-in (fade + slide down 4px over 150ms)
z-50
```

**Dropdown Option**:
```
px-4 py-2
text-neutral-100
hover:bg-neutral-700
cursor-pointer
flex items-center justify-between
```

**Selected Option**:
```
bg-neutral-700 (highlighted bg)
text-accent-500 (accent text)
CheckIcon from Heroicons (16px) on right side
```

#### Behavior Specifications

- **Open/Close**:
  - Click trigger to toggle
  - Click outside to close (useOutsideClick hook)
  - Escape key to close
  - Animation: fade-in + translateY over 150ms

- **Keyboard Navigation**:
  - Arrow Up/Down: Navigate options
  - Enter: Select focused option
  - Escape: Close dropdown
  - Tab: Focus next element (closes dropdown)

- **Disabled State**:
  - Trigger: `opacity-60 cursor-not-allowed`
  - No interaction possible

#### Accessibility Requirements

- **ARIA Attributes**:
  - `role="combobox"` on trigger
  - `aria-expanded` true/false
  - `aria-activedescendant` points to focused option
  - `role="listbox"` on dropdown menu
  - `role="option"` on each option
- **Keyboard Support**: Full keyboard navigation (arrows, enter, escape)
- **Screen Reader**: Announce selected value and option count

#### Usage Examples

```tsx
// Basic select
<Select
  label="Priority"
  options={[
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ]}
  value={priority}
  onChange={setPriority}
  placeholder="Select priority..."
/>

// Select without label
<Select
  options={categories}
  value={category}
  onChange={setCategory}
/>
```

---

## Dashboard Components (`components/dashboard/`)

### StatsCard Component

**File**: `phase2-fullstack/frontend/components/dashboard/StatsCard.tsx`

**Purpose**: Display key metrics with icon, label, and numeric value for dashboard overview.

#### TypeScript Interface

```typescript
interface StatsCardProps {
  /**
   * Metric label (e.g., "Total Tasks")
   */
  label: string;

  /**
   * Metric value (number or formatted string)
   */
  value: number | string;

  /**
   * Optional icon component from Heroicons
   */
  icon?: React.ReactNode;

  /**
   * Optional trend indicator
   */
  trend?: 'up' | 'down' | 'neutral';
}
```

#### Layout Specifications

```
Base: Card component (variant='default', padding='md')
Flexbox layout: flex flex-col gap-3
Icon + Label row: flex items-center gap-2
Value: Large, bold number
```

#### Style Specifications

- **Icon**: 24x24px, `text-accent-500` (or semantic color)
- **Label**: `text-sm text-neutral-400 font-medium`
- **Value**: `text-3xl font-bold text-neutral-100`
- **Trend Indicator** (optional): Small icon + percentage change

#### Responsive Behavior

- **Desktop (>1024px)**: 3 columns (grid-cols-3)
- **Tablet (768-1024px)**: 2 columns (grid-cols-2)
- **Mobile (<768px)**: 1 column (grid-cols-1)

#### Animation

- Fade-in on page load with staggered delay:
  - Card 1: 100ms delay
  - Card 2: 200ms delay
  - Card 3: 300ms delay

#### Usage Example

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <StatsCard
    label="Total Tasks"
    value={42}
    icon={<ListBulletIcon className="w-6 h-6" />}
  />
  <StatsCard
    label="In Progress"
    value={15}
    icon={<ClockIcon className="w-6 h-6" />}
  />
  <StatsCard
    label="Completed"
    value={27}
    icon={<CheckCircleIcon className="w-6 h-6" />}
    trend="up"
  />
</div>
```

---

### TaskCard Component

**File**: `phase2-fullstack/frontend/components/dashboard/TaskCard.tsx`

**Purpose**: Display individual task with title, tags, date, and interactive elements.

#### TypeScript Interface

```typescript
interface Task {
  id: string;
  title: string;
  tags: string[];
  createdAt: string;
  priority?: 'high' | 'medium' | 'low';
  completed?: boolean;
}

interface TaskCardProps {
  /**
   * Task data
   */
  task: Task;

  /**
   * Edit handler (optional)
   */
  onEdit?: (id: string) => void;

  /**
   * Delete handler (optional)
   */
  onDelete?: (id: string) => void;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Layout Specifications

```
Base: Card component (variant='hover', padding='md')
Flexbox layout: flex flex-col gap-3
Header row: flex items-start justify-between
Tags row: flex flex-wrap gap-2
Footer row: text-sm text-neutral-400
```

#### Style Specifications

- **Title**: `text-lg font-medium text-neutral-100` with `line-clamp-2` (max 2 lines, ellipsis)
- **Tags**: Tag components (variant based on tag type)
- **Date**: Relative time format (e.g., "2 hours ago", "3 days ago")
- **Priority Badge** (optional): Small colored dot or text

#### Hover Behavior

- Card elevates (from Card variant='hover')
- Shadow transitions from md to lg
- Subtle upward translate (-1px)

#### Interactive Elements

- **Edit Button**: Ghost button with PencilIcon (appears on hover)
- **Delete Button**: Ghost button with TrashIcon (appears on hover)

#### Truncation Handling

- **Long Titles**: 2-line max with ellipsis (`line-clamp-2`)
- **Many Tags**: Wrap to multiple lines (`flex-wrap`)
- **Alternative**: Show "+N more" tag if >5 tags

#### Usage Example

```tsx
<TaskCard
  task={{
    id: '1',
    title: 'Implement user authentication with JWT tokens',
    tags: ['backend', 'security', 'urgent'],
    createdAt: '2026-01-04T10:30:00Z',
    priority: 'high',
    completed: false,
  }}
  onEdit={handleEdit}
  onDelete={handleDelete}
/>
```

---

### TaskInput Component

**File**: `phase2-fullstack/frontend/components/dashboard/TaskInput.tsx`

**Purpose**: Task creation interface with input field and priority/classification selectors.

#### TypeScript Interface

```typescript
interface TaskInputProps {
  /**
   * Submit handler (receives task title, priority, classification)
   */
  onSubmit: (data: { title: string; priority: string; classification: string }) => void;

  /**
   * Whether form is in loading state (submitting)
   * @default false
   */
  loading?: boolean;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Layout Specifications

```
Card component (variant='default', padding='lg')
Flexbox layout: flex flex-col md:flex-row gap-4
Input takes flex-1 (fills available space)
Selects fixed width on desktop, full width on mobile
```

#### Components Used

- **Input**: Main task title input (placeholder: "What's the next milestone?")
- **Select** (Priority): Options: High, Medium, Low
- **Select** (Classification): Options: Work, Personal, Urgent, etc.
- **Button**: Submit button ("Add Task")

#### Style Specifications

- **Input**: Larger than standard (h-14), prominent border on focus
- **Accent Border on Focus**: `focus-within:border-accent-500 focus-within:ring-2 focus-within:ring-accent-500`
- **Selects**: Inline on desktop, stacked on mobile

#### Responsive Behavior

- **Desktop**: Horizontal layout (input + selects + button in row)
- **Mobile**: Vertical stack (input full width, selects full width, button full width)

#### Validation

- Input required (min 3 characters)
- Priority defaults to 'medium' if not selected
- Classification optional

#### Usage Example

```tsx
<TaskInput
  onSubmit={handleCreateTask}
  loading={isCreating}
/>
```

---

## Landing Page Components (`components/landing/`)

### Hero Component

**File**: `phase2-fullstack/frontend/components/landing/Hero.tsx`

**Purpose**: Landing page hero section with headline, subheadline, and CTA buttons.

#### TypeScript Interface

```typescript
interface HeroProps {
  /**
   * Main headline text
   */
  headline: string;

  /**
   * Subheadline/description text
   */
  subheadline?: string;

  /**
   * Primary CTA button text
   */
  primaryCTA: string;

  /**
   * Primary CTA handler
   */
  onPrimaryCTA: () => void;

  /**
   * Secondary CTA button text (optional)
   */
  secondaryCTA?: string;

  /**
   * Secondary CTA handler
   */
  onSecondaryCTA?: () => void;
}
```

#### Layout Specifications

```
Container: max-w-6xl mx-auto px-6 py-24
Text alignment: text-center
Headline: text-5xl md:text-6xl font-bold leading-tight
Subheadline: text-xl text-neutral-400 mt-6
CTA row: flex gap-4 justify-center mt-10
```

#### Animation

- Fade-in on page load: Headline (0ms), subheadline (100ms), CTAs (200ms)
- Stagger animation using `animate-fade-in` with delays

#### CTA Buttons

- Primary: Button variant='primary' size='lg'
- Secondary: Button variant='outline' size='lg'

#### Usage Example

```tsx
<Hero
  headline="Organize your work with total precision"
  subheadline="PremiumTask helps you manage tasks efficiently with powerful features and a beautiful interface."
  primaryCTA="Get Started Free"
  onPrimaryCTA={() => router.push('/signup')}
  secondaryCTA="Sign In"
  onSecondaryCTA={() => router.push('/login')}
/>
```

---

### FeatureCard Component

**File**: `phase2-fullstack/frontend/components/landing/FeatureCard.tsx`

**Purpose**: Feature highlight card for landing page with icon, title, and description.

#### TypeScript Interface

```typescript
interface FeatureCardProps {
  /**
   * Feature icon (Heroicon component)
   */
  icon: React.ReactNode;

  /**
   * Feature title
   */
  title: string;

  /**
   * Feature description
   */
  description: string;

  /**
   * Additional Tailwind classes
   */
  className?: string;
}
```

#### Layout Specifications

```
Base: Card component (variant='hover', padding='lg')
Flexbox layout: flex flex-col items-center text-center gap-4
Icon: w-12 h-12, text-accent-500
Title: text-xl font-semibold text-neutral-100
Description: text-neutral-400 leading-relaxed
```

#### Hover Behavior

- Inherited from Card variant='hover'
- Icon color intensifies: `hover:text-accent-400`
- Scale effect: `hover:scale-105`

#### Grid Layout (Parent)

```
Grid: grid-cols-1 md:grid-cols-3 gap-8
```

#### Usage Example

```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">
  <FeatureCard
    icon={<ShieldCheckIcon className="w-12 h-12" />}
    title="Enterprise Security"
    description="Your data is protected with bank-level encryption and security measures."
  />
  <FeatureCard
    icon={<ChartBarIcon className="w-12 h-12" />}
    title="Advanced Metrics"
    description="Track your productivity with detailed analytics and insights."
  />
  <FeatureCard
    icon={<BoltIcon className="w-12 h-12" />}
    title="Unified Workflow"
    description="Seamlessly integrate tasks, projects, and teams in one place."
  />
</div>
```

---

## Utility Functions

### `cn()` Utility (Tailwind Class Merging)

**File**: `phase2-fullstack/frontend/lib/utils.ts`

**Purpose**: Merge Tailwind classes with proper conflict resolution using `clsx` and `tailwind-merge`.

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind CSS classes with proper conflict resolution
 * @param inputs - Class values to merge
 * @returns Merged class string
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

**Usage**:
```tsx
<Button className={cn('custom-class', props.className)}>Click</Button>
```

---

## Implementation Notes

### Import Patterns

All components should use barrel exports:

```typescript
// components/ui/index.ts
export { Button } from './Button';
export { Input } from './Input';
export { Card } from './Card';
export { Tag } from './Tag';
export { Select } from './Select';

// Usage in pages
import { Button, Input, Card } from '@/components/ui';
```

### TypeScript Configuration

All components must be fully typed with TypeScript strict mode enabled. Avoid `any` types.

### Accessibility Testing

All components must pass `jest-axe` accessibility tests with zero violations.

### Performance

- Use React.memo() for components that receive stable props
- Avoid inline function definitions in JSX (use useCallback for handlers)
- Use CSS transitions (not JavaScript animations) for better performance

---

## Next Steps

1. ✅ Component contracts defined
2. ➡️ Create quickstart.md implementation guide
3. ➡️ Run `/sp.tasks` to generate atomic implementation tasks with test cases
4. ➡️ Implement components following contracts via `/sp.implement`