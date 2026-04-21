# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What artifact: HLD (system overview), LLD (component-level detail), ADR (single decision), or migration plan?

**How to pick:** HLD = new service or major rewrite. LLD = inside an existing service. ADR = single irreversible decision (DB choice, framework swap). Migration = move from A to B.

### Question 2
**Q:** Which non-functional requirements are hard constraints (latency, throughput, availability, cost, regulatory)?

**How to pick:** List the top 3 with numeric thresholds. Anything below the threshold is a constraint; anything above is a target.

### Question 3
**Q:** What is the blast radius (single service, multiple services, public API, data model)?

**How to pick:** Single service = LLD enough. Multiple services = HLD + per-service LLD. Public API = include API versioning + deprecation plan. Data model = include migration script and rollback.

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
