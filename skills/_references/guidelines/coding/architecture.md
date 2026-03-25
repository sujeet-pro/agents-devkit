# Architecture Review Guidelines

Load these guidelines for PR reviews, codebase reviews, and project documentation when the change affects boundaries, shared libraries, or long-lived systems.

## 1. Boundary Clarity

- Modules should have clear ownership and a small public surface area.
- Avoid cross-layer reach-through, such as UI code reading persistence internals directly.
- Shared helpers should represent stable concepts, not convenience wrappers around one caller.

## 2. Dependency Direction

- Dependencies should point inward toward stable abstractions.
- Flag circular dependencies, bidirectional module knowledge, and cross-package imports that bypass published interfaces.
- New dependencies must be justified by capability, maintenance cost, and bundle/runtime impact.

## 3. Data and Contract Design

- Public interfaces, API payloads, and events must be versionable and documented.
- Validate assumptions at trust boundaries.
- Schema changes should include backward-compatibility and migration thinking.

## 4. Operational Design

- Architecture reviews should check observability, rollback safety, and failure isolation.
- Long-running or asynchronous workflows need retry, idempotency, and timeout behavior.
- Configuration and feature flags should fail safely and be easy to audit.

## 5. Change Isolation

- Prefer changes that localize risk to one layer or capability.
- Flag refactors that mix architecture movement with behavior changes unless the coupling is unavoidable.
- Large structural changes should update ADRs, diagrams, or project docs in the same review cycle when those artifacts exist.

## 6. Reviewer Questions

- Does the change make future features easier or harder to implement?
- Does it introduce a new coupling point or special case?
- Are ownership, rollout, and documentation responsibilities clear?
