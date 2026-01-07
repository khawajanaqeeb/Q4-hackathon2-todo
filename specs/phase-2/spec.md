# Phase II Specification: Todo Full-Stack Web Application

## Overview

### Phase Goal
Transform the Phase I console-based todo application into a production-ready full-stack web application with:
- Multi-user support with authentication and user isolation
- Persistent cloud storage (Neon Serverless PostgreSQL ONLY - no local SQLite files)
- Modern responsive web interface (Next.js 16+ with App Router, React 19 compatible)
- RESTful API backend (FastAPI with async support)
- All Basic features: Add, View, Update, Delete, Mark Complete
- All Intermediate features: Priorities, Tags, Search, Filter, Sort
- Professional deployment (Vercel + Railway/Render)

### Evolution from Phase I
Phase I implemented a rich console application with:
- Interactive CLI using rich.Table for beautiful display
- Dataclass models (Task with title, description, completed, priority, tags, timestamps)
- CRUD operations via typer commands
- File-based persistence (JSON)
- Search, filter, and sort capabilities

Phase II extends this foundation by:
- Moving from single-user file storage to multi-user cloud database
- Replacing CLI with responsive web UI (accessible from any device)
- Adding authentication and user isolation (Better Auth with JWT)
- Implementing REST API for frontend-backend communication
- Enabling real-time updates and collaborative features
- Professional deployment for public access

### Strict PDF Compliance and Structure
This specification follows the Hackathon II PDF guidelines:
- Uses Spec-Driven Development methodology
- Implements Next.js 16+, React 19, FastAPI, SQLModel, Neon Serverless PostgreSQL
- Includes Basic + Intermediate features
- Uses Better Auth with JWT for authentication
- Deploys to Vercel (frontend) and Railway/Render (backend)

---

## Project Structure (MANDATORY)

### Directory Layout
```
specs/phase-2/spec.md (this file)
phase2-fullstack/frontend/ (Next.js application)
phase2-fullstack/backend/app/ (FastAPI application with main.py)
```

### Complete Project Tree
```
phase2-fullstack/
├── backend/                     ← Backend service root
│   ├── app/                    ← Python package (required: __init__.py)
│   │   ├── __init__.py         ← REQUIRED: Makes 'app' a Python package
│   │   ├── main.py             ← FastAPI app instance: app = FastAPI()
│   │   ├── config.py           ← Settings from environment variables
│   │   ├── database.py         ← SQLModel engine, connection pooling
│   │   ├── models/             ← SQLModel table definitions
│   │   │   ├── __init__.py     ← Export models
│   │   │   ├── user.py         ← User table model
│   │   │   └── todo.py         ← Todo table model
│   │   ├── schemas/            ← Pydantic request/response schemas
│   │   │   ├── __init__.py     ← Export schemas
│   │   │   ├── user.py         ← UserCreate, UserResponse, LoginRequest
│   │   │   └── todo.py         ← TodoCreate, TodoUpdate, TodoResponse
│   │   ├── routers/            ← API route handlers
│   │   │   ├── __init__.py     ← Export routers
│   │   │   ├── auth.py         ← /auth endpoints (register, login)
│   │   │   └── todos.py        ← /todos CRUD endpoints
│   │   ├── dependencies/       ← FastAPI dependency functions
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         ← get_current_user (JWT validation)
│   │   │   └── database.py     ← get_session (DB lifecycle)
│   │   └── utils/              ← Helper utilities
│   │       ├── __init__.py
│   │       └── security.py     ← Password hashing, JWT creation/validation
│   ├── alembic/                ← Database migrations
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/                  ← Backend test suite
│   │   ├── __init__.py
│   │   ├── conftest.py         ← Shared fixtures
│   │   ├── test_auth.py        ← Auth endpoint tests
│   │   └── test_todos.py       ← Todo CRUD tests
│   ├── scripts/                ← Utility scripts
│   │   └── seed.py             ← Optional: Database seeding
│   ├── .env                    ← Environment variables (gitignored)
│   ├── .env.example            ← Template for .env
│   ├── requirements.txt        ← Python dependencies
│   └── alembic.ini             ← Alembic configuration
│
├── frontend/                   ← Next.js frontend application
│   ├── app/                   ← Next.js App Router structure
│   │   ├── layout.tsx         ← Root layout
│   │   ├── page.tsx           ← Home page (redirects to /dashboard or /login)
│   │   ├── login/
│   │   │   └── page.tsx       ← Login page
│   │   ├── register/
│   │   │   └── page.tsx       ← Registration page
│   │   └── dashboard/
│   │       ├── layout.tsx     ← Dashboard layout (protected)
│   │       └── page.tsx       ← Main todo list with advanced task table
│   ├── components/            ← React components
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   ├── todos/
│   │   │   ├── TodoTable.tsx      ← Advanced table with search/filter/sort
│   │   │   ├── TodoCard.tsx       ← Mobile card view
│   │   │   ├── AddTaskForm.tsx    ← Add task modal
│   │   │   ├── EditTaskForm.tsx   ← Edit task form
│   │   │   ├── FilterBar.tsx      ← Advanced search/filter controls
│   │   │   └── TodoRow.tsx        ← Single todo row
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       ├── Toast.tsx
│   │       └── Spinner.tsx
│   ├── lib/
│   │   ├── api.ts              ← API client functions
│   │   ├── auth.ts             ← Auth utilities (getToken, logout)
│   │   └── utils.ts            ← Helpers (cn, formatDate)
│   ├── types/
│   │   ├── user.ts             ← User TypeScript interfaces
│   │   └── todo.ts             ← Todo TypeScript interfaces
│   ├── context/
│   │   └── AuthContext.tsx     ← Global auth state
│   ├── middleware.ts           ← Route protection (TO BE REPLACED: deprecated, use app/api/auth/proxy or server actions)
│   ├── tests/                  ← Frontend tests
│   │   ├── components/
│   │   └── integration/
│   ├── .env.local             ← Environment variable template
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
│
├── docker-compose.yml          ← Local development orchestration
└── README.md                   ← Phase II documentation
```

---

## Requirements

### Functional Requirements

#### Basic Features (CRUD + Mark Complete)
- **BASIC-1**: Users must be able to create new todo items with title, description, priority, and tags
- **BASIC-2**: Users must be able to view all their todo items in a responsive list
- **BASIC-3**: Users must be able to update any field of their todo items
- **BASIC-4**: Users must be able to delete their todo items with confirmation
- **BASIC-5**: Users must be able to mark todo items as complete/incomplete

