# Clarifying Questions for `adk-review-pr` (default-ask mode)

When running without `--auto`, the skill asks these questions in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question without asking, and lists every choice it auto-picked in the final report.

### Question 1

**Q:** What is the PR URL and provider (GitHub or Bitbucket)?

**How to pick:** Detect from URL host. `github.com` / GHE → GitHub. `bitbucket.org` → Bitbucket. If the URL host is not one of those, STOP and clarify — do not guess.

### Question 2

**Q:** Ownership: is this your PR or someone else's?

**How to pick:**

- `auto` `(default)` — let the skill compare the PR's `author.login` (or Bitbucket account id) against your local `gh auth status` / `git config user.email` / configured Bitbucket username. Surfaced in the status banner before anything irreversible.
- `not-mine` — force Path A (review-and-post). Pick when the auto-detection is wrong or when you want to write a fresh review on your own PR (rare).
- `mine` — force Path B (validate existing reviewer comments + draft replies, optionally `--fix` locally). Pick when auto-detection misses (fork PRs, no auth) but you know it's yours.

If auto-detection has low confidence (no remote auth, ambiguous identity, fork PR), the skill STOPs and asks before continuing.

### Question 3

**Q:** Focus: correctness, security, performance, style, all?

**How to pick:**

- `all` `(default)` — first review of a PR; broad coverage.
- `correctness` — re-reviewing after a logic fix.
- `security` — narrow focus when scope is huge or this is an explicitly security-tagged PR.
- `performance` — narrow focus when the PR claims a perf improvement and you want to validate it.
- `style` — pre-merge final pass after correctness is settled.

Path B note: focus narrows the validation pass over existing reviewer comments (e.g. `security` only re-validates security-tagged comments).

### Question 4

**Q:** Post mode: post (inline + summary + tasks) or dry-run (report only)?

**How to pick:**

- `post` `(Path A default)` — the source supports comments, so the comments ARE the deliverable. Approval gate still applies before anything is posted unless `--auto`.
- `dry-run-replies` `(Path B default)` — drafted replies sit in `.temp/` for inspection. Pick when you want to review every draft before it hits the PR.
- `dry-run` — pure findings/replies-only, no posting target. Equivalent to `--mode review`.

### Question 5

**Q:** Reconciliation aggressiveness on existing comments?

**How to pick:**

- `validate-then-keep` `(default)` — re-validate every existing thread; reply on the ones that drifted; do not unilaterally close anything.
- `aggressive-cleanup` — also dismiss threads that are clearly no-longer-applicable. Use when the PR has been re-pushed many times and old threads are noise.
- `read-only` — do NOT reply on existing threads at all; just produce new findings (Path A) or skip the validation pass (Path B). Use when re-reviewing without authority over the previous reviewer's comments.

### Question 6 (Bitbucket only)

**Q:** Task strategy for new Blockers / Critical findings?

**How to pick:**

- `task-per-blocker-and-critical` `(default)` — create a Bitbucket task for every Blocker and every Critical finding linked to its inline comment. Standard hygiene.
- `task-per-blocker-only` — tasks only for Blockers; Criticals stay as inline comments only. Use when the team uses tasks lightly.
- `no-tasks` — skip task creation entirely. Use when the team does not use tasks.

Path B note: the skill never creates new tasks on its own PR. It may resolve tasks tied to `Apply`'d comments after the fix is staged + validated.

### Question 7 (Path B / `mine` only)

**Q:** Apply local fixes via `--fix`?

**How to pick:**

- `no` `(default)` — draft replies only, leave the code unchanged. Pick when the goal is to triage feedback and answer reviewers, not ship the fix in this run.
- `yes` — for every reviewer comment classified `Apply`, dispatch the right `adk-build-*` skill (`adk-build-bugfix` for bug-shaped, `adk-build-refactor` for cleanup-shaped, `adk-build-feature` for behavior-change-shaped) as a focused subagent loaded with the comment + the affected files. Each fix is followed by an `adk-review-local` pass. Local commits stay staged — push is a separate, user-gated action. Equivalent to passing `--fix` (or `--mode fix`) on the CLI.

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
