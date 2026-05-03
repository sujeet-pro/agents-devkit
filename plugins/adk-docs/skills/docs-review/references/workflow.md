# `docs-review` — workflow detail

## Phase 0 — prompt expansion

1. Resolve the target shape by the argument:
   - `docs/**/*.md` or other local path → local markdown.
   - `http(s)://.../…` (generic) → WebFetch the URL, treat as HTML or
     markdown depending on response.
   - `*.atlassian.net/wiki/*` → Confluence page via the workspace
     Atlassian connector.
   - `docs.google.com/document/*` → Google Doc via the workspace
     Google Drive connector.
2. Pick slug from the target basename. Create `.temp/task-<slug>/`.
3. Fetch the target; store raw content in `.temp/task-<slug>/input.md`
   (for non-local targets; includes last-modified + last-editor
   metadata when available).

## Phase 1 — preflight

1. `bin/adk-info --check`.
2. If the target is Confluence: run `claude mcp list` (or the adk
   equivalent) and confirm the Atlassian workspace connector is
   connected. If not, stop with the fix-this message.
3. If the target is GDoc: same for the Google Drive workspace connector.
4. Resolve the repo the doc describes via `~/.config/adk/repos.md`.
   If the doc doesn't match a repo (generic / vendor doc), set
   `repo=none` and narrow the audit to structure + readability only.
5. Capture last-modified + last-editor (for shared targets) to drive
   the `--fix` gate.

## Phase 2 — accuracy check

Follow `references/accuracy-check-protocol.md`. Summary:

1. Parse claims from the doc: anything that reads "does X" / "returns
   Y" / "uses Z" / a specific command / a specific path / a specific
   env var / a specific flag / a specific library version.
2. For each claim, locate the supporting code:
   - If the doc cites the path, open it.
   - If it names a symbol, `grep` for it.
   - If it cites a command, run it in a safe sandbox (e.g. `--help`
     only) or read the script file.
3. Classify the claim: `OK` | `wrong` | `stale-but-correct` |
   `unverifiable`.
4. Log to `.temp/task-<slug>/claims.md`.

## Phase 3 — structure + freshness + readability

1. Heading hierarchy: no skipped levels, max depth 4.
2. Internal link integrity: every `[text](url)` and `[text](#anchor)`
   resolves.
3. External link integrity (`http(s)`): optional HEAD check; surface
   404s as Should-Have at most (link rot ≠ doc wrongness).
4. Duplication: no section that restates another section.
5. Freshness: compare doc last-modified to `git log -1 --format=%ci`
   on each cited file. Flag mismatches >180d as a signal, not a
   finding.
6. Readability (audience-calibrated): runbooks are imperative and
   concrete; README overviews are 3-6 sentences not 30; ADRs have a
   decision up front; migration guides have a rollback.

## Phase 4 — triage

1. For each issue, pick severity per the rubric in
   `references/output-format.md`.
2. Group findings by severity in `review.md`.
3. Include evidence per finding: `doc:§X line Y` + `code:<file>:<lines>`.

## Phase 5 — optional `--fix`

1. Partition findings into `non-controversial` and `controversial`
   (per `references/modes.md`).
2. For non-controversial:
   - Local md: edit in place, preserving voice.
   - Confluence: via the Atlassian workspace connector (update page;
     preserve ADF structure).
   - GDoc: via the Google Drive workspace connector (append / edit in
     place; preserve formatting).
   - Write diff to `.temp/task-<slug>/fixes-applied.md`.
3. For controversial: write `fixes-deferred.md` with the proposed
   change + rationale, surface to user.
4. Re-validate: fetch the updated target and confirm the fixes took
   effect.
