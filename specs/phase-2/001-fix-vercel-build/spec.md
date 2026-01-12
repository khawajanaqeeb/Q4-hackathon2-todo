# Feature Specification: Fix Vercel Deployment Build Error

**Feature Branch**: `001-fix-vercel-build`
**Created**: 2026-01-08
**Status**: Draft
**Input**: User description: "Module not found: Can't resolve '../../../../lib/api-utils' - works on localhost but fails on Vercel deployment"

## Executive Summary

The application builds successfully on localhost but fails during Vercel deployment with a module resolution error for `lib/api-utils.ts`. This is a critical production blocker preventing deployment of the full-stack todo application.

**Root Cause Identified**: The `.gitignore` file contains `lib-cov/` on line 27, which Git interprets as matching any `lib/` directory pattern. This causes `lib/api-utils.ts` to be excluded from version control even though it's required by the application. The file exists locally (enabling local builds to succeed) but is missing from the Git repository (causing Vercel deployments to fail).

**Business Impact**:
- **Current State**: Application cannot be deployed to production
- **User Impact**: New features and bug fixes cannot reach end users
- **Development Impact**: CI/CD pipeline is broken
- **Risk**: Critical infrastructure issue blocking all releases

## User Scenarios & Testing

### User Story 1 - Successful Vercel Deployment (Priority: P1)

**As a** developer deploying the application to Vercel
**I want** the build to succeed and resolve all module dependencies
**So that** the application is available to end users in production

**Why this priority**: This is the highest priority because it unblocks all production deployments. Without this fix, no features can be released.

**Independent Test**: Can be fully tested by pushing code to GitHub and verifying Vercel build succeeds with all modules resolved, delivers deployable production application.

**Acceptance Scenarios**:

1. **Given** code is pushed to the main branch, **When** Vercel attempts to build the application, **Then** the build completes successfully without module resolution errors
2. **Given** the `lib/api-utils.ts` file is committed to Git, **When** Vercel clones the repository, **Then** all required files are present in the build environment
3. **Given** the build succeeds on Vercel, **When** users access the deployed application, **Then** all API proxy functionality works correctly

---

### User Story 2 - Consistent Build Behavior (Priority: P2)

**As a** developer working on the application
**I want** builds to behave identically on localhost and Vercel
**So that** I can trust local testing to predict production behavior

**Why this priority**: Prevents future deployment surprises and ensures developer confidence in local builds.

**Independent Test**: Can be tested by comparing build outputs and module resolution between localhost and Vercel environments, delivers consistent build behavior across environments.

**Acceptance Scenarios**:

1. **Given** the same codebase is built locally and on Vercel, **When** both builds complete, **Then** both resolve the same modules successfully
2. **Given** a developer runs `npm run build` locally, **When** the build succeeds, **Then** they can be confident the Vercel build will also succeed
3. **Given** new dependencies are added to `lib/`, **When** files are committed, **Then** Git tracks them correctly (not ignored)

---

### User Story 3 - Clean Git Tracking (Priority: P3)

**As a** developer reviewing Git history
**I want** all source code files to be tracked correctly
**So that** the repository accurately reflects the codebase

**Why this priority**: Ensures repository integrity and prevents similar issues in the future.

**Independent Test**: Can be tested by running `git status` and verifying no untracked required files exist, delivers complete repository with all source files tracked.

**Acceptance Scenarios**:

1. **Given** the `.gitignore` file is updated, **When** `git status` is run, **Then** all required source files in `lib/` are tracked
2. **Given** the fix is applied, **When** reviewing the Git repository, **Then** `lib/api-utils.ts` and `lib/api.ts` are both committed
3. **Given** the repository is cloned fresh, **When** `npm run build` is executed, **Then** all required files are present

---

### Edge Cases

- **What happens when** new files are added to the `lib/` directory after the fix?
  - Files should be automatically tracked by Git (not ignored)
  - Builds should succeed both locally and on Vercel

- **What happens when** the `.gitignore` pattern is reverted accidentally?
  - CI/CD should detect the missing files
  - Build should fail with clear error message indicating missing modules

- **What happens when** other directories have similar naming conflicts?
  - Audit `.gitignore` for overly broad patterns
  - Ensure patterns are specific (e.g., `lib-cov/` should be `/lib-cov/` to match only root directory)

## Requirements

### Functional Requirements

- **FR-001**: The `.gitignore` file MUST NOT exclude the `lib/` directory or any TypeScript source files within it

- **FR-002**: The file `phase2-fullstack/frontend/lib/api-utils.ts` MUST be tracked by Git and present in all repository clones

- **FR-003**: The file `phase2-fullstack/frontend/lib/api.ts` MUST be tracked by Git and present in all repository clones