#### Intermediate Features (Priorities/Tags, Search/Filter, Sort)
- **INT-1**: Todo items must support priority levels (low, medium, high)
- **INT-2**: Todo items must support tags (up to 10 tags per item)
- **INT-3**: Users must be able to search todo items by title content
- **INT-4**: Users must be able to filter todo items by completion status, priority, and tags
- **INT-5**: Users must be able to sort todo items by creation date, priority, or title

#### Multi-User with Better Auth JWT
- **AUTH-1**: Users must register with email (unique), password (8+ chars), and name
- **AUTH-2**: Passwords must be hashed with bcrypt (12+ rounds) before storage
- **AUTH-3**: Users must login with email + password to receive JWT token
- **AUTH-4**: JWT tokens must expire after 30 minutes (configurable), with optional refresh tokens valid for 7 days
- **AUTH-5**: All task endpoints must require valid JWT token in Authorization header
- **AUTH-6**: Frontend must store JWT securely (httpOnly cookies preferred, localStorage as fallback) and attach to all API requests
- **AUTH-7**: Frontend must redirect to /login when token is missing or expired
- **AUTH-8**: Backend must return 401 Unauthorized for invalid/expired tokens
- **AUTH-9**: Users must be able to logout (frontend clears token)
- **AUTH-10**: Email validation must prevent invalid formats (use Pydantic EmailStr)
- **AUTH-11**: JWT implementation must use HS256 algorithm with 256-bit secret key
- **AUTH-12**: Token refresh mechanism must follow security best practices (secure storage, rotation)

#### User Isolation
- **ISO-1**: Each task must be associated with exactly one user (user_id foreign key)
- **ISO-2**: Users must ONLY see their own tasks (enforce in all queries)
- **ISO-3**: Users must NOT be able to access/modify other users' tasks (403 or 404)
- **ISO-4**: API must filter all task queries by current_user.id automatically
- **ISO-5**: Database must enforce user_id foreign key constraint

### Non-Functional Requirements

#### Neon DB Only
- **NEON-1**: All tasks must be stored in Neon PostgreSQL database (NO local SQLite files)
- **NEON-2**: Database must use SSL connection (required by Neon)
- **NEON-3**: Database must use connection pooling (min 5, max 20 connections)
- **NEON-4**: All database operations must be transactional (rollback on error)
- **NEON-5**: Database schema must be managed via Alembic migrations

#### Responsive Advanced UI
- **UI-1**: Application must be responsive (mobile 320px, tablet 768px, desktop 1024px+)
- **UI-2**: Advanced task table must include columns: ID, Title, Description, Priority, Tags, Status, Created Date
- **UI-3**: Task table must support sorting by clicking column headers
- **UI-4**: Search bar must support real-time filtering as user types
- **UI-5**: Multiple filter options must be available in a collapsible sidebar
- **UI-6**: Priority must be color-coded (high: red, medium: yellow, low: green)
- **UI-7**: Tags must be displayed as colored badges/chips
- **UI-8**: Completed tasks must have strikethrough text or different styling

#### Secure API
- **SEC-1**: All passwords must be hashed with bcrypt (cost factor 12+)
- **SEC-2**: JWT secret key must be stored in environment variable (min 256 bits)
- **SEC-3**: HTTPS must be enforced in production (Vercel auto-provides)
- **SEC-4**: CORS must be configured to allow only frontend origin
- **SEC-5**: SQL injection must be prevented (use SQLModel parameterized queries)
- **SEC-6**: XSS must be prevented (React auto-escapes, validate all inputs)
- **SEC-7**: Rate limiting must be applied to login endpoint (5 attempts/min per IP)
- **SEC-8**: Sensitive data (passwords, tokens) must never appear in logs
- **SEC-9**: Database credentials must be stored in environment variables only
- **SEC-10**: JWT tokens must not contain sensitive data (only user_id, email)
- **SEC-11**: All API endpoints must return appropriate HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- **SEC-12**: Error responses must follow consistent format with message and error code
- **SEC-13**: All authentication and authorization failures must be logged for security auditing

---

## Data Model

### User Model
- `id`: Integer (auto-increment primary key)
- `email`: String (unique, indexed, max 255 chars)
- `hashed_password`: String (bcrypt hash, 60 chars)
- `name`: String (max 255 chars)
- `is_active`: Boolean (default true)
- `created_at`: DateTime (UTC, auto-generated)
- `updated_at`: DateTime (UTC, auto-updated)

### Task Model
- `id`: Integer (auto-increment primary key)
- `user_id`: Integer (foreign key to users.id, indexed, NOT NULL)
- `title`: String (required, 1-500 chars, indexed for search)
- `description`: String (optional, max 5000 chars)
- `completed`: Boolean (default false, indexed for filtering)
- `priority`: Enum('low', 'medium', 'high') (default 'medium', indexed)
- `tags`: JSON array of strings (default [], max 10 tags)
- `created_at`: DateTime (UTC, auto-generated, indexed for sorting)
- `updated_at`: DateTime (UTC, auto-updated)

---

## Database

### Neon Serverless PostgreSQL ONLY
- **Provider**: Neon Serverless PostgreSQL (no local SQLite)
- **Connection**: SSL required (enforced by Neon)
- **Pool Size**: 10 connections (min), 20 overflow (max)
- **URL Format**: `postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require`
- **Storage**: 3GB free tier (sufficient for Phase II)
- **Compute**: Auto-scaling (suspends after inactivity)

### Connection via DATABASE_URL from .env
- **Environment Variable**: `DATABASE_URL` from .env file
- **No Local Files**: Strictly prohibit local database files like `todo_app.db`
- **Connection Pooling**: Implemented with SQLModel engine
- **SSL Mode**: Required (enforced by Neon)

### No Local Files
- All data must be stored in Neon PostgreSQL
- No local SQLite files (todo_app.db, etc.)
- No file-based persistence (JSON, etc.)

---

## Authentication

### Better Auth with JWT
- **Implementation**: Better Auth with JWT tokens
- **Flow**: Register → Login → JWT Token → Protected API Access → Logout
- **Token Storage**: Frontend localStorage (with secure options)
- **Token Validation**: Backend JWT middleware

