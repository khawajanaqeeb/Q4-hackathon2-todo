# Phase II Research & Technology Decisions

**Date**: 2026-01-03
**Feature**: Phase II Full-Stack Web Application
**Spec**: [specs/phase-2/spec.md](./spec.md)

## Executive Summary

This document consolidates research findings for the Phase II Full-Stack Web Application. All technology decisions are pre-specified by the Hackathon II requirements and project constitution, with this document providing the rationale and best practices for each technology choice.

## 1. Frontend Framework: Next.js 16+ with App Router

**Decision**: Next.js 16+ (App Router, TypeScript, Tailwind CSS)

**Rationale**:
- Server components for improved performance and SEO
- Built-in routing with file-system based structure
- Automatic code splitting and optimization
- Excellent developer experience with hot reload
- TypeScript support out-of-the-box
- Tailwind CSS integration for rapid UI development
- Vercel deployment optimization (same company)

**Alternatives Considered**: Create React App (deprecated), Vite + React (requires more setup)

**Best Practices**:
- Use App Router (not Pages Router) for server components
- Implement route protection via middleware.ts
- Store JWT in httpOnly cookies OR localStorage (localStorage chosen for simplicity)
- Use React Server Components where possible, Client Components only when needed
- Implement error boundaries for graceful error handling
- Use loading.tsx and error.tsx for better UX

## 2. Frontend Compatibility: React 19

**Decision**: React 19 compatibility with Next.js 16+

**Rationale**:
- Latest React features and performance improvements
- Compatibility with Next.js 16+ App Router
- Modern React patterns and hooks
- Better TypeScript integration
- Future-proofing for upcoming features

**Testing Library Compatibility**:
- @testing-library/react@^15.0.0 or latest (mandatory for React 19 compatibility)
- All testing dependencies must be compatible with React 19 ecosystem
- No deprecated APIs or patterns from older React versions

## 3. Backend Framework: FastAPI with SQLModel

**Decision**: FastAPI 0.100+ with SQLModel ORM

**Rationale**:
- Async/await support for high-performance I/O operations
- Automatic OpenAPI documentation generation
- Type hints with Pydantic for request/response validation
- SQLModel combines SQLAlchemy + Pydantic for type-safe database operations
- Excellent integration with PostgreSQL via asyncpg
- Dependency injection system for clean architecture
- Built-in validation and serialization

**Alternatives Considered**: Django REST Framework (heavier, synchronous), Flask (requires more boilerplate)

**Best Practices**:
- Use dependency injection for database sessions and authentication
- Implement proper CORS configuration for frontend-backend communication
- Use Alembic for database migrations (version control for schema)
- Separate models (database tables) from schemas (request/response)
- Use HTTPException with proper status codes
- Implement rate limiting for auth endpoints

## 4. Database: Neon Serverless PostgreSQL

**Decision**: Neon PostgreSQL with connection pooling

**Rationale**:
- Serverless architecture (auto-scaling, auto-pause)
- Generous free tier (3GB storage)
- SSL required by default (security)
- Fully managed (no infrastructure maintenance)
- PostgreSQL 15 features (JSONB for tags array)
- Excellent for development and small-scale production

**Alternatives Considered**: Railway PostgreSQL (more expensive), Supabase (includes unnecessary features)

**Best Practices**:
- Use connection pooling (SQLAlchemy engine pool_size=10, max_overflow=20)
- Always use parameterized queries (SQLModel handles this)
- Create indexes on foreign keys and frequently queried columns
- Use database constraints for data integrity (UNIQUE, NOT NULL, CHECK)
- Enable SSL mode (required by Neon)
- Use Alembic migrations for schema changes (never manual SQL)

## 5. Authentication: JWT with Better Auth

**Decision**: JWT tokens with python-jose + passlib for bcrypt

**Rationale**:
- Stateless authentication (no server-side session storage)
- Secure password hashing with bcrypt (cost factor 12+)
- Token-based auth works well with REST APIs
- Frontend can easily attach tokens to requests
- 30-minute expiry reduces attack surface

