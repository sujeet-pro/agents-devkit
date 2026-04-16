# ADK Spec Workflow

## Phase 1: Discover

**Goal**: understand the problem space and establish scope before writing requirements.

**Steps**:
1. Clarify the topic: what system, feature, or capability is being specified?
2. Determine or confirm the spec type (`--type` or inferred from topic).
3. Identify the intended audience (product, engineering, QA, API consumers).
4. Capture the current state, target state, desired confidence, and whether a spec is truly the right artifact.
5. Gather existing specs, related docs, and prior decisions in the target area.
6. Read existing code in `--scope` to understand current state and interfaces.

**Gate**: confirm topic, spec type, audience, scope, and artifact choice with the user. Skip if `--auto`.

**Type inference** (when `--type` is not provided):
- mentions users, personas, business goals, success metrics -> `prd`
- mentions architecture, data models, system design -> `technical`
- mentions endpoints, HTTP methods, schemas, API consumers -> `api`
- mentions user flow, feature behavior, edge cases -> `feature`
- mentions test conditions, given/when/then, pass/fail criteria -> `acceptance`
- if still unclear, ask the user before proceeding

**Edge cases**:
- Existing spec on the same topic: propose `update` vs. `replace` and confirm with the user.
- Topic spans multiple spec types: recommend splitting into separate specs or confirm a combined approach.
- Topic is still direction-setting rather than requirement-writing: run the shared brainstorming workflow before proceeding.

## Phase 2: Research

**Goal**: gather the evidence and constraints needed for accurate requirements.

**Steps**:
1. Read source code for existing interfaces, data models, and patterns.
2. Check git history for prior decisions and rejected approaches.
3. Dispatch `adk-research` for:
   - domain standards and industry best practices
   - competitor approaches and prior art
   - technical constraints from external dependencies
   - regulatory or compliance requirements
4. Compile a constraints inventory: what is confirmed, what is inferred, what is unknown.

**Validation rules**:
- Every constraint in the inventory must have a source label.
- Unknowns that research cannot resolve become open questions in Phase 6.

## Phase 3: Define

**Goal**: write the requirements and acceptance criteria.

Follow the type-specific guidance below. Each type maps to a skeleton in `spec-templates.md`; use those sections as a checklist while defining requirements.

**Steps by spec type**:

### PRD
1. Identify target user personas and their goals.
2. Define the problem statement and success metrics.
3. Write user stories with priority (must-have, should-have, nice-to-have).
4. Capture constraints: timeline signals, technical limitations, compliance needs.
5. List assumptions and dependencies.
6. Define scope boundaries (non-goals).

### Technical Specification
1. Describe the current architecture context.
2. Define interface contracts: inputs, outputs, error states.
3. Specify data models with field types, constraints, and relationships.
4. Document error handling strategy.
5. Capture security considerations.
6. Define performance requirements with measurable targets.
7. List migration or backward-compatibility requirements.
8. Note observability needs.

### API Specification
1. Define the API audience and authentication model.
2. List endpoints with HTTP methods, paths, and descriptions.
3. Specify request schemas: headers, query params, body, required vs. optional.
4. Specify response schemas: success shape, pagination, error shape.
5. Define error codes with descriptions and resolution hints.
6. Document rate limiting and quota behavior.
7. Specify versioning strategy and deprecation policy.
8. Note webhook or async callback contracts.

### Feature Specification
1. Describe the feature goal and user problem.
2. Walk through the happy-path user flow.
3. Enumerate edge cases and handling for each.
4. Identify dependencies: features, services, data sources.
5. Define rollback plan and feature-flag strategy.
6. Note accessibility and internationalization requirements.

### Acceptance Criteria
1. Restate the feature or requirement being tested.
2. Write given/when/then scenarios for the happy path.
3. Write given/when/then scenarios for boundary conditions.
4. Write given/when/then scenarios for error and negative paths.
5. Define performance thresholds.
6. Note environment or data prerequisites.
7. Specify pass vs. fail criteria for each scenario.

**Edge cases**:
- Requirements that depend on stakeholder decisions not yet made: capture as open questions with the decision needed and impact of each option.
- Requirements inherited from a parent spec or system: reference the source rather than duplicating.

## Phase 4: Structure

**Goal**: organize requirements into the spec template for readability and traceability.

**Steps**:
1. Apply the appropriate template structure from `spec-templates.md`.
2. Organize sections: Scope, Non-Goals, Requirements, Constraints, Risks, Open Questions.
3. Number all requirements for traceability.
4. Tag priority (must-have, should-have, nice-to-have) on each requirement.
5. Ensure non-functional requirements have their own subsection.
6. Place open questions in a dedicated section at the end.

**Edge cases**:
- Template does not fit the spec: adapt the template and note the deviation.
- Very large specs: consider splitting into a master spec with linked sub-specs.

## Phase 5: Review

**Goal**: self-review the spec against a completeness checklist before presenting to the user.

**Checklist**:
- [ ] Every requirement is testable or explicitly marked aspirational.
- [ ] No ambiguous language ("fast", "easy", "intuitive" -- quantified or flagged).
- [ ] Non-functional requirements are present where applicable.
- [ ] Dependencies and assumptions are called out.
- [ ] The spec is internally consistent (no contradictions).
- [ ] Open questions are separated from the spec body.
- [ ] Success metrics are present (PRD).
- [ ] Error handling is specified (technical, API).
- [ ] Edge cases are enumerated (feature, acceptance).

**Gate**: present the spec for user review. Skip if `--auto`.

**Edge cases**:
- Spec fails multiple checklist items: fix what can be fixed, present the rest as known gaps.
- User disagrees with a requirement: capture the disagreement, adjust, and note the revision source.

## Phase 6: Deliver

**Goal**: present the completed spec with full transparency about coverage and gaps.

**Steps**:
1. Write the spec document to the target path (or present inline).
2. Present the delivery summary:
   - spec type and audience
   - coverage assessment (fully specified sections vs. gaps)
   - open questions for stakeholders
   - suggested next step (usually `adk-plan`)
3. Ask whether deeper detail is needed on any section.

**Edge cases**:
- Spec is incomplete due to unresolvable unknowns: deliver what exists, list unknowns as blockers for the next phase.
- User wants implementation details in the spec: push back gently -- recommend `adk-plan` for the HOW.

## Validation Rules (Summary)

- Every requirement is testable or explicitly marked as aspirational.
- No ambiguous language without a quantification or flag.
- Non-functional requirements are present where applicable.
- Dependencies and assumptions are called out.
- The spec is internally consistent.
- Open questions are separated from the spec body.
- Inferred requirements are labeled `[inferred]`.
- External constraints are cited with their source.