### Shared Secret between Frontend/Backend
- **SECRET_KEY**: Same secret key used by both frontend and backend
- **Token Format**: HS256 algorithm
- **Expiration**: 30 minutes (configurable)
- **Refresh**: Optional refresh token implementation

---

## Backend Architecture

### phase2-fullstack/backend/app/main.py (uvicorn app.main:app)
The backend must follow this exact structure:
```
phase2-fullstack/backend/     ← Working directory for Uvicorn
├── app/                      ← Python package (importable as 'app')
│   ├── __init__.py          ← Required: Makes 'app' a package
│   ├── main.py              ← FastAPI instance defined here as 'app'
│   ├── config.py            ← Database configuration for Neon
│   └── ...
├── requirements.txt
└── alembic.ini
```

**Critical Requirements**:
1. The file `phase2-fullstack/backend/app/__init__.py` **must exist** (can be empty)
2. The file `phase2-fullstack/backend/app/main.py` must contain:
   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Todo API", version="1.0.0")
   # ... rest of application setup
   ```
3. All imports must be relative to the `app` package:
   - ✅ Correct: `from app.routers import todos`
   - ✅ Correct: `from app.models.user import User`
   - ❌ Wrong: `from routers import todos`
   - ❌ Wrong: `from models.user import User`
4. Uvicorn must be run from `backend/` directory with: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
5. Database must use Neon PostgreSQL URL from .env (no local SQLite files)

### Standard Package Structure
- Proper Python package with `__init__.py` files
- Separation of concerns (models, schemas, routers, dependencies, utils)
- FastAPI with dependency injection
- SQLModel for database operations

---

## Frontend Architecture

### Advanced Responsive Task Table
- **Responsive Design**: Table on desktop (1024px+), cards on mobile (<768px), hybrid on tablet
- **Search Functionality**: Real-time search by title with debounced input (300ms delay)
- **Filtering**: Multi-select filters for status, priority, tags with visual chips
- **Sorting**: Click column headers to sort (ID, Title, Priority, Date) with visual indicators (arrows)
- **Actions**: Inline edit, delete, toggle complete with icon buttons and tooltips
- **Visual Indicators**: Color-coded priorities, strikethrough for completed tasks, subtle animations
- **Pagination**: 20 items per page with navigation controls and page number display
- **Hydration Error Prevention**: Proper SSR handling with useEffect for client-only code, static generation where possible, no random/Date.now() in SSR, consistent date formatting, valid HTML nesting
- **Empty States**: Attractive empty state with illustration and CTA when no tasks
- **Loading States**: Skeleton loaders during data fetch, smooth transitions

### High-Quality UI Components
- **Priority Badges**:
  - High: Red gradient with border, icon, and hover scale effect
  - Medium: Yellow/amber gradient with border and icon
  - Low: Green gradient with border and icon
  - All badges: Rounded-full, font-semibold, transition-all for smooth effects

- **Tag Pills**:
  - Multi-color system (8 colors: blue, purple, pink, indigo, green, yellow, red, gray)
  - Rounded-full shape with border
  - Hover effects (scale, brightness change)
  - Interactive (clickable to filter by tag)
  - Max 10 tags per task with overflow indicator

- **Status Indicators**:
  - Completed: Strikethrough text, reduced opacity, checkmark icon, green accent
  - Incomplete: Full opacity, checkbox unchecked, default styling
  - Toggle animation: Smooth transition between states

- **Interactive Elements**:
  - Hover states: Scale transforms, shadow changes, color shifts
  - Focus states: Ring outline for accessibility (ring-4, ring-offset-2)
  - Active states: Slight scale down for press effect
  - Disabled states: Reduced opacity, no pointer events

- **High-Quality Design Features**:
  - Modern gradients for headers and CTAs (from-blue-500 to-purple-600)
  - Consistent spacing with Tailwind scale (p-4, p-6, gap-4)
  - Smooth transitions (duration-200, duration-300)
  - Box shadows for depth (shadow-md, shadow-lg, shadow-xl)
  - Rounded corners (rounded-lg for cards, rounded-full for badges)
  - Dark mode support with class-based toggling
  - Responsive typography (text-sm on mobile, text-base on desktop)
  - Accessible color contrasts (WCAG AA compliant)

- **Form Validation UI**:
  - Real-time validation with error messages below fields
  - Success states with green checkmarks
  - Error states with red borders and error icons
  - Loading states with spinners and disabled buttons
  - Character counters for limited-length fields

---

## UI Error Fixes & Upgrades

### Fix: "[object Object]" Display Error
- **Issue**: Form labels and UI text showing "[object Object]" instead of actual values
- **Root Cause**: Rendering JavaScript objects directly in JSX text nodes instead of strings
- **Common Patterns That Cause This Error**:
  ```tsx
  // ❌ WRONG - Renders "[object Object]"
  <label>{user}</label>                    // user is an object
  <span>{formData}</span>                  // formData is an object
  <p>Priority: {task.priority}</p>         // if task.priority is an object
  <div>{tags}</div>                        // if tags is an array of objects

  // ✅ CORRECT - Renders actual values
  <label>{user.name}</label>               // Access string property
  <span>{formData.email}</span>            // Access string property
  <p>Priority: {task.priority.level}</p>   // Access nested string
  <div>{tags.map(t => t.name).join(', ')}</div>  // Convert to strings
  ```

- **Solution Requirements**:
  1. **Never render objects directly**: Always access specific string properties
  2. **For arrays of objects**: Map to string properties or use .map() to render components
  3. **For debugging**: Use `JSON.stringify(obj, null, 2)` in `<pre>` tags only for development
  4. **Type checking**: Use TypeScript to catch these errors at compile time
  5. **Validation**: Add runtime checks for object types before rendering

- **Implementation Checklist**:
  - [ ] Audit all form labels to ensure they use `user.name`, `user.email` (not `user`)
  - [ ] Check all task displays use `task.title`, `task.description` (not `task`)
  - [ ] Verify priority displays use string values like `task.priority` as enum string (not object)
  - [ ] Ensure tags render as `tags.map(tag => <span key={tag}>{tag}</span>)` (not `{tags}`)
  - [ ] Add TypeScript strict mode to catch object-in-text-node errors
  - [ ] Test all forms with real data to verify no "[object Object]" appears

### React Hydration Error Resolution
- **Issue**: "A tree hydrated but some attributes didn't match" error occurs when server-rendered HTML doesn't match client expectations
- **Root Cause**: Client/server branch usage, variable input like Date.now(), date formatting in locale, external data without snapshot, invalid HTML nesting, or browser extensions
- **Solution Requirements**:
  - Use useEffect for client-only code to prevent SSR conflicts
  - Implement static generation where possible
  - Avoid random/Date.now() in SSR components
  - Ensure consistent date formatting between server and client
  - Maintain valid HTML nesting structure
  - Handle locale-specific formatting properly

### High-Quality Frontend UI Upgrade Requirements

#### Design System Foundation
- **Color Palette**: Define primary, secondary, accent, success, warning, error colors with dark mode variants
- **Typography Scale**: Establish consistent font sizes (text-xs to text-4xl), line heights, and font weights
- **Spacing System**: Use Tailwind's spacing scale consistently (space-1 to space-16)
- **Border Radius**: Standard radius values (rounded-sm, rounded-md, rounded-lg, rounded-xl)
- **Shadows**: Elevation system with shadow-sm, shadow-md, shadow-lg, shadow-xl

#### Modern Component Styling

**Task Table (Desktop)**:
```tsx
// High-quality table with modern design
<table className="w-full border-collapse bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-lg">
  <thead className="bg-gradient-to-r from-blue-500 to-purple-600 text-white">
    <tr>
      <th className="px-6 py-4 text-left font-semibold text-sm uppercase tracking-wider hover:bg-blue-600 cursor-pointer transition-colors">
        Title
      </th>
      {/* More columns with same styling */}
    </tr>
  </thead>
  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
    <tr className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150">
      {/* Row content */}
    </tr>
  </tbody>
