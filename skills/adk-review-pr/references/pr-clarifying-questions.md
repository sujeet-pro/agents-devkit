# Clarifying Questions for `adk-review-pr` (default-ask mode)

When running without `--auto`, the skill asks these questions in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question without asking, and lists every choice it auto-picked in the final report.

### Question 1

**Q:** What is the PR URL and provider (GitHub or Bitbucket)?

**How to pick:** Detect from URL host. `github.com` / GHE → GitHub. `bitbucket.org` → Bitbucket. If the URL host is not one of those, STOP and clarify — do not guess.

### Question 2

**Q:** Focus: correctness, security, performance, style, all?

**How to pick:**

- `all` `(default)` — first review of a PR; broad coverage.
- `correctness` — re-reviewing after a logic fix.
- `security` — narrow focus when scope is huge or this is an explicitly security-tagged PR.
- `performance` — narrow focus when the PR claims a perf improvement and you want to validate it.
- `style` — pre-merge final pass after correctness is settled.

### Question 3

**Q:** Post mode: dry-run (report only) or post (inline + summary + tasks)?

**How to pick:**

- `dry-run` `(default)` — first run, so the user can inspect findings before they hit the PR.
- `post` — after explicit approval, OR when `--auto` is set, OR after iterating on the dry-run findings.

### Question 4

**Q:** Reconciliation aggressiveness on existing comments?

**How to pick:**

- `validate-then-keep` `(default)` — re-validate every existing thread; reply on the ones that drifted; do not unilaterally close anything.
- `aggressive-cleanup` — also dismiss threads that are clearly no-longer-applicable. Use when the PR has been re-pushed many times and old threads are noise.
- `read-only` — do NOT reply on existing threads at all; just produce new findings. Use when re-reviewing without authority over the previous reviewer's comments.

### Question 5 (Bitbucket only)

**Q:** Task strategy for new Blockers / Critical findings?

**How to pick:**

- `task-per-blocker-and-critical` `(default)` — create a Bitbucket task for every Blocker and every Critical finding linked to its inline comment. Standard hygiene.
- `task-per-blocker-only` — tasks only for Blockers; Criticals stay as inline comments only. Use when the team uses tasks lightly.
- `no-tasks` — skip task creation entirely. Use when the team does not use tasks.

## Standard option-presentation shape

Where the answer is multiple-choice, present each option as:

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
