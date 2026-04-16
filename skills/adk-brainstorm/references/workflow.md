# ADK Brainstorm Workflow

## Phase 1: Confirm
Clarify the task, downstream skill context, confidence target, change tolerance, and preferred artifact.

**Gate:** user approval required unless `--auto` is set.

## Phase 2: Detect
Prefer the `brainstorming` MCP server when it is available.

**Actions:**
- detect the MCP server
- if available, start a structured session
- if missing, show one install warning and continue manually

## Phase 3: Capture
State the current state, target state, and what information is still missing.

**Actions:**
- capture the current state
- capture the target state
- capture acceptable blast radius
- capture desired confidence
- capture preferred artifact

## Phase 4: Research
Gather only the evidence needed to close direction-changing uncertainty.

**Actions:**
- inspect repo evidence first
- dispatch `adk-research-agent` when external facts matter
- update the MCP session or manual state with findings

## Phase 5: Options
Present viable paths with trade-offs.

**Actions:**
- produce 2-3 options when real trade-offs exist
- compare risk, effort, maintainability, and fit
- ask the user to choose, combine, or refine

**Gate:** user chooses a direction unless `--auto` is set.

## Phase 6: Questions
Ask follow-up questions until the remaining uncertainty is no longer direction-changing.

**Actions:**
- keep open questions separate from options
- update the confidence score after each resolved question
- stop looping when further questions do not change the direction

## Phase 7: Finalize
Finalize the direction once confidence meets the requested threshold.

**Actions:**
- compare current confidence with desired confidence
- if below threshold, keep iterating or ask the user to accept the remaining gap
- record the chosen route and artifact

## Phase 8: Route
Hand off to the next skill or artifact.

**Possible routes:**
- `adk-spec`
- `adk-plan`
- `adk-write-docs`
- `adk-build`
- `adk-design`
- `adk-refactor`
- `adk-migrate`

## Validation Rules
- current state and target state are explicit
- change tolerance is explicit
- desired and current confidence are explicit
- open questions are separated from the finalized direction
- the recommended route is clear
