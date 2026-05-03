# The mode contract (full text)

## The three modes

### `--auto` (default)

End-to-end execution. Skip per-phase approval gates. Pick the documented `(default)` option at every decision. Still **stop** before destructive shared-state actions (push, post, delete, merge) — these always confirm at least once.

### `-i` / `--interactive`

Per-phase approval gates. Show the plan; ask for approval; allow edits. Used when the user wants to inspect each step before execution. Mutually exclusive with `--auto`.

### `--fix`

Apply changes locally, validate, push. **Only available on skills where mutation is the goal** — typically: `review-pr`, `review-code-changes`, `review-feedback`, `docs-review`, `audit-pr`. Other skills don't accept `--fix` (and reject it at parse time with a helpful message).

## Compositions

| Combo | Behavior |
| --- | --- |
| `--auto` (alone) | Default. End-to-end without per-phase gates. |
| `-i` (alone) | Per-phase gates; nothing auto. |
| `--fix` (alone) | Implies `--auto` for the apply step but still gates before push/post. |
| `--auto --fix` | End-to-end with auto-apply. **Never** auto-merges, **never** force-pushes protected branches, **never** auto-deletes. |
| `-i --fix` | Per-phase gates AND auto-apply per finding (after explicit accept). |
| `--auto -i` | Parse error. |

## Hard rules across every skill

1. **Mutation gating.** `--fix` is only on skills where mutation is the goal.
2. **First-push gate.** Push to a remote branch ALWAYS asks before the first push of a session, even under `--auto --fix`. Subsequent pushes in the same session may proceed without re-asking.
3. **Comment-post gate.** Same rule as push.
4. **Merge gate.** NEVER auto. Always asks. Even under `--auto --fix`.
5. **Branch-delete gate.** NEVER auto. Always asks.
6. **Force-push block.** Force-push to `main` / `master` / `develop` / any branch in `~/.config/adk/github.md.forbid_force_push_branches` is BLOCKED. Even under `--auto --fix`.
7. **Approval-gate text.** When asking, show the exact command / payload. Don't describe it abstractly.
8. **Reporting.** Every skill reports decisions made under `--auto` in the final report (full transparency).

## Why this contract exists

It makes adk predictable. The user always knows:

- "If I want unattended, I pass `--auto`. The skill picks the safe defaults and tells me what it picked."
- "If I want a review, I pass `-i`. The skill walks me through each decision."
- "If I want changes applied, I add `--fix`. Even then, nothing irreversible happens without my OK."

Skills MAY override individual gates with documented justification (e.g. `review-pr` can post comments without re-asking each one under `--auto` because that's the skill's purpose). Overrides are listed in the skill's `Constitution` section.
