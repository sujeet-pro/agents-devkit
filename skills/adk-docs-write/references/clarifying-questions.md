# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Doc type: README / runbook / API / ADR / onboarding / migration / tech-radar / changelog / custom?

**How to pick:** README = first-touch repo intro. Runbook = on-call mitigation. API = developer reference. ADR = single decision record. Onboarding = day-1 to first-PR. Migration = move from A to B. Tech-radar = ring placement. Changelog = release notes. Custom = anything else.

### Question 2
**Q:** Audience and the action they take after reading?

**How to pick:** On-call → mitigation steps. New hire → setup commands. Consumer → API signatures + examples. Decision-maker → trade-offs + recommendation.

### Question 3
**Q:** Where will it live so it stays discoverable?

**How to pick:** Pick a path inside the repo's existing docs structure. Avoid orphan files at the root.

### Question 4
**Q:** Are there extra repos that supply context (clones to read, paths to local checkouts)?

**How to pick:** Pass URLs to clone or paths to local clones. Useful for cross-repo migration guides, integration docs, multi-service onboarding.

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
