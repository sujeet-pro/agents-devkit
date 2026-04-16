# ADK Design Workflow

## Phases

### Phase 1: Context
Gather design system, brand guidelines, existing patterns, constraints, and when relevant the broader target state and acceptable blast radius.

**Inputs:** user design task, `--action`, `--focus`, `--scope` flags
**Actions:**
- Parse the design task and identify the product goal
- Determine the action type (`create`, `audit`, `polish`)
- Identify the primary focus area (UI, UX, accessibility, frontend)
- If the task is still strategy-setting, capture current state, target state, desired confidence, and artifact preference before moving on
- Inspect existing design system, component patterns, and brand guidelines
- Review the current UI surface, screenshots, or code relevant to the task
- Inventory existing components that relate to the design task

**Gate:** User confirms scope, audience, and constraints. Skip when `--auto` is set.

**Outputs:** design context, component inventory, confirmed scope

### Phase 2: Audit
Evaluate the current state against quality criteria and anti-patterns, including AI slop detection.

**Actions:**
- Assess accessibility: WCAG compliance, keyboard navigation, screen reader support
- Evaluate responsive design: breakpoint coverage, mobile experience
- Check visual hierarchy: typography scale, color usage, spacing consistency
- Review interaction states: default, hover, focus, active, disabled, loading, empty, error
- Identify design-system inconsistencies
- **AI slop scan:** check for font monoculture (Inter, DM Sans, etc.), the AI color palette (cyan-on-dark, purple gradients, neon accents), card grid repetition, hero metric templates, flat type hierarchy, untinted black/white, uniform spacing
- Prioritize findings by severity (critical, important, minor)

**Outputs:** prioritized findings with severity levels, AI slop flags

### Phase 3: Design
Propose improvements with rationale, component hierarchy, and implementation effort.

**Actions:**
- Generate 2-3 design options or variations with trade-offs
- If the options still represent materially different product directions, run the shared brainstorming workflow before locking one
- Include component hierarchy and implementation approach per option
- Estimate effort for each option
- Highlight accessibility and responsiveness implications
- Present options for user selection

**Gate:** User selects design direction. Skip when `--auto` is set (uses recommended option).

**Outputs:** selected design direction with rationale

### Phase 4: Implement
Apply design changes, dispatching subagents for parallel component work.

**Actions:**
- Apply design changes following the selected direction
- Dispatch `adk-implementer` for parallel component work when changes span multiple files
- Ensure semantic HTML, proper ARIA attributes, keyboard accessibility
- Include all interaction states in implementation
- Follow the project's existing code conventions and design tokens

**Subagent dispatch criteria:**
- Changes span 3+ components or files
- Parallel work is possible (independent components)
- Do not dispatch for single-component polish

**Outputs:** implemented design changes

### Phase 5: Verify
Validate the implementation against design goals and quality criteria.

**Actions:**
- Visual verification (browser agent if available, code review otherwise)
- Accessibility check: contrast ratios, keyboard navigation, ARIA attributes
- Responsive validation: test at defined breakpoints
- Interaction state coverage: verify all states are handled
- Cross-browser considerations noted when relevant

**Outputs:** verification results with pass/fail per criterion

### Phase 6: Report
Present before/after comparison, design decisions, and remaining polish.

**Actions:**
- Summarize design changes with before/after descriptions
- List design decisions and their rationale
- Report accessibility and responsive compliance status
- Identify remaining polish for future iteration
- Offer deeper detail on any section

**Outputs:** structured design report

## Validation Rules
- Design recommendations tie back to the product goal and current surface
- Accessibility and responsiveness are visible in every closeout
- Unresolved implementation constraints are stated explicitly
- Interaction states are covered: default, hover, focus, active, disabled, loading, empty, error

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Context): skip user confirmation, proceed with parsed intent
- Phase 3 (Design): select recommended option automatically
- Phase 4 (Implement): proceed without intermediate check-ins
- Phase 5 (Verify): still runs full verification
- Phase 6 (Report): still reports full results
