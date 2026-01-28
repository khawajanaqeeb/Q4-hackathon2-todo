# Phase 3 Authentication Flow

## Overview
This document defines the canonical authentication flow for the chatbot-enabled todo application. The authentication system ensures secure user access to both traditional todo features and AI-powered chatbot functionality.

## Authentication Methods
The system will use JWT (JSON Web Tokens) with HTTP-only cookies for session management. This approach provides secure token storage and automatic inclusion in API requests.

## Login Flow

### 1. User Initiation
- User accesses the login page
- User enters username/email and password
- Frontend validates input format before submission

### 2. Credential Verification
- Frontend sends credentials to `/api/auth/login` endpoint
- Backend verifies credentials against stored user data
- Backend generates JWT upon successful authentication
- Backend sets HTTP-only cookie containing the JWT

### 3. Session Establishment
- Backend returns success response with user information
- Frontend receives session cookie automatically
- Frontend updates UI to reflect logged-in state
- User redirected to main application

## Registration Flow

### 1. User Registration
- User accesses the registration page
- User enters username, email, and password
- Frontend validates input format before submission

### 2. Account Creation
- Frontend sends registration data to `/api/auth/register` endpoint
- Backend validates uniqueness of username/email
- Backend creates new user record with hashed password
- Backend generates JWT for new session
- Backend sets HTTP-only cookie containing the JWT

### 3. Welcome Sequence
- Backend returns success response with user information
- Frontend receives session cookie automatically
- Frontend updates UI to reflect logged-in state
- User directed to onboarding or main application

## Session Verification Flow

### 1. Session Check
- Frontend makes request to `/api/auth/verify` endpoint
- Session cookie automatically included in request
- Backend validates JWT signature and expiration
- Backend retrieves user information associated with token

### 2. Response Processing
- Backend returns user information if valid session
- Frontend updates UI based on user status
- If invalid/expired token, redirects to login

## Logout Flow

### 1. User Initiation
- User selects logout option
- Frontend sends request to `/api/auth/logout` endpoint

### 2. Session Termination
- Backend invalidates current session/token
- Backend clears HTTP-only session cookie
- Frontend receives confirmation of logout
- Frontend updates UI to reflect logged-out state
- User redirected to login page

## Error Handling

### Authentication Failures
- Invalid credentials return 401 Unauthorized
- Frontend displays appropriate error message
- User remains on login form to retry

### Session Expiration
- Expired tokens return 401 Unauthorized
- Frontend detects expired session and redirects to login
- User prompted to re-authenticate

### Network Issues
- Failed requests trigger appropriate error handling
- Frontend provides feedback to user
- Automatic retry mechanisms where appropriate

## Security Measures

### Token Security
- JWTs signed with strong algorithm (HS256/RS256)
- Short expiration times with refresh token mechanism
- HTTP-only cookies prevent XSS attacks
- Secure flag ensures transmission only over HTTPS

### Rate Limiting
- Login attempts limited to prevent brute force
- Session verification requests rate-limited
- IP-based and account-based limits applied

### Input Validation
- All credentials validated on both frontend and backend
- Password strength requirements enforced
- Username/email format validation applied