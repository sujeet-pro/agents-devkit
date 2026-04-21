# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Which dimensions to audit (security / performance / quality / dependencies / tests / architecture / all)?

**How to pick:** All for new audits. Narrow when re-auditing a specific area or under time pressure.

### Question 2
**Q:** Depth: quick / standard / deep?

**How to pick:** Quick = surface scan, ~30 min. Standard = run available analyzers (linter/typechecker/audit). Deep = sample-based code review of hot files + per-package metrics.

### Question 3
**Q:** Are there extra repos to clone for cross-repo context (mono-repo subprojects, shared libs)?

**How to pick:** Pass URLs or paths. Each gets its own findings section in the report.

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
