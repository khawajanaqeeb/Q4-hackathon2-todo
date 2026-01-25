---
title: "Backend Technology Stack"
status: "Proposed"
date: "2026-01-25"
references:
  - "specs/phase-3/plan.md"
---

## Context

The AI Chatbot Todo application requires a robust backend to handle natural language processing, conversation management, and persistent storage of user data. The system needs to support real-time interactions, maintain conversation context, and integrate with external AI services through MCP.

## Decision

We will use the following backend technology stack:

- **Web Framework**: FastAPI for its async support, automatic OpenAPI documentation, and type hints
- **ORM**: SQLModel for combining SQLAlchemy's power with Pydantic's validation
- **Database**: PostgreSQL for its reliability, JSONB support, and advanced querying capabilities
- **Authentication**: JWT tokens with proper expiration and refresh mechanisms
- **Rate Limiting**: SlowAPI for preventing abuse and ensuring fair usage

## Alternatives Considered

- **Django + Django REST Framework**: More mature but heavier, with less async support
- **Flask + SQLAlchemy**: Lightweight but lacks built-in async support and automatic documentation
- **Node.js + Express**: Familiar to many developers but JavaScript's async model differs from Python
- **MongoDB**: Better for flexible schemas but lacks ACID transactions needed for data consistency
- **Redis**: Excellent for caching but not suitable for persistent conversation storage

## Consequences

### Positive
- FastAPI provides excellent performance with async support
- SQLModel combines the best of SQLAlchemy and Pydantic
- PostgreSQL offers strong consistency and advanced features
- Built-in documentation and validation reduce development time
- Type safety reduces runtime errors

### Negative
- Learning curve for team members unfamiliar with FastAPI
- PostgreSQL may be overkill for smaller deployments
- Additional complexity compared to simpler stacks

## References

- specs/phase-3/plan.md - Technical Context and Implementation Phases
- Implementation of conversation and message models in the data layer