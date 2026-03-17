# Product Requirements Document (PRD) Guidelines

Guidelines for writing and reviewing Product Requirements Documents. A PRD defines what a product or feature should do from the user's perspective, with clear success criteria that engineering, design, and business stakeholders can align on.

**Audience**: Product managers, designers, engineers, and business stakeholders who need to agree on what to build, for whom, and how to measure success.

---

## 1. Required Sections

Every PRD must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Problem Statement | The user or business problem being solved. |
| 2 | User Personas | Who experiences this problem and their characteristics. |
| 3 | User Stories | Specific capabilities described from the user's perspective. |
| 4 | Acceptance Criteria | Precise conditions that define "done" for each story. |
| 5 | Success Metrics | Measurable KPIs with target values. |
| 6 | Scope | What is in-scope and explicitly out-of-scope. |
| 7 | Dependencies | External teams, systems, or decisions this work depends on. |
| 8 | Timeline & Milestones | Delivery phases with target dates and deliverables. |
| 9 | Risks & Mitigations | Known risks and planned responses. |

---

## 2. Content Standards

### Problem Statement
- Describe the problem from the user's perspective, not from the product team's perspective. "We need a dashboard" is not a problem statement; "Operators cannot identify failing deployments until customers report them" is.
- Quantify the impact: how many users are affected, how often, and what is the cost (time, revenue, satisfaction).
- Explain why now: what has changed that makes this problem urgent or important at this time.
- Cite evidence: user research, support tickets, analytics data, or competitive analysis. Do not rely on assumptions or anecdotes alone.

### User Personas
- Define each persona with:
  - **Name and role**: A descriptive label (e.g., "Platform Engineer" not "User Type A").
  - **Goals**: What they are trying to accomplish.
  - **Pain points**: What frustrates them about the current experience.
  - **Context**: How, when, and where they interact with the product.
- Personas must be based on research or data. If they are hypothetical, state that explicitly.
- Limit to 2-4 primary personas. If more are needed, the scope may be too broad.

### User Stories
- Follow the standard format: **"As a [persona], I want [capability], so that [benefit]."**
- Each story must be:
  - **Independent**: Can be implemented and delivered separately from other stories.
  - **Testable**: A QA engineer can write a test for it without further clarification.
  - **Valuable**: Delivers a clear benefit stated in the "so that" clause.
