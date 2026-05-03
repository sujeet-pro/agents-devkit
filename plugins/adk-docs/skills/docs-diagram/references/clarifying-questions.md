# `docs-diagram` — clarifying questions

Asked under `-i`; defaults apply under `--auto`.

## Phase 0

1. **Diagram type: `<inferred>`. Override?**
   - _Default under `--auto`:_ inferred type.
   - _When to ask:_ `-i` mode; inferred type isn't a good fit for
     the subject (e.g. "checkout flow" could be sequence or
     flowchart — both valid).

2. **Subject: `<subject>`. Narrow the scope?**
   - _Default under `--auto`:_ subject as given.

## Phase 1

3. **`--scope` path: `<path>`. Confirm?**
   - _Default under `--auto`:_ path as given.
   - _When to ask:_ path could be narrower (e.g. `services/` when
     `services/checkout/` is the concept).

## Phase 2 (under `--scope`)

4. **`<N>` nodes found. Over the 15-node budget. Choose a split
   strategy:**
   - **A: Overview + zoom-in** (default): one 5-7 node overview,
     one zoom-in per subsystem (up to 15 nodes each). Best for
     architecture / flowcharts.
   - **B: Lifecycle phase split:** for state machines; one diagram
     per lifecycle phase.
   - **C: Actor-view split:** for sequences; one diagram per actor
     view.
   - _Default under `--auto`:_ A.

## Phase 3

5. **Preview draft — looks right?**
   - _Default under `--auto`:_ proceed to validate.
   - _When to ask:_ `-i` mode; user wants to tune labels or layout.

## Phase 4

6. **Render failed: `<error>`. Show error and offer to fix?**
   - _Default under `--auto`:_ show error; attempt one automated
     fix (common mistakes: missing node declaration, bad arrow
     syntax); if that fails, surface.

## Anti-rules

- Never ask more than one question per turn.
- Never ask "what's the subject?" — that's part of the prompt.
- Never offer all 10 diagram types when the subject strongly
  implies 1-2; offer the top 2 + "other".
- Never skip the budget gate under `--auto` — always surface the
  split decision in the report even when the skill chose
  silently.
