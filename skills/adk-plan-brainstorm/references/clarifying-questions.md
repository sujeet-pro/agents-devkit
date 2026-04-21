# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the current state today, with one piece of evidence?

**How to pick:** Cite a file path, URL, command output, or screenshot. Without evidence the brainstorm is speculative.

### Question 2
**Q:** What change tolerance is acceptable: surgical, bounded, or transformative?

**How to pick:** Surgical = touch only what must change; reversible in <1h. Bounded = touch one subsystem; reversible in <1d. Transformative = touch many subsystems; reversibility hard. Pick the smallest that still meets the goal.

### Question 3
**Q:** What confidence threshold do you want before locking the direction (80/90/95)?

**How to pick:** Production-safe surgical = 95. Standard feature/refactor = 90. Exploratory or personal = 85.

### Question 4
**Q:** What artifact should this brainstorm produce: none, proposal, PRD, RFC, HLD, LLD, TDD, or plan?

**How to pick:** None = continue inside the calling skill. Proposal/RFC/HLD/LLD/TDD = adk-docs-write. PRD = adk-plan-spec. Plan = adk-plan-roadmap.

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
