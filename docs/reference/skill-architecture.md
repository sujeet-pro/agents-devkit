---
title: "architecture"
description: "Software architecture patterns, principles, and review criteria"
skill_name: architecture
category: guideline
workflow_tier: helper
user_invocable: false
---

# architecture

Helper skill that scans the repository to determine the architecture type and loads relevant architecture guidelines. Provides core architecture principles, focus-specific patterns (frontend, backend, fullstack, infra), and anti-pattern detection criteria for review, audit, design, and development skills.

## Purpose

- Auto-detect the project's architecture type from project structure, dependencies, and config files
- Load focus-appropriate architecture patterns and principles
- Provide anti-pattern detection criteria with severity ratings and fix guidance
- Supply architecture review criteria for code review, audit, and design skills

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--focus` | `frontend` \| `backend` \| `fullstack` \| `infra` | auto-detect | Force a specific architecture focus area instead of auto-detection |

## Key Behaviors

### Architecture Detection

Scans the repository to determine the primary architecture type:

| Signal | Focus |
|--------|-------|
| `package.json` with React/Vue/Svelte/Angular | frontend |
| `next.config.*`, `nuxt.config.*`, `astro.config.*` | frontend (SSR/SSG) |
| `.storybook/`, design tokens, `tailwind.config.*` | frontend (design system) |
| `pom.xml`, `build.gradle`, `go.mod`, `Cargo.toml` | backend |
| `pyproject.toml` with FastAPI/Django/Flask | backend |
| API route handlers, GraphQL schemas, OpenAPI specs | backend (API) |
| Both frontend and backend signals present | fullstack |
| `Dockerfile`, `docker-compose.*`, `k8s/`, `helm/` | infra |
| `terraform/`, `pulumi/`, `.github/workflows/` | infra |

**Precedence**: both frontend + backend → `fullstack`; dominant infra signals with no app code → `infra`; otherwise strongest single signal.

### Core Architecture Principles (Always Loaded)

| Principle | Summary |
|-----------|---------|
| Separation of Concerns | Each module/layer has a single, well-defined responsibility |
| Single Responsibility | A class, module, or function has one reason to change |
| Dependency Inversion | High-level modules depend on abstractions, not low-level modules |
| Interface Segregation | Narrow, role-specific interfaces over broad ones |
| CQRS | Separate read/write models when loads differ significantly (not for simple CRUD) |
| Event-Driven vs Request-Response | Choose based on consistency and latency requirements per operation |

### Architecture Style Guidance

| Style | When to Use | When to Avoid |
|-------|-------------|---------------|
| Layered | Small to medium apps with clear request/response flows | Layers become pass-through with no logic |
| Hexagonal | Domain must be framework-agnostic or testable in isolation | Simple CRUD where indirection adds overhead |
| Clean Architecture | Complex domains with multiple delivery mechanisms | MVPs or single delivery mechanism apps |
| Modular monolith | Service boundaries without distributed system complexity | Services genuinely need independent deployment |
| Microservices | Independent deployment, scaling, and team ownership | Early-stage products, small teams, unclear boundaries |

### Focus-Specific Patterns

**Frontend** (loaded when focus is `frontend` or `fullstack`): component hierarchy and composition, state management patterns (local → lifted → context → external store → server state), data fetching strategies, route-based code splitting, design system integration.

**Backend** (loaded when focus is `backend` or `fullstack`): API design (REST, GraphQL, gRPC), service boundaries and DDD, database access patterns (Repository, Active Record, Query Builder, Raw SQL), error handling and resilience, observability (logging, metrics, tracing).

**Infrastructure** (loaded when focus is `infra` or infra files detected): container orchestration, CI/CD pipelines, infrastructure as code, environment management.

### Anti-Patterns to Detect

| Anti-Pattern | Severity | Detection Signals |
|-------------|----------|-------------------|
| God Classes / God Modules | High | Files over 500 lines, classes with 10+ unrelated methods, modules imported by >50% of codebase |
| Circular Dependencies | High | Import cycles, modules that import each other directly or transitively |
| Leaky Abstractions | Medium | Consumers working around limitations, catch-and-rethrow adding no context, pass-through wrappers |
| Over-Engineering | Medium | Abstract base class with one implementation, config for nonexistent features, unnecessary indirection layers |
| Under-Engineering | High | Missing error handling, no input validation on public APIs, no logging for failures, missing auth checks |

## What It Provides

A summary listing the detected focus and loaded guidelines for the calling skill:

```
Focus: backend (detected via go.mod, cmd/, internal/)

Loaded:
- Core architecture principles
- Backend architecture patterns
- Anti-pattern detection criteria

Detected patterns:
- Layered architecture (cmd/ → internal/service/ → internal/repository/)
- REST API (internal/handler/)
- Repository pattern (internal/repository/)
```

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | always (architecture review is one of 10 review dimensions) |
| `code-review-repo` | always |
| `audit` | always |
| `design` | always |
| `dev-build` | when architectural decisions are needed |
| `dev-refactor` | always (refactoring requires architecture awareness) |