**Alternatives Considered**: Session-based auth (requires session store), OAuth2 (overkill for Phase II)

**Best Practices**:
- Store JWT secret in environment variable (min 256 bits)
- Use HS256 algorithm (symmetric signing)
- Include minimal claims in JWT (user_id, email, expiry)
- Implement token expiry and validation on every request
- Use HTTPBearer security scheme in FastAPI
- Never include password or sensitive data in JWT
- Implement rate limiting on login endpoint (5 attempts/min)

## 6. Deployment: Vercel + Railway/Render

**Decision**: Vercel (frontend), Railway or Render (backend)

**Rationale**:
- Vercel: Optimized for Next.js, automatic HTTPS, CDN, zero config
- Railway/Render: Easy Docker deployment, environment variables, auto-deploy from GitHub
- Both offer generous free tiers
- Separate deployment allows independent scaling

**Alternatives Considered**: Netlify (less Next.js optimization), Heroku (no longer free)

**Best Practices**:
- Use environment variables for all secrets (DATABASE_URL, SECRET_KEY)
- Configure CORS to allow only frontend origin
- Set up automatic deployment from GitHub
- Use health check endpoints (/health)
- Monitor deployment logs for errors
- Use Docker for backend containerization (reproducible builds)

## 7. Security Patterns

### JWT Security
- HS256 algorithm with 256-bit secret key
- 30-minute token expiration with optional refresh tokens valid for 7 days
- Secure token storage (httpOnly cookies preferred, localStorage as fallback)
- Token refresh mechanism with security best practices (secure storage, rotation)

### Database Security
- SQL injection prevention via SQLModel parameterized queries
- User isolation: Each user accesses only their own tasks
- Foreign key constraints enforced at database level
- Input validation at application boundaries

### API Security
- Rate limiting on login endpoint (5 attempts/min per IP)
- CORS configured to allow only frontend origin
- HTTPS enforcement in production
- Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Consistent error response format with message and error code

## 8. Testing Strategy

### Backend Testing (pytest)
- Target: 80%+ code coverage
- Unit tests for models, utilities, and pure functions
- API tests for authentication and CRUD operations
- Integration tests for full user flows
- User isolation tests to verify security

### Frontend Testing (Jest + React Testing Library)
- Target: 70%+ code coverage
- Component tests for UI elements
- Integration tests for user workflows
- Compatibility with React 19 and @testing-library/react@^15.0.0

### E2E Testing (Playwright)
- Critical user flows: registration, login, CRUD operations
- Cross-platform testing: Windows, macOS, Linux
- Responsive testing across device sizes
- Browser compatibility: Chrome, Firefox, Safari

## 9. Performance Considerations

### API Performance
- Target: <200ms p95 response time for list queries
- Target: <100ms p95 response time for single-item queries
- Database indexing on frequently queried fields
- Connection pooling for database operations
- Pagination for large result sets (20 items per page)

### Frontend Performance
- Lighthouse performance: 90+
- Lighthouse accessibility: 95+
- Bundle optimization and code splitting
- Responsive design for all device sizes (mobile, tablet, desktop)
- Real-time search with debouncing to prevent excessive API calls

## 10. Data Model Validation

### User Entity
- Email validation using Pydantic EmailStr
- Password validation: min 8 characters
- Unique email constraint enforced at database level
- Active status flag with default true

### Todo Entity
- Title validation: 1-500 characters
- Description validation: max 5000 characters
- Priority validation: enum of low/medium/high
- Tags validation: JSON array with max 10 tags
- User ownership validation: foreign key to user

## 11. Middleware Migration: From 'middleware' to 'proxy'

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

## Conclusion

All technology decisions align with the Hackathon II requirements and project constitution. The selected stack provides a solid foundation for a production-ready full-stack application with proper security, performance, and maintainability considerations.