- **FR-004**: Builds MUST resolve the import `'../../../../lib/api-utils'` from `app/api/auth/[...path]/route.ts` successfully on Vercel

- **FR-005**: The `.gitignore` pattern `lib-cov/` MUST be updated to `/lib-cov/` to match only the root-level coverage directory, not any `lib/` source directories

- **FR-006**: All existing functionality in `lib/api-utils.ts` (safeJsonParse, createErrorResponse) MUST remain unchanged after the fix

- **FR-007**: Vercel deployment builds MUST complete without "Module not found" errors for any `lib/` imports

- **FR-008**: Local builds MUST continue to work after the fix (no regression)

### Key Entities

- **lib/api-utils.ts**: Utility file containing `safeJsonParse` and `createErrorResponse` functions used by the authentication proxy
- **lib/api.ts**: API client library containing `todoAPI` and `authAPI` functions
- **.gitignore**: Git configuration file controlling which files are excluded from version control
- **app/api/auth/[...path]/route.ts**: Unified authentication proxy that imports from `lib/api-utils.ts`

## Success Criteria

### Measurable Outcomes

- **SC-001**: Vercel deployment build completes in under 3 minutes without errors

- **SC-002**: 100% of required TypeScript files in `lib/` directory are tracked by Git

- **SC-003**: Zero "Module not found" errors appear in Vercel build logs

- **SC-004**: Application deploys successfully to production URL and all API endpoints function correctly

- **SC-005**: Developers can push code to GitHub and receive successful Vercel deployment within 5 minutes

- **SC-006**: Git repository size accurately reflects all source code (no missing critical files)

## Scope

### In Scope

- Updating `.gitignore` to fix the `lib-cov/` pattern
- Adding `lib/api-utils.ts` to Git tracking
- Verifying `lib/api.ts` is properly tracked
- Testing Vercel deployment build succeeds
- Documenting the root cause and fix

### Out of Scope

- Refactoring the `lib/` directory structure
- Moving files to different locations
- Changing import paths in application code
- Modifying the functionality of `api-utils.ts` or `api.ts`
- Updating other `.gitignore` patterns not related to this issue
- Implementing additional build validation checks

## Assumptions

- The Vercel build environment uses the same Node.js and npm versions as local development
- The `.gitignore` pattern `lib-cov/` is intended for code coverage output directory, not source code
- The `lib/` directory contains source code that should be version controlled
- No other files in the repository are being incorrectly ignored by similar patterns
- The Vercel deployment is configured to build from the `phase2-fullstack/frontend` directory
- All developers have the `lib/` files present locally (they were created/modified locally)

## Dependencies

### External Dependencies

- **Vercel Platform**: Deployment platform where builds are failing
- **Git Version Control**: Must correctly interpret updated `.gitignore` patterns
- **GitHub**: Remote repository hosting the code

### Internal Dependencies

- **Frontend Build Process**: Uses Next.js build system which must resolve all imports
- **Authentication Proxy**: Route handler that imports `api-utils.ts`

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Pattern change breaks other ignores | Medium | Low | Test with `git status` before committing; review all `.gitignore` patterns |
| Files too large for Git | Low | Very Low | `lib/` contains TypeScript source files (<10KB each), well within Git limits |
| Vercel cache issues | Medium | Low | Clear Vercel build cache if issues persist after fix |
| Other similar patterns exist | Medium | Medium | Audit entire `.gitignore` for overly broad patterns (e.g., `lib/`, `src/`, `app/`) |

## Non-Functional Requirements

### Performance

- Build time on Vercel should not increase by more than 10 seconds after adding tracked files
- Repository clone time should not increase noticeably (files are small)

### Maintainability

- `.gitignore` patterns should be specific and well-commented
- Documentation should explain why `/lib-cov/` uses leading slash

### Reliability

- Builds must succeed consistently on every deployment (100% success rate)
- No intermittent module resolution failures

## Acceptance Criteria Summary

**The fix is complete when:**

- [ ] `.gitignore` updated with `/lib-cov/` pattern (leading slash added)
- [ ] `phase2-fullstack/frontend/lib/api-utils.ts` is committed to Git
- [ ] `phase2-fullstack/frontend/lib/api.ts` is committed to Git
- [ ] `git ls-files phase2-fullstack/frontend/lib/` shows both files tracked
- [ ] Local build succeeds: `npm run build` completes without errors
- [ ] Vercel build succeeds: deployment completes without module resolution errors
- [ ] Deployed application functions correctly (can create/read/update/delete todos)
- [ ] No other files are accidentally unignored by the pattern change
- [ ] Documentation added to `.gitignore` explaining the pattern fix

---

**Next Steps**: Run `/sp.plan` to create implementation plan or `/sp.clarify` if requirements need refinement.
