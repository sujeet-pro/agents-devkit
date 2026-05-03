# `docs-review` — modes

Supports `--auto` (default), `-i`, and `--fix`. Read
`references/interaction-contract.md` for the universal shape.

## `--auto` (default)

- Phase 0–4 run without approval gates.
- Report is produced; nothing is written to the target doc.
- Final surface: a sorted findings list + evidence.

## `-i` / `--interactive`

- Per-phase approval gates.
- Useful when the target is ambiguous (which doc? which section?)
  or when the user wants to scope the audit (accuracy only; structure
  only).

## `--fix` — non-controversial only

`--fix` composes with `--auto` or `-i`. It applies only
**non-controversial** corrections.

### What counts as non-controversial

| Change | Fix under `--fix`? |
| --- | --- |
| Wrong command flag (`-r` → `--recursive`) | yes |
| Renamed file path (`src/app.js` → `src/app/index.ts`) | yes |
| Changed default value (`timeout 30 → 10`) | yes |
| Removed feature (the referenced flag is gone) | yes (delete the paragraph) |
| Obvious typo (`teh` → `the`) | yes |
| Broken internal link (`#old-anchor` → `#new-anchor`) | yes |
| Wrong version number (`2.7` in doc; `3.2` in `build.gradle.kts`) | yes |
| Rewriting the doc's voice / tone | **no** — out of scope |
| Restructuring sections (moving content between headings) | **no** |
| Adding a new section for missing context | **no** (Should-Have finding) |
| "This paragraph reads awkwardly" fix | **no** (Nitpick) |
| Changing vocabulary to match a style guide | **no** |

### Controversial changes

Controversial changes land in `fixes-deferred.md` with rationale; the
user decides whether to apply.

### Remote targets

- Confluence pages: `--fix` goes through the workspace Atlassian
  connector. First confirm the page is bot-authored or opt-in for
  human-authored. Always re-fetch after update to confirm.
- Google Docs: same via the workspace Google Drive connector.
- Human-authored pages (non-bot last editor) **always** require
  explicit opt-in before any change, even under `--auto --fix`.

### Guardrails

1. Never apply more than 20 `--fix` corrections in a single run on a
   shared page. Paginate with user approval.
2. Always back up the target before first write
   (`.temp/task-<slug>/backup/<target>`).
3. Re-validate the fix actually landed (fetch the updated doc, confirm
   the corrected claim is now correct).
