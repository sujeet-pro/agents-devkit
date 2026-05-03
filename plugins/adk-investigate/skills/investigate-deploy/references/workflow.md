# `investigate-deploy` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the user's question in one sentence.
2. **Resolve repo:**
   - `<repo>` arg if given.
   - Else, walk up from CWD to a `.git` directory; `git remote get-url origin` to find `<owner/repo>`. Map back to `~/.config/adk/repos.md.repos[].name` for canonicalization.
   - Else, ask the user. List candidates from `repos.md`.
3. **Resolve workflow:**
   - `--workflow` flag if given.
   - Else, `repos.md.repos[<repo>].deploy_workflow` if set.
   - Else, fall back to literal `deploy` and warn at Phase 3 if zero runs returned.
4. **Resolve window:**
   - `--window` flag (e.g. `last 2h`, `last 30m`, `today`).
   - Else default `last 2h`.
5. **Resolve symptom timestamp** (optional, passed by parent skill like `investigate-incident`):
   - `--symptom-time <ISO>` flag.
   - Used to tag near-symptom candidates in Phase 3.

Output: `entities.md` table in `.temp/task-<slug>/investigation/deploy/`.

## Phase 1 — preflight

1. `gh --version` — `gh` CLI installed.
2. `gh auth status` — authenticated to GitHub.
3. (If repo provided as argument and not local) — `gh api repos/<owner>/<repo>` returns 200.
4. `bin/adk-info --check repos github` — meta-info parses.

## Phase 2 — execute

1. Run:

   ```bash
   gh run list \
     --repo <owner/repo> \
     --workflow=<workflow> \
     --limit <N> \
     --json status,conclusion,createdAt,event,headBranch,headSha,actor,url,name,displayTitle
   ```

2. Filter to runs within the resolved window (post-process the JSON, since `gh run list` lacks a window flag).
3. For each run, extract:
   - `createdAt` (ISO timestamp).
   - `status` (in_progress / completed).
   - `conclusion` (success / failure / cancelled / timed_out / skipped / startup_failure / null).
   - `headSha` (the deployed SHA).
   - `actor.login` (the triggering user).
   - `url` (link to the workflow run page on GitHub).
   - `displayTitle` (the deploy title — typically "deploy: <ref>" or commit message subject).
   - `headBranch` (typically `main` for production deploys).
4. Compute duration if `completed_at` available.
5. (Optional) Cross-reference Datadog deploy events:
   - If `datadog` MCP reachable in this session, call `get_events --query "sources:my_apps tags:deploy service:<service>" --window <window>`.
   - Match each `gh run` to a DD event by `(time, sha)` if available.
6. Tag rows:
   - `failed` if `conclusion in [failure, cancelled, timed_out, startup_failure]`.
   - `slow` if duration > 2x the median of the returned set.
   - `near-symptom` if `--symptom-time` provided AND `abs(createdAt - symptom_time) <= 30min`.

## Phase 3 — summarize

1. **Render timeline** as a table, newest first by default. Columns: `Time (UTC) | Status | Duration | SHA | Author | Title | URL`.
2. **Highlight failures** in a separate `Failed deploys` section.
3. **Near-symptom candidates** in a separate section if `--symptom-time` set, sorted by `abs(time-delta)`.
4. **Cross-source: Datadog deploy events** in a section if DD reachable; table matched against `gh run` set.
5. **Summary line** at the top: "<N> deploys in window; <K> failed; <M> near-symptom candidates".

## Phase 4 — report

Emit `.temp/task-<slug>/investigation/deploy.md` per `output-format.md`. Return path to caller.

## Loop control

- Cap `--limit` at 200 runs (anything more is a different question).
- If 0 runs returned: warn the operator. Likely cause: wrong `--workflow` name. Suggest `gh workflow list --repo <repo>` to discover.
- If `gh` rate-limited (60 req/h unauthenticated, 5000 req/h authenticated): surface and stop.
