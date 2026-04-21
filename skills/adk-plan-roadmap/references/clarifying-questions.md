# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the source spec or design we are planning from?

**How to pick:** Pass a path to the spec/design markdown. If none, ask the user to run adk-plan-spec or adk-plan-design first.

### Question 2
**Q:** What is the slice size you want: thin vertical slices (one user-visible behavior at a time) or layered (model → API → UI)?

**How to pick:** Vertical = ship value continuously, simpler review, harder coordination. Layered = easier per-team handoff, slower user value, riskier integration. Default = vertical for ≤5 engineers.

### Question 3
**Q:** Are there hard deadlines or external dependencies to respect?

**How to pick:** List them. Steps that depend on external parties get marked with a blocker tag and a fallback path.

## Standard option-presentation shape

Where the answer is multiple-choice (mode, focus, depth, severity filter, etc.), present each option as:

```
### Option <A | B | C>: <short label>
- What it does: <one sentence>
- Pros: <2-3 bullets>
- Cons: <2-3 bullets>
- Best when: <one sentence with a concrete signal>
- Blast radius: surgical | bounded | transformative
- Reversibility: easy | moderate | hard
```

Mark exactly one option `(default)` and say in one sentence why it is the safest pick for the current evidence.