- Prioritize stories using MoSCoW (Must have, Should have, Could have, Won't have) or a similar framework. The priority must be stated, not implied.
- Avoid compound stories. "As a user, I want to create, edit, and delete reports" is three stories.

### Acceptance Criteria
- Use the Given/When/Then format for testable criteria:
  - **Given** [precondition or context]
  - **When** [action the user takes]
  - **Then** [expected outcome]
- Each user story must have at least two acceptance criteria: the happy path and one error or edge case.
- Acceptance criteria must be specific. "The page loads quickly" is not testable; "The page renders within 2 seconds on a 3G connection" is.
- Include boundary conditions: What happens at limits? What happens with empty data? What happens with invalid input?

### Success Metrics
- Define 2-5 KPIs that measure whether the feature achieves its goals. Each must have:

| Metric | Current Value | Target Value | Measurement Method | Timeframe |
|---|---|---|---|---|
| Deployment failure detection time | 45 minutes (median) | Under 5 minutes | Monitoring platform timestamps | 30 days post-launch |
| Support tickets for deployment issues | 120/month | Under 30/month | Support ticket system | 60 days post-launch |

- Metrics must be **measurable with existing or planned instrumentation**. If new instrumentation is needed, that is a dependency.
- Include both leading indicators (adoption, usage frequency) and lagging indicators (retention, satisfaction, revenue impact).
- Define the baseline (current state) so improvement can be objectively measured.

### Scope
- **In-Scope**: List specific capabilities, platforms, and user segments included.
- **Out-of-Scope**: List items that are explicitly excluded from this effort. This section is **as important as in-scope** because it prevents scope creep and sets correct expectations.
- For each out-of-scope item, briefly explain why it is excluded (deferred to a future phase, handled by another team, not justified by the data).
- If something is ambiguous, default to out-of-scope and document it. It is safer to explicitly add scope later than to discover unstated expectations during development.

### Dependencies
- List every external dependency with:
  - **What**: The specific deliverable or decision needed.
  - **Who**: The team or individual responsible.
  - **When**: The date by which it is needed.
  - **Impact if delayed**: What happens to the timeline or scope if this dependency is not met.
- Include technical dependencies (API availability, infrastructure provisioning), design dependencies (finalized mocks, design system components), and business dependencies (legal approval, partnership agreements).

### Timeline & Milestones
- Break delivery into phases. Each phase must have:
  - **Milestone name**: Descriptive label for the deliverable.
  - **Target date**: Specific date, not "Q3" or "soon."
  - **Deliverables**: What is included in this phase (reference specific user stories).
  - **Exit criteria**: What must be true to consider this milestone complete.
- The first milestone should deliver user value. Avoid milestones that are purely technical ("set up infrastructure") with no user-facing outcome.
- Include buffer for unknowns. If the timeline has zero slack, flag it as a risk.

### Risks & Mitigations
- For each risk, document:

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Third-party API rate limits may be insufficient | Medium | High (blocks core feature) | Negotiate higher limits; design with caching fallback | Platform team |
| User adoption may be low without training | High | Medium (delays metric targets) | Create onboarding guide; schedule training sessions | Product team |

- Categorize risks: technical, resourcing, dependency, market, and regulatory.
- Every risk must have a mitigation plan or an explicit acceptance ("We accept this risk because...").
- Review risks at each milestone. Remove resolved risks and add newly discovered ones.

---

## 3. Structure & Flow

- A PRD is a contract between product and engineering. Ambiguity in the PRD becomes disagreement during implementation.
- Write for the skeptical reader. Anticipate "why?" and "how do you know?" questions and answer them proactively.
- Keep the document focused on the problem and desired outcomes. Do not prescribe technical solutions unless there is a hard constraint (e.g., "must integrate with existing Kafka infrastructure").
- User stories and acceptance criteria are the most referenced sections during development. Invest the most effort here.

---

## 4. Common Issues

- **Solution disguised as a problem**: "We need a real-time dashboard" is a solution. The problem is "Operators cannot detect failures quickly enough." Always start with the pain, not the prescription.
- **Untestable acceptance criteria**: Criteria that use words like "intuitive," "easy," "fast," or "user-friendly" without measurable definitions. Every criterion must be verifiable by someone who was not involved in writing it.
- **Missing out-of-scope section**: Without explicit boundaries, stakeholders assume everything they want is included. This is the most common source of mid-project conflict.
- **Vanity metrics**: Metrics that look good but do not indicate real success. "Number of page views" does not mean users found the feature useful. Prefer outcome metrics over activity metrics.
- **Compound user stories**: A single story that bundles multiple capabilities makes it impossible to prioritize, estimate, or test independently. Split them.
- **Risks without owners**: A risk that nobody owns will not be mitigated. Every risk needs a named individual or team responsible for monitoring and responding.

---

## 5. Review Checklist

- [ ] Problem statement describes a user/business problem with quantified impact
- [ ] Evidence is cited (research, data, support tickets), not just assumptions
- [ ] User personas are based on research and limited to 2-4 primary personas
- [ ] Every user story follows "As a [persona], I want [X], so that [Y]" format
- [ ] User stories are independent, testable, and prioritized
- [ ] Each story has at least two acceptance criteria in Given/When/Then format
- [ ] Acceptance criteria cover happy paths, error cases, and boundary conditions
- [ ] Success metrics have current baselines, target values, and measurement methods
- [ ] Out-of-scope section is present and explains why each item is excluded
- [ ] Dependencies list specific deliverables, owners, dates, and delay impact
- [ ] Timeline milestones have target dates, deliverables, and exit criteria
- [ ] Every risk has likelihood, impact, mitigation plan, and an owner
- [ ] Document does not prescribe technical solutions unless constrained
- [ ] No TODO/TBD placeholders remain in the final version
