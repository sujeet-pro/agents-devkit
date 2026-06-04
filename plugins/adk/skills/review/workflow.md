# review — workflow

Five phases. Read-only by default; `--fix` extends Phase 4 with apply + push. The phased process is the contract; the **Workflow tool** is how the heavy middle phase fans out for real diffs.

## Phase 0 — gather

- Resolve the diff per `dispatch.md`:
  - **GitHub PR** → `gh pr view <url> --json title,body,author,baseRefName,headRefName,headRefOid,additions,deletions,files` and `gh pr diff <url>`. Read existing review threads with `gh pr view <url> --json comments,reviews` so you don't re-raise resolved concerns.
  - **local** → `git diff $(git merge-base HEAD origin/<default>)...HEAD` (or `git diff` for unstaged work).
  - **doc / thread** → fetch directly.
- Pull repo conventions that scope the review: `CLAUDE.md`, `AGENTS.md`, lint config, `package.json` / `pyproject.toml`, recent commits for style.
- Note diff size. > 5,000 LOC → refuse a single pass (`rules.md`); recommend chunking.

## Phase 1 — advise

- In `-i` mode, ask up to 3: severity bar, which dimensions, post policy (if it's someone else's PR). In default mode pick sensible defaults (all six dimensions, report-only) and **state the assumptions** in the output.
- **Challenge** if the PR already has ≥2 approvals: "fresh full pass, or just sanity-check the last commit?"
- Decide: inline review (trivial diff) or Workflow fan-out (anything non-trivial).

## Phase 2 — review (the Workflow)

For any non-trivial diff, drive a **Workflow**:

1. **Fan out one agent per applicable dimension** (`code-reviewer` for correctness/tests/performance/readability/consistency; `security-auditor` for security; `test-engineer` consulted for the tests dimension). Each gets the diff + the files it needs + its single dimension. They run in parallel.
2. **Adversarially verify** each surfaced finding: spawn an independent skeptic that tries to *refute* it (is the quote real? is the triggering input plausible? is it already handled elsewhere in the diff?). A finding survives only if it isn't refuted.
3. **Dedup + synthesize** the survivors into one severity-ordered list.

Sketch:
```js
const DIMENSIONS = [
  {key:'correctness', agent:'code-reviewer'},
  {key:'security',    agent:'security-auditor'},
  {key:'tests',       agent:'test-engineer'},
  {key:'performance', agent:'code-reviewer'},
  {key:'readability', agent:'code-reviewer'},
  {key:'consistency', agent:'code-reviewer'},
];
const results = await pipeline(
  DIMENSIONS,
  d => agent(`Review ONLY the ${d.key} dimension of this diff: …`, {agentType:d.agent, phase:'Review', schema:FINDINGS}),
  review => parallel(review.findings.map(f => () =>
    agent(`Try to refute this ${f.dimension} finding — default to refuted if uncertain: ${JSON.stringify(f)}`,
          {phase:'Verify', schema:VERDICT}).then(v => ({...f, refuted:v.refuted})))),
);
const confirmed = results.flat().filter(Boolean).filter(f => !f.refuted);
```
A trivial diff (≤ ~150 LOC, single concern) may skip the Workflow — review inline, still one dimension at a time, and say you skipped it.

## Phase 3 — validate findings

- Re-open each cited file and confirm the quote is byte-exact (regenerate the line ref if the diff shifted it).
- Drop any finding that duplicates an existing PR comment (PR targets only).
- For `--fix`: re-confirm no force-push / no merge / no protected-branch push is implied.

## Phase 4 — report (and post / fix if asked)

- Write the severity-ordered findings (`persona.md` output shape) and the `ship | iterate | reject` recommendation. Lead with blockers.
- **default** — stop here; nothing posted.
- **`-i`** — walk each finding (accept / reject / edit), then report only the accepted set.
- **post to a PR** — only if the task asked for it; confirm the batch first (`rules.md`).
- **`--fix`** — hand accepted findings to the `implementer` agent, validate (repo typecheck/lint/tests), then push to the PR head branch **after explicit confirmation**.

## Narrate

State each phase boundary, the fan-out ("reviewing 6 dimensions in parallel"), any skipped dimension + why, and any gap (a file you couldn't see). Never go silent for more than a phase.