</table>
```

**Task Cards (Mobile)**:
```tsx
// Beautiful responsive cards for mobile view
<div className="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 p-6 border border-gray-200 dark:border-gray-700">
  <div className="flex items-start justify-between mb-4">
    <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate flex-1">
      {task.title}
    </h3>
    <PriorityBadge priority={task.priority} />
  </div>
  {/* More card content */}
</div>
```

**Priority Badges with Enhanced Styling**:
```tsx
// Color-coded priority badges with modern design
const priorityStyles = {
  high: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200'
};

<span className={`px-3 py-1 rounded-full text-xs font-semibold border ${priorityStyles[priority]} transition-all hover:scale-105`}>
  {priority.toUpperCase()}
</span>
```

**Tag Pills with Interactive Design**:
```tsx
// Colorful, interactive tag pills
const tagColors = ['blue', 'purple', 'pink', 'indigo', 'green', 'yellow', 'red', 'gray'];

<div className="flex flex-wrap gap-2">
  {tags.map((tag, index) => (
    <span
      key={tag}
      className={`px-3 py-1 rounded-full text-xs font-medium bg-${tagColors[index % tagColors.length]}-100 text-${tagColors[index % tagColors.length]}-700 border border-${tagColors[index % tagColors.length]}-300 hover:bg-${tagColors[index % tagColors.length]}-200 transition-colors cursor-pointer`}
    >
      {tag}
    </span>
  ))}
</div>
```

**Form Inputs with Modern Styling**:
```tsx
// Beautiful form inputs with focus states
<input
  type="text"
  className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 transition-all outline-none"
  placeholder="Enter task title..."
/>
```

**Buttons with Visual Feedback**:
```tsx
// Primary button with hover and active states
<button className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg shadow-md hover:shadow-xl hover:scale-105 active:scale-95 transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-blue-500/50">
  Add Task
</button>

// Secondary button
<button className="px-6 py-3 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 font-semibold rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 transition-all duration-200">
  Cancel
</button>

// Danger button
<button className="px-6 py-3 bg-red-500 text-white font-semibold rounded-lg shadow-md hover:bg-red-600 hover:shadow-xl hover:scale-105 active:scale-95 transition-all duration-200">
  Delete
</button>
```

#### Dark Mode Implementation
```tsx
// Dark mode toggle with smooth transition
<button
  onClick={toggleDarkMode}
  className="p-3 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-300"
>
  {isDark ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
</button>

// Add to tailwind.config.js
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  // ... rest of config
}

// Add to root layout
<html className={isDarkMode ? 'dark' : ''}>
```

#### Animations & Transitions
- **Page Transitions**: Smooth fade-in on route changes (200ms ease-in-out)
- **List Animations**: Stagger animation for task list items (framer-motion or CSS)
- **Modal Animations**: Scale and fade animations for dialogs
- **Loading States**: Skeleton screens and spinners with pulse animation
- **Micro-interactions**: Button press effects, hover scale transforms, ripple effects

#### Toast Notifications
```tsx
// Beautiful toast notifications
<div className="fixed top-4 right-4 z-50 animate-slide-in-right">
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl border-l-4 border-green-500 p-4 flex items-center gap-3 min-w-[300px]">
    <CheckCircleIcon className="w-6 h-6 text-green-500" />
    <div>
      <p className="font-semibold text-gray-900 dark:text-white">Success</p>
      <p className="text-sm text-gray-600 dark:text-gray-400">Task created successfully</p>
    </div>
  </div>
