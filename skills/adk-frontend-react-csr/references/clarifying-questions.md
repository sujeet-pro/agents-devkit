# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Mode: new (bootstrap), feature (extend existing), audit (read-only)?

**How to pick:** Inferred from the request when omitted. New = create dir + scaffold. Feature = inside an existing app on the stack. Audit = read-only findings.

### Question 2
**Q:** Target directory + repo name + base path?

**How to pick:** Repo name → Pages URL `/<repo-name>/`. Custom domain → base = `/`. Subpath hosting → explicit base.

### Question 3
**Q:** Should the agent suppress the user-facing version-research report (--no-research)?

**How to pick:** Default = show the report. Suppress only when output noise is unwanted; the lookups still run.

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
