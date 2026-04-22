# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the single concern of this refactor: rename, extract, inline, dedupe, simplify, restructure modules?

**How to pick:** Pick exactly one. Multi-concern refactors hide regressions. If multiple are needed, run the skill multiple times in series.

### Question 2
**Q:** Is the touched code covered by tests today?

**How to pick:** Yes → proceed. No → write characterization tests first (capture current behavior even if quirky), then refactor.

### Question 3
**Q:** What is the acceptable blast radius (file, module, package, repo-wide)?

**How to pick:** Smaller is safer. Repo-wide rename = one commit per package + automation; never a single mega-commit.

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