</div>
```

#### Responsive Layout
- **Mobile (320px-767px)**: Single column, card layout, bottom navigation, hamburger menu
- **Tablet (768px-1023px)**: Two-column grid, condensed table, side navigation
- **Desktop (1024px+)**: Full table view, sidebar filters, multi-column layout

#### UI Requirements Checklist
- [ ] Implement consistent color palette with dark mode support
- [ ] Use gradient backgrounds for headers and primary CTAs
- [ ] Add hover effects to all interactive elements (scale, shadow, color)
- [ ] Implement smooth transitions (200-300ms) for all state changes
- [ ] Use rounded corners consistently (rounded-lg for cards, rounded-full for badges)
- [ ] Add drop shadows for depth (shadow-md for cards, shadow-lg for modals)
- [ ] Implement loading skeletons for async content
- [ ] Add empty states with illustrations and helpful CTAs
- [ ] Use icons consistently (Heroicons or Lucide React recommended)
- [ ] Implement toast notifications for user feedback
- [ ] Add confirmation modals for destructive actions
- [ ] Ensure all forms have proper validation states (error borders, success checkmarks)
- [ ] Implement dark mode toggle with smooth transition
- [ ] Add keyboard shortcuts for power users
- [ ] Ensure WCAG 2.1 AA accessibility compliance

---

## Middleware Migration: From 'middleware' to 'proxy'

### Issue: Next.js Middleware Deprecation
- **Problem**: The "middleware" file convention is deprecated in Next.js
- **Warning**: "The 'middleware' file convention is deprecated. Please use 'proxy' instead."
- **Impact**: Current `middleware.ts` file needs to be replaced with the new proxy pattern

### Solution: Proxy Pattern Implementation
- **Replace**: `middleware.ts` with API routes or server actions for auth protection
- **New Approach**: Use `app/api/auth/proxy/route.ts` or server actions for route protection
- **Auth Protection**: Implement authentication checks using Next.js App Router server components
- **Route Guarding**: Use server-side authentication in layout.tsx or page.tsx files

### Migration Requirements
- **Remove**: Legacy `middleware.ts` file after implementing proxy pattern
- **Implement**: API route handlers using the new proxy approach
- **Preserve**: All existing authentication and route protection functionality
- **Test**: Ensure all protected routes continue to work as expected

---

## API Endpoints

### Table of Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create new user with email, password, name |
| POST | `/auth/login` | No | Login user with email, password, return JWT |
| GET | `/todos` | Yes | Get all user's todos with query params |
| POST | `/todos` | Yes | Create new todo item |
| GET | `/todos/{id}` | Yes | Get single todo item |
| PUT | `/todos/{id}` | Yes | Update todo item |
| DELETE | `/todos/{id}` | Yes | Delete todo item |
| POST | `/todos/{id}/toggle` | Yes | Toggle completed status |

### Query Parameters for GET /todos
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 | Max results (max 100) |
| `completed` | bool | null | Filter by completion status |
| `priority` | str | null | Filter by priority (low/medium/high) |
| `search` | str | null | Search in title (case-insensitive) |
| `sort_by` | str | created_at | Sort field (created_at, priority, title) |
| `sort_order` | str | desc | Sort direction (asc/desc) |

---

## Feature Specifications

### Feature 1: User Registration
**User Story**: As a new user, I want to create an account so that I can manage my personal todo list.

**UI Description**:
- Page route: `/register`
- Form fields with proper JSX rendering:
  ```tsx
  // ✅ CORRECT - Render string values, not objects
  <input
    name="name"
    value={formData.name}  // String property, not formData object
    onChange={(e) => setFormData({...formData, name: e.target.value})}
    placeholder="Enter your name"
  />
  <input
    name="email"
    type="email"
    value={formData.email}  // String property, not formData object
    onChange={(e) => setFormData({...formData, email: e.target.value})}
    placeholder="Enter your email"
  />
  <input
    name="password"
    type="password"
    value={formData.password}  // String property, not formData object
    onChange={(e) => setFormData({...formData, password: e.target.value})}
    placeholder="Enter password (min 8 chars)"
  />
  // Display user feedback with strings only
  {error && <p className="text-red-600">{error.message}</p>}  // error.message, not error
  {user && <p>Welcome, {user.name}!</p>}  // user.name, not user
  ```
- Form fields: Name (text input, required, max 255 chars), Email (email input, required, unique), Password (password input, required, min 8 chars, show strength), Confirm password
- Submit button with loading state and proper disabled attribute
- Link to login page with proper href
- Error display for duplicate email or validation failures using error.message strings
- **CRITICAL**: All form labels, placeholders, and error messages must render string values, never objects

**API Description**:
- Endpoint: POST /auth/register
- Request: `{email, password, name}`
- Response: `{id, email, name, created_at}`
- Status: 201 Created, 400 Bad Request (duplicate email)

### Feature 2: User Login
**User Story**: As a registered user, I want to log in so that I can access my todo list.

**UI Description**:
- Page route: `/login`
- Form fields: Email (email input, required), Password (password input, required)
- Submit button with loading state
- Link to registration page
- Error display for invalid credentials

**API Description**:
- Endpoint: POST /auth/login
- Request: `{email, password}`
- Response: `{access_token, token_type}`
- Status: 200 OK, 401 Unauthorized (invalid credentials)

### Feature 3: Advanced Task Table
**User Story**: As a user, I want to see all my tasks in an organized table with advanced features so that I can efficiently manage them.

**UI Description**:
- Page route: `/dashboard`
- Advanced table with columns: ID, Title, Description, Priority, Tags, Status, Created Date
- Search bar for real-time filtering
- Filter sidebar with status, priority, and tags filters
- Sortable column headers
- Action buttons (edit, delete, toggle) for each row
- Pagination controls

**API Description**:
- Endpoint: GET /todos
- Query parameters: skip, limit, completed, priority, search, sort_by, sort_order
- Response: `[{id, title, description, completed, priority, tags, created_at}, ...]`
- Status: 200 OK

### Feature 4: Create Task
**User Story**: As a user, I want to add new tasks so that I can track things I need to do.

**UI Description**:
- Trigger: "Add Task" button opening modal/form
- Form fields with proper JSX rendering:
  ```tsx
  // ✅ CORRECT - Always use string values in JSX
  <input
    value={formData.title}  // String property
    onChange={(e) => setFormData({...formData, title: e.target.value})}
  />
  <select
    value={formData.priority}  // String enum: 'low' | 'medium' | 'high'
    onChange={(e) => setFormData({...formData, priority: e.target.value})}
  >
    <option value="low">Low</option>
    <option value="medium">Medium</option>
    <option value="high">High</option>
  </select>

  // ✅ CORRECT - Render tags as string array
  <div className="flex flex-wrap gap-2">
    {formData.tags.map((tag, index) => (
      <span key={index} className="px-2 py-1 bg-blue-100 rounded-full">
        {tag}  {/* String value, not object */}
      </span>
    ))}
  </div>

  // ❌ WRONG - Never do this
  <div>{formData}</div>  // Shows "[object Object]"
  <div>{formData.tags}</div>  // Shows "tag1,tag2,tag3" (array toString)
  ```
- Form fields: Title (required, 1-500 chars), Description (optional), Priority (dropdown low/medium/high), Tags (multi-select or comma-separated)
- Save and Cancel buttons with proper event handlers
- Loading state on submit with disabled form during submission
- **CRITICAL**: Priority must render as string enum ('low'|'medium'|'high'), tags must map to individual span elements

**API Description**:
- Endpoint: POST /todos
- Request: `{title, description?, priority?, tags?}`
- Response: `{id, title, description, completed, priority, tags, created_at, updated_at}`
- Status: 201 Created, 400 Bad Request (validation), 401 Unauthorized

### Feature 5: Update Task
**User Story**: As a user, I want to edit my tasks so that I can update details or fix mistakes.

**UI Description**:
- Trigger: Edit button on task row
- Inline edit form or modal with pre-filled values
- All fields editable (title, description, priority, tags, completed)
- Save and Cancel buttons
- Loading state on save

**API Description**:
- Endpoint: PUT /todos/{id}
- Request: `{title?, description?, priority?, tags?, completed?}`
- Response: `{id, title, description, completed, priority, tags, updated_at}`
- Status: 200 OK, 400 Bad Request (validation), 401 Unauthorized, 404 Not Found

### Feature 6: Delete Task
**User Story**: As a user, I want to delete tasks so that I can remove items I no longer need.

**UI Description**:
- Trigger: Delete button on task row
- Confirmation dialog with warning message
- Confirm and Cancel buttons
- Loading state on confirm

**API Description**:
- Endpoint: DELETE /todos/{id}
- Response: `null`
- Status: 204 No Content, 401 Unauthorized, 404 Not Found

### Feature 7: Toggle Complete
**User Story**: As a user, I want to mark tasks as complete/incomplete so that I can track my progress.

**UI Description**:
- Trigger: Checkbox in task row
- Visual indication of completion status (strikethrough, color change)
- Optimistic update for immediate feedback

**API Description**:
- Endpoint: POST /todos/{id}/toggle
- Response: `{id, completed, updated_at}`
- Status: 200 OK, 401 Unauthorized, 404 Not Found

---

## Setup & Running

### Use Existing .env (CRITICAL: Preserve and Use Correctly)
- Preserve existing .env file with Neon DATABASE_URL (never overwrite or ignore)
- Use the same DATABASE_URL for Neon PostgreSQL connection (no local SQLite files)
- Ensure .env file is properly loaded in all environments (development, testing, production)
- Environment variables must be loaded before application startup
- All sensitive data (DATABASE_URL, SECRET_KEY) must be stored in environment variables only
- Never hardcode sensitive information in source code

### Correct Uvicorn Command
- Navigate to `phase2-fullstack/backend/` directory
- Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- This imports the 'app' object from 'app.main' module
- The 'app' directory must contain __init__.py to be a Python package
- The 'main.py' file must contain the FastAPI instance as 'app'

### Development Setup
```bash
# 1. Clone repository
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo

