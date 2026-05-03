# `audit-repo` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are surfaced in the methodology section.

## Phase 0 questions

1. **Audit `<repo-name>` at `<resolved-path>`?**
   - _How to pick:_ default = path arg or CWD walk-up to `.git`.
   - _Skip when:_ unambiguous.

2. **Run all 6 dimensions, or a subset?**
   - _How to pick:_ default `all 6` (security, performance, quality, deps, test-coverage, architecture).
   - _Skip when:_ user passed `--dimensions` explicitly OR `--auto`.

3. **Restrict scope to a sub-path?**
   - _How to pick:_ default `whole repo`.
   - _Skip when:_ user passed `--scope` OR repo is small (<1000 LOC).

## Phase 1 questions

4. **Tool `<name>` not installed; the `<dimension>` dimension will run heuristics-only. OK?**
   - _How to pick:_ default `yes` (still useful with heuristics; install command surfaced in report).
   - _Skip when:_ `--auto` (default applies silently).

## Phase 2 questions

5. **Inventory complete (<n> files; <m> LOC). Proceed to dimension passes?**
   - _How to pick:_ default `yes`.
   - _Skip when:_ `--auto` OR inventory is fast (<30s).

## Phase 3 questions

6. **Estimated time for all 6 dimensions: ~<n> minutes. Proceed, or set --time-budget?**
   - _How to pick:_ default `proceed`.
   - _Skip when:_ `--auto` OR estimate <3min.

## Phase 5 questions (under `-i`)

7. **For each Top-10 finding: accept, re-tier, discard, or merge with another?**
   - _How to pick:_ default `accept`.
   - _Skip when:_ `--auto`.

8. **Add a finding the heuristic missed?**
   - _How to pick:_ default `no` — the user volunteers.
   - _Skip when:_ `--auto`.

9. **Top-N count: 10 (default) or other?**
   - _How to pick:_ default `10`. Override with `--top <n>`.
   - _Skip when:_ `--auto` OR user passed `--top` explicitly.

10. **Include "what's healthy" section?**
    - _How to pick:_ default `yes` (the section is REQUIRED unless `--no-healthy`).
    - _Skip when:_ `--auto` OR `--no-healthy` flag set.

## Phase 6 questions

11. **Report is `<n>` lines. Show executive summary + offer-depth, or full doc?**
    - _How to pick:_ default `executive summary` + offer-depth.
    - _Skip when:_ `--auto`.

## Anti-rules for asking

- **Never ask about something the meta-info answers.**
- **Never stack 3 questions in one turn.**
- **Never ask under `--auto`** — defaults apply silently.
- **No SHARED-STATE actions to gate.** This skill is read-only; no push, no comment, no merge. So no mandatory gates.
- **Once-per-session.** If the user already answered the same question (e.g. "yes, run all 6 dimensions"), don't re-ask within the same audit slug.

## Why this skill asks fewer questions than `review-pr`

- No code mutation → no fix-application question.
- No comment posting → no post-style question.
- No reconciliation → no per-existing-comment question.
- Fixed dimension model (6) → fewer per-dimension decisions.
- Read-only → no SHARED-STATE gates.

Under `--auto`, this skill typically asks ZERO questions and runs end-to-end (writes the report; surfaces it).

Under `-i`, the typical interaction is:

1. Skill: "Audit `acme/checkout-api`? Inventory complete (47 files, 12.4K LOC). Proceed?"
2. User: yes.
3. Skill: runs all 6 dimensions; ~6 min.
4. Skill: "Top-10 ready. Walk each?"
5. User: walks; re-tiers 1; accepts 9.
6. Skill: writes report; surfaces.
