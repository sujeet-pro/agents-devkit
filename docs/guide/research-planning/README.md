---
title: Research & Planning
description: Research topics, create implementation plans, and write specifications
order: 5
---

# Research & Planning

ADK helps you research engineering topics with cited sources, create structured implementation plans, and write formal specifications. These skills work well together — research feeds into specs, specs feed into plans, plans feed into implementation.

## Scenarios

- [Research a topic](#research-a-topic)
- [Deep research with multiple agents](#deep-research-with-multiple-agents)
- [Create an implementation plan](#create-an-implementation-plan)
- [Execute a plan](#execute-a-plan)
- [Track plan progress](#track-plan-progress)
- [Write specifications](#write-specifications)
- [Analyze existing specifications](#analyze-existing-specifications)
- [Generate checklists from specs](#generate-checklists-from-specs)
- [Chaining research into plans](#chaining-research-into-plans)

---

## Research a Topic

Use `research` to investigate an engineering topic. ADK launches parallel research agents that search official docs, specs, implementations, and community patterns.

```text
/adk:research "Next.js App Router migration patterns"
/adk:research "gRPC vs REST for microservices"
/adk:research "SQLite WAL mode"
```

Standard search launches 2 parallel agents:

1. **Primary-source researcher** — official docs, specs, RFCs, maintainer guidance
2. **Implementation researcher** — real repositories, migration notes, community patterns

### Save to file

```text
/adk:research "React Server Components" --save ./docs/research/rsc-research.md
```

### Verbosity control

```text
/adk:research "Kubernetes autoscaling" --verbosity short    # Key findings + sources only
/adk:research "Kubernetes autoscaling" --verbosity detailed  # Full analysis with confidence ratings
```

---

## Deep Research with Multiple Agents

Use `--deep` for thorough investigation with 4 parallel agents:

```text
/adk:research "WebAssembly for server-side computation" --deep
```

Deep mode adds:

3. **Risk analyst** — edge cases, tradeoffs, version compatibility, breaking changes
4. **Synthesis agent** — merges all findings, resolves contradictions, assigns confidence ratings

### Deep + detailed

For the most comprehensive output:

```text
/adk:research "migrating from Kafka to Redpanda" --deep --verbosity detailed
```

---

## Create an Implementation Plan

Use `plan` to create a structured, actionable implementation plan.

### Brainstorm first

Start with brainstorming to explore approaches:

```text
/adk:plan --mode brainstorm user authentication system
```

### Write a plan

```text
/adk:plan --mode write implement caching layer for the API
```

### From a spec

Reference a specification to generate a plan:

```text
/adk:plan --mode write --spec ./docs/specs/caching-tdd.md implement the caching layer
```

### Plan format

```text
/adk:plan --mode write --format markdown API versioning strategy
/adk:plan --mode write --format checklist database migration steps
```

---

## Execute a Plan

Once a plan is approved, execute it:

```text
/adk:plan --mode execute --plan ./.temp/caching-plan/plan.md
```

Execution runs through each task in the plan with approval gates. ADK won't execute unless the plan has been reviewed and approved.

### Auto-execute

```text
/adk:plan --mode execute --plan ./.temp/caching-plan/plan.md --auto
```

---

## Track Plan Progress

Monitor an in-progress plan:

```text
/adk:plan --mode track --plan ./.temp/caching-plan/plan.md
```

Shows completed tasks, in-progress items, blockers, and remaining work.

---

## Write Specifications

Use `spec` to create formal specifications:

```text
/adk:spec --mode write authentication service specification
/adk:spec --mode write API rate limiting specification
```

### Specification depth

```text
/adk:spec --mode write --depth quick payment processing spec
/adk:spec --mode write --depth thorough user data model specification
```

### Constitutions (style/quality specs)

Create a constitution — a spec that defines quality criteria:

```text
/adk:spec --mode constitution --action create code quality standards for the frontend team
```

Update or audit an existing constitution:

```text
/adk:spec --mode constitution --action update ./docs/constitutions/frontend-standards.md
/adk:spec --mode constitution --action audit ./docs/constitutions/frontend-standards.md
```

---

## Analyze Existing Specifications

Review a spec for completeness, consistency, and ambiguity:

```text
/adk:spec --mode analyze ./docs/specs/auth-spec.md
```

---

## Generate Checklists from Specs

Turn a specification into an actionable checklist:

```text
/adk:spec --mode checklist ./docs/specs/auth-spec.md
```

---

## Chaining Research into Plans

A common workflow: research → spec → plan → build.

```text
# 1. Research the topic
/adk:research "OAuth2 with PKCE for SPAs" --save ./docs/research/oauth-pkce.md

# 2. Write a spec informed by the research
/adk:spec --mode write OAuth2 PKCE implementation specification

# 3. Create an implementation plan from the spec
/adk:plan --mode write --spec ./docs/specs/oauth-pkce-spec.md implement OAuth2 PKCE

# 4. Execute the plan
/adk:plan --mode execute --plan ./.temp/oauth-plan/plan.md

# 5. Self-review
/adk:code-review-pr --fix
```

---

## Which Skill to Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Research a topic | `research` | `<topic>`, `--save` |
| Deep research | `research` | `--deep`, `--verbosity detailed` |
| Brainstorm approaches | `plan` | `--mode brainstorm` |
| Write an implementation plan | `plan` | `--mode write`, `--spec`, `--format` |
| Execute a plan | `plan` | `--mode execute`, `--plan` |
| Track plan progress | `plan` | `--mode track`, `--plan` |
| Write a specification | `spec` | `--mode write`, `--depth` |
| Analyze a spec | `spec` | `--mode analyze` |
| Generate checklist from spec | `spec` | `--mode checklist` |
| Create quality standards | `spec` | `--mode constitution` |

## Related Skills

- **[`dev-build`](/reference/skill-dev-build/)** — implement after planning
- **[`docs-write`](/reference/skill-docs-write/)** — publish research or specs as documents
- **[`audit`](/reference/skill-audit/)** — audit code against specifications