# 2. Backend setup
cd phase2-fullstack/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment (use existing .env with Neon DATABASE_URL)
# Ensure DATABASE_URL points to your Neon PostgreSQL instance
# SECRET_KEY should be a 256-bit secret

# 4. Run database migrations
alembic upgrade head

# 5. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Frontend setup (in new terminal)
cd phase2-fullstack/frontend
npm install

# 7. Configure frontend environment
# NEXT_PUBLIC_API_URL=http://localhost:8000

# 8. Start frontend server
npm run dev
```

---

## Acceptance Criteria

### Works with Neon DB
- ✅ All data stored in Neon PostgreSQL database
- ✅ No local SQLite files used
- ✅ Database connection uses SSL
- ✅ Connection pooling configured
- ✅ Migrations managed via Alembic

### Correct Structure
- ✅ All code in phase2-fullstack/ directory
- ✅ Backend in phase2-fullstack/backend/app/
- ✅ Frontend in phase2-fullstack/frontend/
- ✅ Specification in specs/phase-2/spec.md
- ✅ Proper Python package structure with __init__.py files

### Advanced Frontend
- ✅ Responsive task table with ID, Title, Description, Priority, Tags, Status, Created Date
- ✅ Real-time search functionality
- ✅ Multiple filter options (status, priority, tags)
- ✅ Sortable columns with click-to-sort
- ✅ Priority color coding (red/yellow/green)
- ✅ Tag chips display
- ✅ Completed task visual indicators

### Git Tagged v2.0-phase2
- [ ] Create git tag v2.0-phase2 when Phase II is complete
- [ ] Tag includes all Phase II features
- [ ] Tag represents stable, working version

---

## Deployment & Environment

### Deployment Targets

**Frontend (Vercel)**:
- Framework: Next.js (auto-detected)
- Build command: `npm run build`
- Output directory: `.next`
- Environment variables:
  - `NEXT_PUBLIC_API_URL`: Backend API URL (Railway/Render)
- Domain: `your-app.vercel.app` (custom domain optional)

**Backend (Railway or Render)**:
- Runtime: Python 3.11
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
  - `ALGORITHM`: HS256
  - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30
  - `DEBUG`: false (production)
- Health check: `GET /health`

**Database (Neon)**:
- Region: Auto (closest to backend)
- Connection string format: `postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`
- Compute: Auto-scale (suspend after inactivity)
- Storage: 3GB free tier
- Backups: Automatic daily

### Environment Variables

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

**Backend (.env)**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
SECRET_KEY=your-256-bit-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=false
CORS_ORIGINS=https://your-app.vercel.app
```

### Deployment Steps

**1. Deploy Database (Neon)**:
```bash
# Create Neon project at neon.tech
# Copy connection string
# Run migrations
alembic upgrade head
```

**2. Deploy Backend (Railway)**:
```bash
# Connect GitHub repo to Railway
# Add environment variables
# Deploy from main branch
# Verify health check: https://your-backend.railway.app/health
```

**3. Deploy Frontend (Vercel)**:
```bash
# Connect GitHub repo to Vercel
# Add NEXT_PUBLIC_API_URL environment variable
# Deploy from main branch
# Verify app loads: https://your-app.vercel.app
```

---

## Testing Requirements

### Backend Testing (pytest)

**Target Coverage**: 80%+

**Test Categories**:
1. **Unit Tests** (`tests/test_models.py`, `tests/test_utils.py`):
   - Model validation (Pydantic schemas)
   - Password hashing/verification
   - JWT token creation/decoding

