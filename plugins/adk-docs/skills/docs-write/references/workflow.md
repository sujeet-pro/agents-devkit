# `docs-write` — workflow detail

## Phase 0 — prompt expansion

1. Classify the doc type from the prompt. The matcher:
   - `README` / `readme` → `readme` template.
   - `ADR` / `decision record` → `adr` template.
   - `runbook` / `on-call` / `incident response` → `runbook` template.
   - `migration` / `upgrade guide` / `breaking change` → `migration-guide` template.
   - `API reference` / `endpoint docs` / `SDK surface` → free-form with API reference skeleton.
   - anything else → free-form.
2. Resolve the repo via `~/.config/adk/repos.md` (walk up from CWD to
   find `.git`, match by path, fallback to `git remote get-url`).
3. Pick a slug via `bin/adk-task-slug "<prompt>"`. Create
   `.temp/task-<slug>/` and write `prompt.txt` (verbatim user prompt +
   ISO timestamp).
4. Read `~/.config/adk/docs.md` for `audience_default`, `adr_path`,
   `runbook_path`, and template path overrides.

## Phase 1 — preflight

1. Run `bin/adk-info --check`. Stop with parse errors if any.
2. Confirm the repo is clean enough for a doc write — dirty tree is OK
   (docs don't depend on clean working copy) but note it in the report.
3. Decide the canonical target path (`--fix` mode only):
   - README → `README.md` at repo root (unless the prompt names a
     subservice and a nested README is more appropriate).
   - ADR → next free number under `docs.md.adr_path` (default
     `docs/adr/`), zero-padded to 4 digits.
   - Runbook → `docs.md.runbook_path` (default `docs/runbooks/`).
   - Migration guide → `docs/migrations/<from>-to-<to>.md`.
4. If the target path already exists, warn and surface options: refresh
   in place (default), write alongside (`<name>-v2.md`), or abort.

## Phase 2 — gather source of truth

1. Read the files / configs / commands the doc will describe. For a
   README, that's: `package.json` / `pyproject.toml` / `go.mod` /
   `build.gradle.kts`, the `bin/` folder, any `scripts/`, the `Dockerfile`,
   the README of the parent repo if this is a sub-package. For a runbook,
   that's: the service entry-points, the health endpoint, the deploy
   workflow, the rollback path. For an ADR, that's: `git log -20
   --format=%s%n%b%n-----` scoped to the area + the current code shape.
2. Build an evidence map in `.temp/task-<slug>/sources.md`:
   ```
   claim: add-to-cart is idempotent
   file: src/main/kotlin/com/acme/checkout/CartService.kt
   lines: 42-58
   evidence: |
     The `addLine` method uses `upsert(cartId, sku)` with a unique
     constraint on (cartId, sku), so repeat calls don't duplicate.
   ```
3. If a fact can't be verified from the code, mark it `TODO: verify` in
   the evidence map and flag to the user in Phase 4. Do NOT ship the
   unverified claim in the prose.

## Phase 3 — draft

1. Pick the template: `references/templates/<doc-type>.md` or free-form.
2. Draft into `.temp/task-<slug>/draft.md`. Fill every template
   placeholder with real values from the evidence map — no "<fill in>"
   or "lorem ipsum".
3. Audience-calibrate per `references/audience-calibration.md`.
4. Copy code snippets verbatim from the cited files — never paraphrase.
5. Append the validation block at the bottom of the draft:
   ```
   <!-- validation
   claims:
     - path: <repo-path>
       lines: <start>-<end>
       claim: <short sentence>
   audience: <engineer|pm|em|mixed>
   template: <name|freeform>
   external-quotes: <count>  # must be 0 unless each ≤15 words
   todos-verify: <count>     # must be 0 at --fix time
   -->
   ```

## Phase 4 — validate + report

1. Run `references/validator.md` gates. If any fails, loop back to
   Phase 2 (fetch more evidence) or Phase 3 (rewrite).
2. If not `--fix`, stop here. Final report at `report.md`.
3. If `--fix`:
   - Re-read the canonical target path to detect any concurrent changes.
   - Write the draft to the canonical path.
   - `git add <path>` (stage only).
   - Run `git status` and capture the change in the report.
   - Never run `git commit` or `git push` — that's `docs-commit-message`
     and `docs-publish-*`.
4. Write `.temp/task-<slug>/report.md` per `references/output-format.md`.

## Loop control

- If the validator fails 3× on the same gate, stop and surface to the
  user — don't rewrite the whole draft on the 4th pass.
- If the evidence map is empty (no cited files), stop — you're about to
  ship speculation.
- Never lower the audience calibration to pass a validator (e.g. don't
  strip implementation detail to shorten the doc). Split into two docs
  or push back on the scope.
