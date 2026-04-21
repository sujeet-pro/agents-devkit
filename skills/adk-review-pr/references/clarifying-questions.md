# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the PR URL and provider (GitHub or Bitbucket)?

**How to pick:** Detect from URL host. github.com / GHE → github. bitbucket.org → bitbucket.

### Question 2
**Q:** Focus: correctness, security, performance, style, all?

**How to pick:** All = default for first review. Narrow to one when re-reviewing after changes or when scope is huge.

### Question 3
**Q:** Post mode: dry-run (report only) or post (inline + summary)?

**How to pick:** Default dry-run on first run so the user can review the findings. Post after explicit approval (or pass --auto).

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