2. **API Tests** (`tests/test_auth.py`, `tests/test_todos.py`):
   - Registration (valid, duplicate email, weak password)
   - Login (valid, invalid credentials, rate limiting)
   - CRUD operations (create, read, update, delete)
   - User isolation (user A cannot access user B's tasks)
   - Filtering, searching, sorting
   - Edge cases (invalid IDs, unauthorized access)

3. **Integration Tests**:
   - Full flow: register → login → create task → update → delete
   - Database transactions (rollback on error)

**Testing Dependencies**:
- pytest: Latest stable version
- pytest-cov: For coverage reports
- pytest-asyncio: For async tests
- All testing dependencies must be compatible with Python 3.11+

**Example Test**:
```python
def test_create_todo_requires_auth(client):
    response = client.post("/todos", json={"title": "Test"})
    assert response.status_code == 401

def test_user_isolation(client, auth_headers_user1, auth_headers_user2):
    # User 1 creates task
    response = client.post("/todos", json={"title": "User 1 task"}, headers=auth_headers_user1)
    task_id = response.json()["id"]

    # User 2 tries to access it
    response = client.get(f"/todos/{task_id}", headers=auth_headers_user2)
    assert response.status_code == 404  # Not found (user isolation)
```

**Run Tests**:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

**Testing Configuration**:
- All tests must run successfully in cross-platform environments (Windows, macOS, Linux)
- Test database connections must use Neon PostgreSQL (no SQLite for testing)
- Test fixtures and setup must be compatible with async operations
- Test coverage reports must meet 80%+ requirement

### Frontend Testing (Jest + React Testing Library)

**Target Coverage**: 70%+

**Test Categories**:
1. **Component Tests**:
   - LoginForm renders and submits
   - TodoTable displays tasks
   - FilterBar updates filters
   - AddTaskForm validation

2. **Integration Tests**:
   - Full flow: login → view tasks → add task → edit → delete
   - Filter + sort combinations

**Testing Dependencies**:
- Jest: Latest stable version compatible with React 19
- @testing-library/react: `^15.0.0` or latest (mandatory for React 19 compatibility)
- @testing-library/jest-dom: Latest stable version
- @testing-library/user-event: Latest stable version
- All testing dependencies must be compatible with React 19 ecosystem

**Example Test**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import LoginForm from '@/components/auth/LoginForm';

test('login form submits with valid data', async () => {
  const onSubmit = jest.fn();
  render(<LoginForm onSubmit={onSubmit} />);

  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: 'password123' }
  });
  fireEvent.click(screen.getByRole('button', { name: /log in/i }));

  expect(onSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123'
  });
});
```

**Dependency Requirements**:
- Frontend must use React 19 compatible testing libraries: `@testing-library/react@^15.0.0` or latest
- All testing dependencies must be compatible with React 19
- No deprecated APIs or patterns from older React versions

**Run Tests**:
```bash
npm run test -- --coverage
```

### Dependency Version Requirements

**Frontend Dependencies**:
- Next.js: `^16.0.0` or latest stable
- React: `^19.0.0` (mandatory for compatibility)
- React DOM: `^19.0.0` (mandatory for compatibility)
- @testing-library/react: `^15.0.0` or latest (mandatory for React 19 compatibility)
- All other dependencies must be compatible with React 19 ecosystem

**Backend Dependencies**:
- Python: `3.11+` (minimum)
- FastAPI: Latest stable
- SQLModel: Latest stable
- All dependencies specified in requirements.txt with pinned versions for stability

### E2E Testing (Playwright)

**Critical Flows**:
1. User registration and login
2. Create task → view in list → edit → mark complete → delete
3. Search and filter tasks
4. Responsive behavior (mobile, tablet, desktop)

**Testing Dependencies**:
- Playwright: Latest stable version
- @playwright/test: Latest stable version
- All E2E testing dependencies must be compatible with React 19 and Next.js 16+

**Example Test**:
```typescript
import { test, expect } from '@playwright/test';

