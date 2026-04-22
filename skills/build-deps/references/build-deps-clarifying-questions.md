# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Mode: inventory, upgrade, audit, dedupe, or remove-unused?

**How to pick:** Inventory = list-only, no changes. Upgrade = bump versions. Audit = flag security/license/staleness. Dedupe = collapse multiple installs of the same package. Remove-unused = prune deps with zero call sites.

### Question 2
**Q:** Upgrade scope: patch only, minor, major (breaking)?

**How to pick:** Patch = always safe to auto-apply with tests. Minor = safe with tests + changelog scan. Major = read every changelog, expect breakage, plan migration.

### Question 3
**Q:** Are there pinned-version constraints (peer deps, runtime, monorepo)?

**How to pick:** List them up front. The plan must respect every constraint or explicitly justify breaking one.

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