test('full task CRUD flow', async ({ page }) => {
  // Register
  await page.goto('/register');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.fill('[name="name"]', 'Test User');
  await page.click('button[type="submit"]');

  // Login
  await expect(page).toHaveURL('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'SecurePass123');
  await page.click('button[type="submit"]');

  // Dashboard
  await expect(page).toHaveURL('/dashboard');

  // Create task
  await page.click('text=Add Task');
  await page.fill('[name="title"]', 'Buy groceries');
  await page.selectOption('[name="priority"]', 'high');
  await page.click('text=Save');

  // Verify in list
  await expect(page.locator('text=Buy groceries')).toBeVisible();

  // Edit task
  await page.click('[aria-label="Edit task"]');
  await page.fill('[name="title"]', 'Buy groceries and cook dinner');
  await page.click('text=Save');

  // Mark complete
  await page.click('[aria-label="Mark complete"]');
  await expect(page.locator('text=Buy groceries and cook dinner')).toHaveClass(/line-through/);

  // Delete task
  await page.click('[aria-label="Delete task"]');
  await page.click('text=Confirm');
  await expect(page.locator('text=Buy groceries')).not.toBeVisible();
});
```

**Run E2E Tests**:
```bash
npx playwright test
```

**Cross-Platform Testing**:
- All E2E tests must pass on Windows, macOS, and Linux
- Browser compatibility: Chrome, Firefox, and Safari (where applicable)
- Responsive testing across device sizes

---

## Setup & Running Locally

### Prerequisites
- **Node.js**: 18+ (for Next.js frontend, Node 20+ recommended for React 19 compatibility)
- **Python**: 3.11+ (for FastAPI backend)
- **PostgreSQL**: Neon account (no local SQLite files allowed)
- **Git**: For version control
- **Operating System**: Cross-platform support (Windows, macOS, Linux) - all scripts must be compatible

### Troubleshooting Hydration Errors
- **Issue**: "A tree hydrated but some attributes didn't match" error
- **Common Causes**:
  - Using Date.now() or other client-side only code during SSR
  - Inconsistent date formatting between server and client
  - Invalid HTML nesting in components
  - Using browser APIs during server-side rendering
- **Solutions**:
  - Wrap client-only code in useEffect hooks
  - Use dynamic imports with ssr: false for components that use browser APIs
  - Ensure consistent formatting for dates and times
  - Validate HTML structure in components
  - Check for any random values generated during SSR

### Troubleshooting Middleware Deprecation
- **Issue**: "The 'middleware' file convention is deprecated. Please use 'proxy' instead."
- **Solution**: Migrate from middleware.ts to the new proxy pattern using API routes or server actions
- **Migration Steps**:
  - Replace middleware.ts with API route handlers in app/api/ directory
  - Use server actions for authentication checks instead of middleware
  - Implement route protection using server components in layout.tsx
  - Test all protected routes to ensure authentication still works

### Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/khawajanaqeeb/Q4-hackathon2-todo.git
cd Q4-hackathon2-todo/phase2-fullstack/backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (IMPORTANT: Use Neon PostgreSQL URL, NO local SQLite files)
cat > .env << EOF
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/neondb?sslmode=require
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
EOF

# IMPORTANT: Ensure no local SQLite files are created during development
# All data must be stored in Neon PostgreSQL database only

# 5. Run migrations
alembic upgrade head

# 6. (Optional) Seed database
python scripts/seed.py

# 7. Start server (IMPORTANT: Must be run from backend/ directory)
# Ensure you are in phase2-fullstack/backend/ before running this command
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
#        ^^^^^^^^^^^
#        Imports 'app' instance from 'app.main' module
#        Requires: phase2-fullstack/backend/app/__init__.py (makes 'app' a package)
#                  phase2-fullstack/backend/app/main.py (contains 'app = FastAPI()')
```

Backend runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

**Troubleshooting ModuleNotFoundError**:
- If you see "ModuleNotFoundError: No module named 'app'":
  1. Verify you're in the `phase2-fullstack/backend/` directory (not `phase2-fullstack/`)
  2. Verify `app/__init__.py` exists (can be empty, but must exist)
  3. Verify `app/main.py` exists and contains `app = FastAPI(...)`
  4. Check that all imports in your code use `from app.xxx import yyy` pattern

**Windows-Specific Troubleshooting**:
- Use PowerShell or Command Prompt instead of Git Bash for Windows compatibility
- Ensure Python virtual environment is activated: `venv\Scripts\activate` (not `source venv/bin/activate`)
- Use Windows-style paths in all commands
- Ensure all scripts and dependencies are cross-platform compatible
- Check that line endings are consistent (CRLF vs LF) across all files

### Frontend Setup

```bash
# 1. Navigate to frontend (from project root or backend directory)
cd phase2-fullstack/frontend
# OR from backend: cd ../frontend

# 2. Install dependencies
npm install

# 3. Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# 4. Start development server
npm run dev
```

Frontend runs at `http://localhost:3000`

### Verify Setup

1. Open `http://localhost:3000`
2. Click "Sign up" → Create account
3. Login with credentials
4. Add a test task
5. Verify task appears in list
6. Test search, filter, and sort
7. Mark task complete and delete

---

## Assumptions

1. **Users have unique email addresses** (enforced by database constraint)
2. **Tasks belong to exactly one user** (no shared/collaborative tasks in Phase II)
3. **Tags are simple strings** (no tag management UI, users type tags manually)
4. **No task due dates** (future enhancement)
5. **No file attachments** (Phase II focuses on text-based tasks)
6. **No real-time collaboration** (no WebSockets, users see their own data only)
7. **No offline support** (requires internet connection, future enhancement)
8. **No email verification** (users can register and login immediately)
9. **No password reset** (future enhancement)
10. **No user profile editing** (name/email fixed after registration)
11. **No task archiving** (tasks are either active or deleted)
12. **No notifications** (no email/push notifications for task updates)
13. **No recurring tasks** (each task is one-time)
14. **Frontend assumes modern browsers** (ES2020+, no IE11 support)
15. **Neon PostgreSQL is the only database** (no local SQLite files)

---

## Success Metrics

**Technical Metrics**:
- Backend test coverage: 80%+
- Frontend test coverage: 70%+
- API response time: <200ms (p95)
- Page load time: <3 seconds for initial render
- Concurrent user support: 1000+ simultaneous users
- Lighthouse performance: 90+
- Lighthouse accessibility: 95+
- Zero critical security vulnerabilities (OWASP Top 10)

**Functional Metrics**:
- All 10 features implemented and tested
- User isolation verified (security testing)
- Responsive on 3 device sizes (mobile, tablet, desktop)
- Deployment successful (Vercel + Railway + Neon)
- API documentation complete (FastAPI auto-docs)

**User Experience Metrics**:
- User can register, login, and create first task in <2 minutes
- Task CRUD operations complete in <3 clicks
- No blocking bugs in critical flows
- Error messages clear and actionable

---

## Next Steps (Post Phase II)

Future enhancements for Phase III or beyond:
- Task due dates and reminders
- Recurring tasks (daily, weekly, monthly)
- Task categories/projects
- Collaboration (shared tasks, team workspaces)
- File attachments
- Calendar view
- Mobile apps (React Native)
- Offline support (Service Workers, sync)
- Email notifications
- Password reset flow
- User profile editing
- Dark mode
- Keyboard shortcuts
- Task templates
- Time tracking
- Analytics dashboard (task completion rates, productivity trends)

---

## Clarifications

### Session 2026-01-03
- Q: What are specific performance targets? → A: API response time <200ms p95, page load time <3s, support 1000+ concurrent users
- Q: What are specific JWT security requirements? → A: HS256 algorithm, 256-bit secret, 30-min expiration with refresh tokens, secure storage
- Q: What are error handling and logging requirements? → A: Standard HTTP status codes, consistent error format, audit logging for auth failures

## Next Steps

### Implementation Path
1. **/sp.plan** → Generate implementation plan based on this specification
2. **/sp.tasks** → Generate atomic task breakdown for implementation
3. **/sp.implement** → Execute implementation using agents and skills

### Use Agents/Skills
- **Agents**: Use reusable agents for complex tasks (database schema, API endpoints, UI components)
- **Skills**: Use building block skills for specific features (auth setup, UI generation, DB design)
- **Subagents**: Delegate complex subtasks to specialized agents
- **Building Blocks**: Assemble features from existing skills

### Reusable Intelligence
- **hackathon-nextjs-builder**: Generate frontend components
- **hackathon-fastapi-master**: Build backend API endpoints
- **hackathon-db-architect**: Design database schemas
- **hackathon-auth-specialist**: Implement authentication
- **hackathon-integration-tester**: Create full-stack tests
- **nextjs-ui-generator**: Generate UI components
- **fastapi-endpoint-builder**: Build API endpoints
- **sqlmodel-db-designer**: Create database models
- **better-auth-setup**: Implement authentication
- **fullstack-consistency-checker**: Verify API contracts

This specification provides a comprehensive blueprint for implementing Phase II of the todo application with all corrections and improvements. All agents and skills referenced are available in `.claude/agents/` and `.claude/skills/` directories.