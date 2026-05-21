# adk v4 — unified overhaul plan

Status: design — not implemented.
Scope: GitHub-first migration · filesystem restructure · dependency-aware sync DAG · skill rewiring · CLI additions · install/migration · interactive TUI.
Execution: agentic teams (§7 details the team-per-phase breakdown).

This is the single master plan. The earlier `adk-tui.md` is a pointer here.

---

## 0. Vision

adk has grown into a working pipeline but with rough edges:
- Some legacy filesystem (`pr-reviews/`, `improve/`, `memory/`), some new (`.indices/`, `branches/<slug>/`).
- PR-review task folders mix review-specific files with shared concerns (worktree, index, docs).
- Bitbucket and GitHub are treated as symmetric peers in code, but reality is GitHub-primary within a week.
- Multi-branch indexing exists at the indexer layer; the CLI uses it; the **sync pipeline does not yet exploit it for ordering**.
- No interactive front-end.

**v4 lands one coordinated overhaul that:**

1. Makes **GitHub-first** the default everywhere (terminology, routing, defaults, fallback to `gh` CLI).
2. Restructures `~/.agents-devkit/` so that **a branch dir and a PR task dir have the same shape**, with skill-specific files isolated in subfolders.
3. Replaces today's straight-line sync with a **dependency-aware 3-tier DAG**: existing bases serve their PRs immediately, branches needing a base get one built (user **or** auto-created), and singleton PRs run as full indexes. A PR becomes "ready for review" only after its prerequisites are met.
4. Auto-creates **transient base indexes** for branches shared by ≥2 queued PRs, tagged so the TUI can show them; cleans them up after 24h of zero use.
5. Migrates skill-specific working dirs to a `skill-<name>/` prefix. **Migration preserves existing prepared indices** — re-indexing every PR after a layout change would burn hours of CPU; the install script MOVES task folders and branch indices, it does not rebuild them.
6. Adds a **post-review Slack notification** that tags the PR author in the original thread with the verdict + summary + link to the PR.
7. Adds a **fully automated review mode** (`adk auto`) — headless sync + parallel reviews + Slack roll-up; scheduler-friendly.
8. Adds an iterative **`prj-adk-pr-auto` project-level skill** (lives in `<repo>/.claude/skills/`) — runs `adk auto` at growing batch sizes (1 → 4 → all), observes failures via verbose logs, proposes + applies fixes, repeats until clean. The auto-improve loop is itself a skill, scriptable, repeatable.
9. Adds a **verbose mode** (`--verbose` / `-v`) to every CLI verb. Off by default; writes structured debug logs to `~/.agents-devkit/logs/` so dev users and the `prj-adk-pr-auto` skill can observe behaviour.
10. Adds a Textual **TUI** that surfaces the whole pipeline live: queue list, per-row prep progress, "review" enabled only when prereqs are met, parallel batched runs, repo & branch management. **Built LAST**, after the skill + CLI version of every feature is stable.
11. Enforces a **single binary + CLI-as-sole-API** layering: every operation goes through `adk <verb>`; TUI and skills both shell out; nothing imports the implementation modules directly.
12. Drives the whole build using **agentic teams** — each phase has a lead/worker/reviewer breakdown so independent units can run in parallel.

The migration runs through `install.sh`, idempotently. Each phase is shippable on its own.

**Safety reminder:** all of this runs on the user's machine. No destructive operation runs without explicit confirmation; migration is non-destructive (move + verify, never delete-then-recreate); the auto-improve loop has no permission to push, merge, or modify shared state beyond what the review pipeline already does.

---

## 1. Current state snapshot

Confirmed by re-reading the repo on $(date +%Y-%m-%d). Anything marked ✓ is in-tree today and should not be re-implemented:

**Filesystem & data:**
- `~/.agents-devkit/repos/<name>/` ✓ clone at the top, `.indices/<name>/branches/<slug>/{code-index,branch-meta.json}/` per-branch index (mid-migration shape).
- `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/` ✓ legacy PR task root.
- `pr-queue.json5` row schema captures `target_branch`, `head_oid`, `status` ∈ {`pending`, `in_review`, `reviewed`, `comments`, `approved`, `merged`, `declined`, `error`, `reminded`}, plus `last_reviewed_*`, `last_reminded_at`. ✓
- `memory/` exists, is empty, has no callers. Drop in Phase P2.

**Multi-branch indexing:**
- `scripts/lib/code_index/base_index.py` ✓ exposes `BranchIndex`, `list_branch_indexes`, `get_branch_index`, `pick_base_index`, `seed_copy`, `is_fresh`.
- `repo.py` ✓ has `cmd_add`, `cmd_update`, `cmd_branch_{add,remove,list}`, `cmd_migrate`, `_migrate_if_legacy`, multi-branch dirs.
- `pr_sync.py::_audit_base_indexes` ✓ groups queued rows by `(repo, target_branch)`, can run in `off` / `warn` / `auto` mode, calls `adk repo branch add|update` for gaps.

**Sync pipeline (today, in pr_sync.py):**
1. `pr-scan`
2. `pr-queue update --all` (metadata + target_branch capture)
3. `pr-queue clean` (drop merged)
4. `pr-task clean-orphans`
5. `pr-queue remind`
5.5 `_audit_base_indexes` (NEW since the original plan)
6. `pr-task prepare --all`

**Gap (this plan closes):**
The audit runs at 5.5 and can build missing bases — but **prepare still iterates the queue in arbitrary order**, and there is no `ready_for_review` flag on rows. The TUI cannot tell "this PR is ready to review now" from "this PR is mid-prep". §5 fixes both.

**Already done (don't replicate):**
- GitHub `gh` CLI is the metadata fetcher today (pr_scan.cheap_pr_meta uses `gh pr view`). ✓
- `head_sha` is captured under `head_oid` field (rename pending).
- target_branch capture works for both GitHub (`baseRefName`) and Bitbucket (`destination.branch.name`).

---

## 2. Read-before-build gate (mandatory per phase)

Every phase below runs §2 before any code is written. The implementer:

1. Reads `bin/adk` for the live verb list.
2. Reads every file under `skills/adk-cli/scripts/` and `skills/adk-pr-review/scripts/` that the phase touches.
3. Reads `SKILL.md` for `adk-pr-review` (and any other skill being modified).
4. Reads `shared/constitution.md` (§I.3 no auto-merge, §I.4 posting policy, §VII secret handling).
5. Reads `shared/paths.md` for canonical roots.
6. Inspects `~/.agents-devkit/` on the dev machine to see what's actually on disk.
7. Greps for callers of any symbol about to be renamed.
8. Lists any open PRs touching the same files.

**Output of the pass:** a delta note in the phase PR description + in-place edit to this plan with `<!-- updated YYYY-MM-DD: <reason> -->`. The lead agent (§7) runs this gate before spawning workers.

---

## 3. Target architecture (end state)

```
~/.agents-devkit/
├── config/                              # user-owned (preserved)
│   ├── core.yaml                        # adds defaults.platform=github, defaults.repo=…
│   ├── pr-queue.json5
│   ├── connectors/
│   └── links.json5
│
├── repos/                               # shared resource
│   └── <repo-name>/
│       ├── repo-meta.json               # catalog: name, url, platform, default_branch, tracked_branches[]
│       ├── original-clone/              # full clone — source for worktrees, never modified by skills
│       │   └── .git/  …
│       ├── branch-<DEFAULT>/            # always present
│       │   ├── branch-meta.json         # branch, slug, last_indexed_sha, last_indexed_at, embed_model
│       │   ├── code/                    # git worktree at HEAD of this branch
│       │   ├── code-index/              # chunks.jsonl + chunks.lance + meta.json
│       │   ├── scip/<lang>/index.scip   # optional
│       │   └── docs/                    # supplied docs
│       └── branch-<other>/  …
│
├── tui/                                 # NEW — Textual app state + logs
│   ├── state.json
│   ├── workers/<pid>.json               # heartbeat from each running worker (TUI-launched OR external)
│   └── logs/<worker-id>.log
│
├── skill-pr-review/                     # was pr-reviews/
│   └── <repo>_pr-<n>/                   # mirrors a repo branch dir's shape
│       ├── code/                        # worktree at PR head
│       ├── code-index/
│       ├── scip/
│       ├── docs/
│       └── pr-review/                   # NEW — review-specific bundle
│           ├── pr.json
│           ├── pr-comments.json
│           ├── diff.patch
│           ├── precis.md
│           ├── findings.json
│           ├── validated-findings.json
│           ├── initial-findings.json
│           ├── validation-report.json
│           ├── triage.json
│           ├── posting-plan.json
│           ├── post-result.json
│           ├── comment-actions.json
│           ├── findings.md
│           ├── report.md
│           ├── state.json
│           └── queue-context.json
│
├── skill-investigate/   skill-review/   skill-sync/
├── skill-setup/         skill-improve/  skill-explain/
└── skill-document/      skill-implement/
```

A branch dir under `repos/` and a PR task dir under `skill-pr-review/` have **the same shape** (`code/`, `code-index/`, `scip/`, `docs/`), plus one skill-specific subfolder for PRs (`pr-review/`). Future skills add their own subfolder using the same pattern.

---

## 4. Queue row schema (v4)

```json5
{
  "pr_url": "https://github.com/acme/storefront-bff/pull/1234",
  "platform": "github",
  "owner": "acme",
  "repo": "storefront-bff",
  "pr_number": 1234,

  // metadata (refreshed by pr-queue update --all)
  "title": "feat: coupon engine",
  "author": "sujeet",
  "head_sha": "a4f2c1...",
  "target_branch": "main",
  "merged_at": null,
  "state": "OPEN",                      // origin-API state, verbatim
  "status": "pending",                  // canonical adk status — see below
  "last_checked_at": "...",

  // review lifecycle (set by /adk-pr-review on completion)
  "last_reviewed_at": null,
  "last_reviewed_head_sha": null,
  "approved_host": null,
  "recommendation": null,
  "last_reminded_at": null,

  // prep lifecycle (NEW in v4)
  "prep_status": "pending",             // pending | preparing | ready | failed | skipped
  "prep_started_at": null,
  "prep_completed_at": null,
  "prep_head_sha": null,                // the sha that was prepared
  "prep_used_base": null,               // (repo, branch) of the base index seeded from, if any
  "prep_error": null,

  // claim
  "taken_at": null,

  // extras from pr-scan
  "slack": {
    "channel_id": "C…",
    "thread_ts": "…",                  // thread root
    "message_ts": "…",                 // the message that carried THIS PR link (reaction target)
    "link_origin": "main" | "reply",   // where in the thread the link appeared
    "n_pr_links_in_message": 1         // disambiguator for multi-PR messages
  },
  "supporting_docs": [ "https://…" ],

  // derived (computed, not stored):
  // ready_for_review = (prep_status == "ready" AND prep_head_sha == head_sha
  //                     AND status not in {merged, closed})
}
```

**Status set (canonical, v4 — GitHub-first):**
- `pending` · `in_review` · `reviewed` · `comments` · `approved` · `merged` · `closed` (replaces `declined`) · `error` · `reminded`

**`prep_status` state machine:**
```
pending → preparing → ready
              ↘ failed (with reason)
              ↘ skipped (e.g. merged before prep finished)

ready → preparing  (when head_sha moves)
```

**`ready_for_review`** is a derived predicate (not a stored field). Anywhere we need it, callers compute it.

---

## 5. The dependency-aware sync DAG (the new algorithm)

### 5.1 Why

A repo with 8 open PRs all targeting `main` shouldn't trigger 8 full-from-scratch indexes (~30s each, ollama-bound). The right algorithm:

1. **Build the base index for `acme/foo:main` once** (~30s).
2. **Each PR seeds from that base** + indexes only its diff against the base (~2-3s per PR).

That's 30s + 8×3s = 54s, vs 8×30s = 240s. The base is also reusable for the next sync.

But if 2 of those 8 PRs target a different exotic branch with no base, they need full indexing. So PRs split into tiers: those that can seed (fast), those that can't (slow).

### 5.2 The DAG (executed by `adk pr-sync`)

```
Phase A · Discover
────────────────────
  A1  pr-scan                            (Slack → queue; new rows have no metadata)
  A2  pr-queue update --all              (metadata refresh; captures head_sha + target_branch
                                           + classifies merged/closed)
  A3  pr-queue clean                     (drop terminal rows + their task folders)
  A4  pr-task clean-orphans              (drop task folders without a queue row)

Phase B · Plan
────────────────────
  B1  Group non-terminal rows by (repo, target_branch):
        groups = {
          ("acme/storefront-bff", "main"):       [pr-1234, pr-1235, pr-1240, pr-1241],
          ("acme/storefront-bff", "release/v2"): [pr-1242, pr-1243],
          ("acme/checkout-fe",    "main"):       [pr-1233]
        }
  B2  For each group, classify base-index state via base_index.pick_base_index:
        - "fresh-user"  — exact-branch user index, age < max_staleness
        - "fresh-auto"  — exact-branch AUTO index, age < max_staleness
        - "stale-user"  — exact-branch user index, age >= max_staleness
        - "stale-auto"  — exact-branch auto index, age >= max_staleness
        - "missing"     — no exact-branch index
  B3  Decide auto-base candidates:
        For each "missing" group, if PR_count >= pr_sync.auto_base_threshold (default 2):
          → mark for AUTO-base creation in Phase C with `created_by: "auto"`
        Otherwise (singleton group, missing base):
          → mark PR(s) for Tier-2 (full-from-scratch indexing)
  B4  Emit the plan as plan.json under ~/.agents-devkit/tui/workers/sync-plan.json
       with each PR tagged (tier-0 | tier-1 | tier-2) so the TUI can render
       the DAG and the auto-vs-user origin of each base.

Phase C · Build / refresh BASES (the prerequisites)
────────────────────
  In parallel up to `pr_sync.base_jobs` workers (default min(CPU, 2)):

    For each group needing a base build:
       - "stale-user"  → adk repo update <repo> --branch <branch>          (refresh user base)
       - "stale-auto"  → adk repo update <repo> --branch <branch>          (refresh auto base)
       - "missing" w/ ≥ threshold  → adk repo branch add <repo> --branch <branch> --auto
                                     (creates with created_by: "auto",
                                      records auto_reason)
       - "missing" singleton       → no base; the PR goes to Tier-2

  Each completion updates plan.json so the TUI can promote rows
  (tier-1 → tier-0 once their base is fresh).

Phase D · Prepare PRs in three tiers (optimal ordering)
────────────────────
  Tier-0 (immediate · fresh existing base, user or auto):
     Doesn't wait for Phase C. Starts as soon as Phase B finishes.
     prep_status = preparing → ready
     adk pr-task prepare <pr-url>   (seeds from base; ~2-3s)

  Tier-1 (after-base · waiting on a base being built in Phase C):
     Each PR starts the moment its (repo, branch) base finishes building.
     prep_status = waiting_for_base → preparing → ready
     adk pr-task prepare <pr-url>   (seeds from the freshly-built base)

  Tier-2 (full-from-scratch · singleton groups with no base):
     Runs alongside Tier-0/1 in the shared prepare_jobs pool.
     prep_status = preparing → ready
     adk pr-task prepare <pr-url> --no-base-seed   (~30s)

  All three tiers share one pool of `pr_sync.prepare_jobs` workers (default 4).
  Tier-0 typically finishes first; Tier-1 staggered behind base completions;
  Tier-2 runs as background noise.

Phase E · Remind
────────────────────
  E1  pr-queue remind  (Slack pings for stale reviews)

Phase F · Cleanup
────────────────────
  F1  adk repo auto-bases clean    (delete auto-bases with 0 active users + ≥ 24h old)
       — never touches user-created bases
       — emits a one-line summary into plan.json: "auto-base cleanup: 2 removed"
```

### 5.3 Eligibility for `/adk-pr-review`

Eligibility rules are owned by **§6.u** (single source of truth for what makes a PR pickable). In short: not in a terminal status (`merged`, `closed`), not locked, prep is fresh, and the current `head_sha` hasn't already been reviewed.

`adk pr-queue get-next` returns the next FIFO row matching the §6.u predicate. `adk pr-queue claim <url>` succeeds for an explicit URL only if §6.u holds. The TUI's "Review" button enables only on rows where §6.u holds.

### 5.4 Auto-base lifecycle

A **base index** is the chunked + embedded view of a branch in `~/.agents-devkit/repos/<repo>/branch-<NAME>/code-index/`. Two origins:

| Origin | Created by | Cleanup | Survives if 0 users |
|---|---|---|---|
| **user** | `adk repo branch add` (explicit) | Manual only (`adk repo branch remove`) | Yes — never auto-deleted |
| **auto** | `pr-sync` Phase C, when ≥ `auto_base_threshold` PRs target an un-indexed branch | `adk repo auto-bases clean` (runs in `pr-sync` Phase F) | No — deleted after `auto_base_ttl_hours` of zero usage |

**`branch-meta.json` schema (extended):**

```json5
{
  "branch": "release/v2.1",
  "slug": "release-v2-1",
  "last_indexed_sha": "...",
  "last_indexed_at": "...",
  "embed_model": "nomic-embed-text",

  // NEW in v4:
  "created_by": "auto",                                // "user" | "auto"
  "created_at": "2026-05-21T09:00:00Z",
  "auto_reason": "shared by 3 PRs: #1234, #1235, #1240",   // only on auto
  "last_used_at": "2026-05-21T09:32:11Z"               // bumped whenever a PR seeds from it
}
```

**Auto-create policy** (in Phase C of `pr-sync`):
- Group has `prep_used_base` count >= `pr_sync.auto_base_threshold` (default 2) AND no exact-branch index → create with `created_by: "auto"`.
- Singleton group (1 PR, no base) → skip; the PR runs as Tier-2.

**Cleanup policy** (in Phase F of `pr-sync`, also via `adk repo auto-bases clean`):
- For every branch dir with `branch-meta.json:created_by == "auto"`:
  - Count non-terminal queue rows whose `target_branch == this.branch` (or which have `prep_used_base.branch == this.branch`).
  - If count == 0 AND `(now - created_at) >= auto_base_ttl_hours` (default 24h):
    - Delete `branch-<NAME>/` recursively.
    - Remove from `repo-meta.json:tracked_branches`.
- User-created branches are NEVER touched.

**Race / safety:**
- File lock per `(repo, branch)` during create — concurrent `pr-sync` runs serialize.
- Cleanup only fires when a `pr-sync` run is otherwise quiet (no Phase C / D in flight against that repo).
- An auto-base referenced mid-cleanup by a freshly-arrived PR is detected by re-reading the queue right before deletion.

### 5.5 What changes vs today

| Today | v4 |
|---|---|
| `_audit_base_indexes` runs as step 5.5 (warn / auto), then `pr-task prepare --all` iterates queue in arbitrary order | Phase B planner classifies groups; Phase C builds bases (user + auto); Phase D runs PRs in 3 tiers ordered by base-readiness |
| No `prep_status` on rows | New row field, lifecycle tracked end-to-end |
| `ready_for_review` not surfaced | Derived predicate consumed by the picker + TUI |
| `pr-task prepare --all` iterates queue with no tier ordering | Three-tier execution: Tier-0 (existing fresh base) starts immediately, Tier-1 (after-base) gated on its base, Tier-2 (full) runs in parallel |
| No auto-bases | Auto-created bases tagged in `branch-meta.json`; TUI shows origin; cleanup after 24h of zero use |
| Prep failures silent until you `pr-task info <url>` | `prep_status="failed"` + `prep_error` recorded; TUI shows it |

### 5.6 Concurrency

- `pr_sync.base_jobs` (default 2): how many base-index builds run concurrently. Bottleneck is ollama + disk I/O on the same machine.
- `pr_sync.prepare_jobs` (default 4): how many PR preps run concurrently across all 3 tiers.
- Cap globally by RAM (`min(N, ram_gb // 8)`).

### 5.7 Resumability

If `pr-sync` is interrupted mid-Phase-D:
- Rows in `prep_status="preparing"` are reset to `pending` on next start (or kept "preparing" with an expired `prep_started_at` and reclaimed).
- Rows in `prep_status="ready"` short-circuit on next run (head_sha unchanged → no work).
- Auto-bases partially built (no `last_indexed_sha` in `branch-meta.json`) are torn down and rebuilt next sync.

### 5.8 Config

`~/.agents-devkit/config/core.yaml`:
```yaml
pr_sync:
  base_jobs: 2                  # parallel base-index builds
  prepare_jobs: 4               # parallel per-PR preps (all 3 tiers share this pool)
  max_base_staleness_days: 7
  auto_base_threshold: 2        # NEW: PRs-per-branch needed to trigger auto-base
  auto_base_ttl_hours: 24       # NEW: how long a 0-use auto-base lingers before cleanup
```

### 5.8 Code mapping

The implementation lives in `skills/adk-cli/scripts/pr_sync.py`:

```python
def main(argv):
    ...
    # A · Discover
    _run_step("pr-scan", lambda: pr_scan.main([...]), log)
    _run_step("pr-queue update --all", lambda: pr_queue.main([...]), log)
    _run_step("pr-queue clean", lambda: pr_queue.main([...]), log)
    _run_step("pr-task clean-orphans", lambda: pr_task.main([...]), log)

    # B · Plan
    plan = _build_sync_plan(queue_path, embed_model=args.embed_model, log=log)
    _write_plan(plan)

    # C · Build/refresh BASES (parallel up to base_jobs)
    _build_bases(plan, jobs=cfg.pr_sync.base_jobs, embed_model=args.embed_model, log=log)
    plan = _refresh_plan(queue_path)  # re-classify after bases land

    # D · Prepare PRs in two tiers (parallel up to prepare_jobs)
    _prepare_tier(plan.tier1, jobs=cfg.pr_sync.prepare_jobs, log=log,
                  on_progress=_write_plan)
    _prepare_tier(plan.tier2, jobs=cfg.pr_sync.prepare_jobs, log=log,
                  on_progress=_write_plan)

    # E · Remind
    _run_step("pr-queue remind", ..., log)
```

`_build_sync_plan` + `_build_bases` + `_prepare_tier` are new helpers in `pr_sync.py`. The existing `_audit_base_indexes` is removed (subsumed by Phase B + C; its warn/auto modes are reduced to a Phase B output flag).

---

## 6. Architecture principle — single binary, CLI as the sole API

**One binary, `adk`.**

```
$ adk                  # no args  → TUI
$ adk pr-sync          # any verb → CLI op
```

Textual is **lazy-imported** so `adk <verb>` doesn't pay the TUI's import cost. Only `adk` (no args) loads the TUI module.

```python
# bin/adk (sketch)
def main(argv):
    if not argv or argv[0] not in SUBCMDS:
        from skills.adk_cli.scripts.tui.app import run_tui   # lazy
        return run_tui(argv)
    return dispatch(argv[0], argv[1:])
```

**Layering (strict — no skipping):**

```
┌─ Layer 1 · UI ──────────────┬────────────────────────────────┐
│  TUI (adk no-args)          │  Skills (/adk-pr-review, …)    │
└──────────┬──────────────────┴───────────────┬────────────────┘
           │ subprocess.run                    │ subprocess.run
           ▼                                   ▼
┌─ Layer 2 · public API (the CLI verbs) ────────────────────────┐
│  adk pr-sync · pr-task · pr-queue · repo · doctor · auto · …  │
└────────────────────────┬──────────────────────────────────────┘
                         │ Python imports
                         ▼
┌─ Layer 3 · implementation modules ────────────────────────────┐
│  queue_io · base_index · embedder · chunker · pr_scan · …     │
└────────────────────────┬──────────────────────────────────────┘
                         │ shell / network
                         ▼
┌─ Layer 4 · external systems ──────────────────────────────────┐
│  git · gh · ollama · MCP servers                              │
└───────────────────────────────────────────────────────────────┘
```

**The rule:** Layer 1 ALWAYS calls Layer 2. Layer 1 NEVER imports Layer 3 or 4 directly.

**The one exception:** the agent's Phase 2 (the actual review reasoning). The agent reads `pr-review/precis.md` + `diff.patch` + index queries and produces `pr-review/findings.json`. That's the agent's intrinsic work — not a layer call. Before Phase 2 and after Phase 2, the skill makes Layer-2 (CLI) calls.

**Consequence: every script the skill calls today gets a CLI wrapper in P6.** SKILL.md's "Process" stops referencing `python3 scripts/...` and references `adk pr-task <verb>` only. The skill is decoupled from internal script paths; refactors below Layer 2 don't break the skill.

| Today the skill calls | v4 the skill calls |
|---|---|
| `python3 scripts/run_review.py --prepare-only <url>` | `adk pr-task prepare <url>` (exists) |
| `python3 scripts/validate_findings.py --task-dir <dir>` | `adk pr-task validate <url>` (exists) |
| `python3 scripts/comment_resolver.py ...` | `adk pr-task resolve-comments <url>` (new) |
| `python3 scripts/triage.py --init --finalize ...` | `adk pr-task triage <url> [--init|--finalize|--mark|--default-state]` (new) |
| `python3 scripts/post_comments.py ...` | `adk pr-task post <url> [--no-post|--use-mcp|--no-slack-summary]` (new) |
| `python3 scripts/report.py ...` | `adk pr-task report <url> [--merge-if-approved]` (new) |

### 6.w Who runs the review (Phase 2) — script-name + invocation contract

This is a contract the rest of the plan relies on; it's worth nailing down explicitly because the current code is misleadingly named.

**The script that prepares the task folder does NOT review the PR.** It's mis-named today (`run_review.py`) — its actual job is Phase 0 (prereq) + Phase 1 (clone + worktree + index + supporting docs + precis). It never reads `findings.json`. It never invokes an LLM. It exits with `{"action": "prepared", ...}` before any review happens.

**P5 renames** `skills/adk-pr-review/scripts/run_review.py` → `skills/adk-pr-review/scripts/prepare_task.py`. The CLI wrapper `adk pr-task prepare` stays; only the internal file name changes. The agent invocation path (CLI verb) is unaffected.

**Phase 2 (the actual review) is run by the chosen AGENT.** The agent loads the skill (`/adk-pr-review`) which tells it to read `pr-review/precis.md` + the diff + the index, then produce `pr-review/findings.json`. No Python script does this.

**The agent is invoked as a subprocess** by whichever caller is initiating the review:

| Caller | How the agent gets invoked |
|---|---|
| Human in a terminal | User types `claude -p "/adk-pr-review <url>"` (or `codex exec`, `cursor-agent -p`, …) |
| `adk auto` (P9) | Spawns the configured agent with the same `-p "/adk-pr-review <url>"` per PR |
| `prj-adk-pr-auto` (P10) | Same, with `--verbose` always set |
| TUI (P8) | Same; the worker driver picks the configured agent and `subprocess.create`s it |

Default agent: **claude** (overridable per `core.yaml`'s `tui.default_agent` and per CLI flag).

**The skill, once loaded by the agent, runs the rest via the CLI:**

```
[caller]  spawns: claude -p "/adk-pr-review <url>"
   │
   ▼
[agent loads SKILL.md]
   │
   ▼
[Phase 0/1] Skill says: adk pr-queue claim <url>     ← lock the queue row (NEW verb, P6)
   │
   ▼
[Phase 0/1] Skill says: adk pr-task prepare <url>    ← idempotent; short-circuits if ready
   │
   ▼
[Phase 2]   Agent reads pr-review/precis.md + diff;
            writes pr-review/findings.json           ← the agent itself, no script
   │
   ▼
[Phase 3]   Skill says: adk pr-task validate <url>
   │
   ▼
[Phase 4]   Skill says: adk pr-task triage <url> --init --default-state accept --finalize
   │
   ▼
[Phase 5]   Skill says: adk pr-task post <url>       ← inline comments + Slack reply
   │
   ▼
[Phase 6]   Skill says: adk pr-task report <url>     ← report.md + queue release
            → adk pr-queue release <url> --status approved   (called by report internally)
```

**Nothing here is `python3 scripts/...`.** Every Layer-1 invocation goes through a Layer-2 CLI verb.

### 6.v Lock contract — held for the whole review

The queue row's `taken_at` field IS the long-running lock. It must be set when the review starts (Phase 0) and cleared when the review completes (Phase 6 `report.py`'s release). The current 30-minute auto-expiry is too short for long reviews.

**v4 contract:**

| Lock | Holder | Lifetime | Expiry |
|---|---|---|---|
| `taken_at` (queue row) | the review run | Phase 0 (claim) → Phase 6 (release) | Auto-expires after `taken_lock_max_age_seconds` (default raised to **2 hours** in v4) |
| `.adk-pr-lock` (file lock in task dir) | only during prep | Phase 1 only | Released when prepare exits |

**Heartbeat to avoid mid-review expiry.** During Phase 2-5, the agent periodically calls `adk pr-queue heartbeat <url>` (every 5 minutes) which bumps `taken_at` to now. If the agent crashes between heartbeats, the next sync sees a stale `taken_at` (older than `taken_lock_max_age_seconds`) and reclaims the row. Implementation: a simple "update last_heartbeat field" on the row; `_is_locked()` consults that too.

**New CLI verbs in P6:**

```bash
adk pr-queue claim <url>           # set taken_at + status=in_review atomically; fail if locked
adk pr-queue heartbeat <url>       # bump taken_at; called every ~5 min during a review
adk pr-queue release <url> [--status <s>]   # clear taken_at; optionally set terminal status (exists; rename + extend)
adk pr-queue set-status <url> <s>  # change status mid-review (e.g. "reviewed" after Phase 5)
```

The agent uses these. The skill's "Process" wraps them around Phase 2-5. The TUI's worker driver calls `claim` at start, `release` at end, and runs a heartbeat loop in a daemon thread.

### 6.u Eligibility for review (single source of truth)

A PR can ONLY be reviewed if EVERY condition is met:

1. `status` ∉ `TERMINAL_STATUSES` (`merged`, `closed`). Both adk's `closed` (GitHub closed-without-merge) and Bitbucket's `DECLINED`/`SUPERSEDED` (mapped to `closed` by `classify_pr_state`) are excluded by this single check.
2. `taken_at` is null OR `(now - taken_at) >= taken_lock_max_age_seconds`.
3. `prep_status == "ready"`.
4. `prep_head_sha == head_sha` (the prep is for the current commit; no commits arrived since).
5. `head_sha != last_reviewed_head_sha` (this commit hasn't been reviewed already). When `last_reviewed_head_sha` is null (never reviewed), this passes.

`adk pr-queue get-next` returns the next FIFO row matching ALL five. `adk pr-queue claim <url>` succeeds only if all five hold for that URL (it's the explicit-URL counterpart).

Explicit override exists: `adk pr-queue claim <url> --force` bypasses rules 1, 4, 5 (still respects 2 — never breaks an active lock). Useful for re-reviewing a merged PR for posterity. Constitution §I.3 still applies (no auto-merge).

### 6.x Verbose mode (cross-cutting)

Every CLI verb gains `--verbose` / `-v`. Off by default.

**On (`--verbose`):**
- Logging level upgraded to `DEBUG`.
- Each subprocess invocation logged with full argv, cwd, exit code, runtime.
- Each network call logged with method, URL (no headers — secret hygiene), response code, elapsed.
- Each file read/write over 1 MB logged with byte count.
- One structured log file per invocation at `~/.agents-devkit/logs/<verb>-<utc-ts>-<pid>.log`. JSON-lines so it's `jq`-able.
- Stderr also receives a human-readable summary line per major step.

**Off (default):**
- Logging level `INFO`.
- Stderr only — no log file.
- The user sees only what's actionable.

**Consumers:**
- Dev users running locally to debug ("`adk pr-sync --verbose 2>sync.log`").
- The **`prj-adk-pr-auto` skill (§ P10)** always invokes verbs with `--verbose` so it has structured logs to read when observing failures.
- The TUI optionally reads these logs for the log pane when a worker is launched in verbose mode (off by default; toggle with `v` in the TUI).

**Implementation:** new helper `skills/adk-cli/scripts/_verbose.py` exposing `setup_verbose(verb_name)` — wires the file handler + structured formatter into the existing logger. Every CLI verb calls this in `main()` if `args.verbose`.

**Secret hygiene:** the verbose formatter scrubs values of any env var matching `*_TOKEN`, `*_KEY`, `*_SECRET`, `*_CRED`, `*_PASSWORD`, `*_PAT`, `*_API_KEY` from output. Same redactor applied to subprocess argv.

### 6.y Post-review Slack notification (cross-cutting)

> <!-- updated 2026-05-21: shape + PR-identity + reaction-flip rules pulled from a live `/adk-pr-review` against `bitbucket.org/lastbrand/ecomm-ssr#5559`, posted into a thread that carried 3 PR links. Today's `format_slack_summary` in `post_comments.py` collapsed the verdict + link + bullets onto a single visual line and rendered the PR identifier only inside the Slack URL anchor text, so a reader scanning the thread couldn't tell which of the 3 PRs the bot was responding to. The shape below + §6.y.3 reaction-flip + §6.z auto-approve are the agreed responses. -->

After Phase 6 (disposition), the skill posts a reply into the queue row's Slack thread with the verdict, identity, and a bulleted summary of what the run did.

#### 6.y.1 Message shape (canonical, v4)

Three sections, each on its own line(s). The shape is fixed so a human or another agent scanning the thread can parse it without context.

```
<line 1 — verdict + 1-line TL;DR>
<line 2 — PR identity + status facts>
<line 3..n — bullet summary of what the run did>
```

**Concrete example (approve, 0 issues, 3 appreciations):**

```
✅ *Approved* — analytics-only hotfix, payload matches non-PL parity, tests cover both emit + suppress paths.
📌 `lastbrand/ecomm-ssr#5559` · status `approved` · head `f6a31aae` · author <@U097Z9CUYJF>
• Posted 3 PR-level appreciations (api · tests · observability).
• 0 inline issues.
• Approved via `approvePullRequest` (auto-approve gate, §6.z).
• 🔗 https://bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5559
```

**Concrete example (comment_only, 2 should-have + 1 question, no auto-approve):**

```
⚠ *Comments* — 2 should-have findings on input validation + 1 clarification question; nothing blocking.
📌 `acme/storefront-bff#1240` · status `comments` · head `a4f2c1be` · author <@U123ABC>
• Posted 3 inline comments + 2 appreciations.
• Resolved 1 prior thread the diff addressed; left 2 ambiguous threads open.
• Did not auto-approve — issues identified (§6.z).
• 🔗 https://github.com/acme/storefront-bff/pull/1240
```

**Verdict emojis (line 1, leading character):** ✅ approve · ⚠ comments · 🚫 request_changes · 🔒 merged (skipped review).

**Why this shape:**

1. **Line 1 is a glanceable verdict.** The leading emoji + bold word lets a scroller categorise the message in one fixation.
2. **Line 2 carries the PR identifier outside the URL anchor.** Slack threads frequently carry multiple PR links (today's run hit a thread with 3). A reader can't tell from `<https://…|ecomm-ssr#5559>` which PR the bot replied about if their client hides URL chrome, so the identifier appears as plain `lastbrand/ecomm-ssr#5559` backticked text — search-friendly + copyable. Status, head sha (12 chars), and author mention are factual + short.
3. **Bullets describe what the run did, not what's wrong.** A reader who needs more clicks through to the PR; the Slack reply is the index, not the report.
4. **The URL is the last bullet, prefixed `🔗`.** Stays out of the way of the human-readable lines but remains one click away.

**Hard rules:**
- Line 1 ≤ 100 chars (Slack truncates around 110-120 in thread previews).
- The PR identifier on line 2 is always `<workspace-or-owner>/<repo>#<n>` in backticks, never folded into a URL anchor — so multi-PR threads stay disambiguated.
- Bullets are short (≤ 80 chars each). 4-6 bullets max.
- Always include the URL bullet, even when the workspace name appears on line 2.

#### 6.y.2 Author-to-Slack mapping

GitHub `author.login` (already captured in `pr.json` + queue row) maps to a Slack user ID via:

```yaml
# core.yaml
user_mappings:
  github_to_slack:
    sujeet-pro: U123ABC
    other-user: U456DEF
```

When the mapping is missing, the message uses plain text (`@sujeet-pro`) instead of `<@U123ABC>` — still readable, no broken mention. Bitbucket users use a parallel `bitbucket_to_slack` block keyed on the Bitbucket `nickname`.

#### 6.y.3 Reaction flip on the source message

The Slack message that originally carried the PR link (the one `adk pr-scan` indexed into the queue row) gets a reaction matching the final status. Today's pipeline sets a `change requested` reaction at queue time and **does not flip it back** when the review finishes — so a thread with only appreciations on the PR ends up with a misleading "change requested" indicator.

**v4 rule:** after Phase 6 disposition, `post_comments.py` flips the reaction on `slack.message_ts` (NOT `slack.thread_ts` — see queue schema §4) to match the final canonical status:

| Final status | Reaction emoji (default; configurable per `connectors/slack.md` frontmatter) |
|---|---|
| `approved` | ✅ `:white_check_mark:` |
| `comments` | 💬 `:speech_balloon:` |
| `reviewed` (request_changes) | 🚫 `:no_entry:` |
| `merged` | 🟣 `:large_purple_circle:` |
| `closed` | ⚪ `:white_circle:` |
| `error` | ⚠ `:warning:` |

**Idempotency:** the helper reads existing reactions first; removes any prior adk-managed emoji from the table above; then adds the new one. Never strips reactions added by humans. The set of "adk-managed" emojis is the values column above + any emojis the connector frontmatter declares.

**When the flip fires:** every time the final disposition is computed, including re-runs at the same head_sha. (Reactions are idempotent — re-applying the same emoji is a no-op.)

#### 6.y.4 When the notification fires

- The queue row has Slack metadata (`channel_id` + `message_ts` + `thread_ts`) — otherwise no thread to reply in; the run still produces `report.md` and posts inline comments.
- `--no-slack-summary` flag suppresses the reply but **not** the reaction flip in §6.y.3. (The reaction is status hygiene; the reply is the summary.) Add `--no-slack-reaction` for full silence.
- `--merge-if-approved` + approve: the MERGEABLE line goes into the Slack reply as an additional bullet, so the author sees it inline. Merge itself never happens (constitution §I.3).

#### 6.y.5 Implementation

- New function `post_review_slack_reply(...)` in `slack_helpers.py` renders §6.y.1 and posts via `mcp__adk-mcp-slack__conversations_add_message`.
- New function `flip_slack_reaction(...)` in `slack_helpers.py` runs the §6.y.3 idempotent remove-then-add.
- Both are called by `post_comments.py` after the inline-comment posting completes. Plumbed through `adk pr-task post`.
- `post-result.json` records `slack_reply_ts` + `slack_reaction_after` so a re-run is a no-op (matches the existing risk-row safety in §13).

### 6.z Auto-approve gate

> <!-- added 2026-05-21: today's run on `ecomm-ssr#5559` produced 0 issues + 3 appreciations; the pipeline returned `recommendation: comment_only` and skipped the host approval because the 3 appreciations the bot itself posted created "open threads", which the prior gate counted as a reason to withhold approval. The reviewer then approved manually. That manual step is a tell — the gate is too conservative. The rule below is the agreed v4 behaviour. -->

**Rule:** `/adk-pr-review` calls the host approve API when **no identified issue exists**, regardless of comment count, appreciation count, or open-thread state. An "identified issue" means a finding with severity in `{blocker, critical, should-have}`.

Concretely, set `posting-plan.json.approve_ready = true` iff **all** of:

1. `findings[]` contains zero entries with `severity ∈ {blocker, critical, should-have}`.
2. `existing_comment_actions[]` contains zero entries with `decision == "reopen"` whose reopen reason references a fresh finding (i.e., the reopen is the bot's call, not an offline-alignment passthrough).
3. The PR is in a non-terminal `state` (not `MERGED` / `CLOSED` / `DECLINED`).
4. The current user has approve permission on the PR (probed at posting time; on fail, downgrade to `comment_only` and add a bullet to the Slack summary explaining why).

**Findings of severity `may-have` / `nitpick` / `question` / `appreciation` do NOT block approval.** The reasoning:

- **may-have / nitpick**: by definition deferrable. If the reviewer thought they were blocking, they would have raised them at `should-have`+.
- **question**: a question is the bot saying "I don't have enough context" — that's not a defect in the code. The author can answer in the thread without the PR being held.
- **appreciation**: positive feedback. Counting it as "an open thread" was the bug today.

**Approve action:**

- GitHub: bundled with the review summary post — `pull_request_review_write` with `event: APPROVE`.
- Bitbucket: separate `approvePullRequest` MCP call after the review summary.

The Slack reply (§6.y) reflects the approve in the verdict line + a bullet ("Approved via `approvePullRequest`"). The reaction (§6.y.3) flips to `:white_check_mark:`.

**Constitution §I.3 is untouched.** Approve ≠ merge. The skill approves; the human (author, another reviewer, or CODEOWNERS) clicks merge.

**Override flags:**

- `--no-approve` — force `approve_ready=false` even when the gate passes. For runs where the reviewer wants to leave the verdict for a human (e.g. `adk auto` on a sensitive repo).
- `--require-human-approval=<pattern>` (core.yaml `pr_review.require_human_approval` list of repo patterns) — same effect, persistent. Useful for compliance-tagged repos.

**Test plan:**

| Scenario | findings | existing-actions | expected | reaction |
|---|---|---|---|---|
| Trivial green PR | 0 of any | 0 | approve | ✅ |
| Appreciation-only | 0 issues + 3 appreciations | 0 | approve | ✅ |
| 1 should-have | 1 should-have | 0 | comments | 💬 |
| 1 question only | 0 issues + 1 question | 0 | approve | ✅ |
| 1 nitpick only | 0 issues + 1 nitpick | 0 | approve | ✅ |
| Bot reopens prior thread | 0 issues | 1 reopen by bot | comments | 💬 |
| Offline-aligned reopen passthrough | 0 issues | 1 reopen w/ `offline_alignment_detected: true` | approve | ✅ |
| `--no-approve` set | 0 issues | 0 | comments | 💬 |
| User lacks approve perm | 0 issues | 0 | comments + bullet | 💬 |

---

## 7. Fully automated reviews (`adk auto`)

### 7.1 Why

For scheduled / unattended runs: cron, launchd, GitHub Action. Same pipeline as a human-driven session, no `-i`, deterministic exit codes, single aggregated report.

### 7.2 Surface

```
adk auto [--max-reviews N] [--max-cost-usd X] [--quiet-hours 00-08]
         [--platform github] [--repo owner/name]* [--exclude <pr-url>]*
         [--parallel N] [--report-to-slack #channel] [--dry-run]
         [--agent claude|codex|cursor|opencode]
```

### 7.3 What it does

1. `adk pr-sync` — runs the full DAG (Phase A→F including auto-base creation + cleanup).
2. For each PR with `ready_for_review` true (up to `--max-reviews`, default 20):
   - Spawn the agent: `<agent> -p "/adk-pr-review <url>"`.
   - Auto-mode: the skill runs Phase 2-6 without `-i`.
   - Posts inline comments + Slack summary per existing policy (constitution §I.4).
3. Final `adk pr-queue clean` to drop rows that became terminal during the run.
4. Write `~/.agents-devkit/skill-setup/auto-runs/<ts>/report.md` aggregating per-PR recaps.
5. If `--report-to-slack` set: one summary post to that channel ("Auto-review: 8 PRs reviewed · 4 approved · 2 needs-changes · 2 comment-only · run time 12m18s").

### 7.4 Safety

- **Constitution §I.3 absolute** — `adk auto` never merges. `--merge-if-approved` still only prints the MERGEABLE line.
- `--quiet-hours WW-XX` (local clock) — refuse to spawn during the window. Useful so a scheduled job doesn't ping people overnight.
- `--max-cost-usd` — multiply `cost_per_review * ready_pr_count`; if > limit, abort with rc=2 and emit the predicted bill.
- `--exclude <pr-url>*` — skip specific PRs (regression safety).
- `--dry-run` — show what would happen; no agent spawned.
- Idempotency: `last_reviewed_head_sha == head_sha` filter already skips already-reviewed PRs.

### 7.5 Scheduling

`SETUP.md` ships an example launchd plist that fires `adk auto --max-reviews 10 --report-to-slack #pr-reviews --quiet-hours 00-08` every 2h.

---

## 8. Phase plan

Each phase ships independently. Every phase starts with the §2 read gate. Phases are ordered by dependency; the agentic team for each is in §7.

### P1 · GitHub-first migration (≈2 engineer-days)

**Goal:** Rename `declined` → `closed`, `head_oid` → `head_sha`, `pr_link` → `pr_url`; default to GitHub; document `gh` CLI fallback.

**Touched files:** `queue_io.py`, `queue_release.py`, `pr_scan.py`, `pr_queue.py`, `pr_task.py`, `pr_sync.py`, `pr_reminders.py`, `run_review.py`, `report.py`, `post_comments.py`, `comment_resolver.py`, all SKILL.mds, README.md, every test.
<!-- updated 2026-05-21: P1 read-gate added: scripts/lib/code_index/base_index.py + README.md (indexer's head_oid), skills/adk-pr-review/scripts/{_common.py, fetch_pr.py, create_worktree.py, validate_findings.py, triage.py}, skills/adk-pr-review/references/{indexing.md, workflow.md}, skills/adk-cli/SKILL.md, completion.py, bin/adk USAGE — all carry legacy terms and must be in P1's scope. Detail in docs/plans/deltas/P1-delta-2026-05-21.md. -->

**Migration:** In-place rewrite of `pr-queue.json5` rows + decision logs + every `state.json` under `pr-reviews/`. Aliases (`STATUS_DECLINED = STATUS_CLOSED`, `head_oid = head_sha` as deprecated property) live for one release.
<!-- updated 2026-05-21: P1 read-gate refined: migration is implemented as an idempotent read-shim in queue_io.read_queue() (and analogous shim in state.json readers), not a one-shot rewrite. The shim renames pr_link→pr_url, head_oid→head_sha, last_reviewed_head_oid→last_reviewed_head_sha, "declined"→"closed" on every read and writes the normalised form back on next save. This makes the migration self-healing on first use under P1 code, so the user's live Bitbucket-shaped queue survives without P7. -->

**Exit:** `adk pr-queue add 1234` works against `defaults.repo`. All tests green. No legacy term in user-visible strings.
<!-- updated 2026-05-21: P1 read-gate noted that `defaults.platform` + `defaults.repo` are NEW keys in core.yaml (not present today). P1 adds them + extends pr_queue.cmd_add to accept a bare PR number that resolves against defaults.repo. The other shorthand forms (acme/foo#1234, two-arg, explicit) land in P6 per §8 P6. -->
<!-- updated 2026-05-21: P1 read-gate noted that `last_reviewed_head_oid` must also be renamed to `last_reviewed_head_sha` (transitively, as a consequence of head_oid→head_sha). -->


### P2 · `skill-*` filesystem prefix (≈1 day)

**Goal:** Rename per-skill working dirs. Drop empty `memory/`.

Renames (handled by install migration step):
- `pr-reviews/` → `skill-pr-review/`
- `investigations/` → `skill-investigate/`
- `reviews/` → `skill-review/`
- `sync/` → `skill-sync/`
- `setup/` → `skill-setup/`
- `improve/` → `skill-improve/`
- `explain/` → `skill-explain/`
- (new) `skill-document/`, `skill-implement/` created lazily on first use
- `memory/` removed if empty

**Touched files:** `_common.py` constants in every skill, `shared/paths.md`, every CLI module's task-root constant, `scripts/adk_task_slug.py`.

**Exit:** All skill working dirs under `skill-<name>/`; old paths return ENOENT after migration.

### P3 · Repo layout overhaul (≈3 days)

**Goal:** Symmetric repo + PR-task shape; `original-clone/` as the worktree source; `branch-<NAME>/` per tracked branch.

The current state already has `branches/<slug>/code-index/`; this phase deepens the layout (clone separation + `branch-<NAME>` naming + `branch-meta.json` consolidation).

**New verbs (most already partially in-tree):**
```
adk repo add <url> [--branch X]*
adk repo update <name> [--branch X | --all-branches | --all] [--rebuild]
adk repo branch add <name> --branch X
adk repo branch remove <name> --branch X
adk repo branch list <name>
adk repo rebuild-index <name> [--branch X]   ← NEW (for "folder got deleted" cases)
adk repo migrate [<name>]                    ← already in-tree; finish it
```

**Migration:** Walk every `~/.agents-devkit/repos/<name>/`. For each, detect layout state (legacy v3 / mid-transition / v4) and apply the minimal moves to reach v4. Idempotent.

**Exit:** Every repo has `repo-meta.json`, `original-clone/`, `branch-<DEFAULT>/`. Every branch dir has `code/`, `code-index/`, `branch-meta.json`. `adk repo rebuild-index` works when a folder was deleted by hand.

### P4 · PR task folder restructure (≈1.5 days)

**Goal:** Move PR-review-specific files into a `pr-review/` subfolder of each task dir. PR task dir now has the same shape as a branch dir + one subfolder.

**Add helper:** `pr_review_dir(task_dir)` in `_common.py` returns `task_dir / "pr-review"` (creating if needed). Every script that reads/writes `pr.json`, `findings.json`, etc. goes through it.

**Migration:** For each `skill-pr-review/<repo>_pr-<n>/`, `mkdir pr-review/` and `mv` the well-known files in.

**Exit:** No PR-review-specific file lives at the top of the task dir. All scripts updated.

### P5 · Dependency-aware sync DAG + auto-base lifecycle (≈4 days)

**Goal:** Implement §5 in full — the 3-tier sync algorithm, `prep_status` lifecycle, `ready_for_review` predicate, AND the auto-base creation + cleanup policy (§5.4).

**Touched files:** `pr_sync.py` (new helpers, removed `_audit_base_indexes`), `queue_io.py` (new fields + predicate), `pr_task.py` (prep records `prep_*` on completion), `pr_queue.py` (`get-next` consults `prep_status`), `repo.py` (`branch add --auto`, `auto-bases list|clean`), `scripts/lib/code_index/base_index.py` (`created_by` + `auto_reason` + `last_used_at` in branch-meta), tests. **Also: rename `skills/adk-pr-review/scripts/run_review.py` → `prepare_task.py`** (the script is prep-only; the misleading name was confusing).

**New helpers in pr_sync.py:**
- `_build_sync_plan(queue_path, embed_model, log) -> SyncPlan` — Phase B (classifies groups; picks auto-base candidates).
- `_build_bases(plan, jobs, embed_model, log)` — Phase C (user refreshes + auto-creates).
- `_prepare_tier(prs, jobs, log, on_progress, tier)` — Phase D (tier-0, tier-1, or tier-2).
- `_clean_auto_bases(log)` — Phase F.
- `_write_plan(plan)` — persists to `~/.agents-devkit/tui/workers/sync-plan.json` for the TUI.

**Queue schema additions:** `prep_status`, `prep_started_at`, `prep_completed_at`, `prep_head_sha`, `prep_used_base` (now includes `{repo, branch, created_by}`), `prep_error`.

**`branch-meta.json` additions:** `created_by` (`"user"` | `"auto"`), `created_at`, `auto_reason`, `last_used_at`.

**`repo.py` additions:** `cmd_branch_add --auto`, `cmd_auto_bases_list`, `cmd_auto_bases_clean`.

**Migration:** Existing rows get `prep_status="pending"` if their task dir doesn't have a fresh index, `prep_status="ready"` if it does. Existing branch-meta files get `created_by: "user"` (everything in-tree today was user-driven).

**Exit:** `pr-sync` follows the 3-tier DAG; the TUI plan file accurately reflects tiers + auto-vs-user origin. `adk pr-queue get-next` only returns rows where `ready_for_review` is true. `adk repo auto-bases list|clean` works. Auto-base TTL cleanup runs at the tail of every sync.

### P6 · CLI completeness + skill rewiring + verbose + Slack reply (≈4 days)

**Goal A — close the CLI surface so the skill (and TUI) make CLI calls only.** Add wrapper verbs for every script the skill currently invokes directly. After P6, `SKILL.md` "Process" lists only `adk pr-task <verb>` calls.

**Goal B — skill defaults.** `/adk-investigate`, `/adk-implement`, `/adk-document`, `/adk-review` consume `repos/<repo>/branch-<DEFAULT>/code-index/` by default. `--branch` overrides. Each SKILL.md gets a "Default code source" section.

**Goal C — convenience input forms.** GitHub-shorthand for adding PRs.

**Goal D — verbose mode.** Every CLI verb accepts `--verbose / -v` (§6.x). New helper `_verbose.py`.

**Goal E — post-review Slack reply + reaction flip + auto-approve.** `adk pr-task post` posts the 3-section summary into the queue row's Slack thread (§6.y.1), flips the reaction on the source message to match final status (§6.y.3), and calls the host approve API when the §6.z gate passes. New helpers `post_review_slack_reply` + `flip_slack_reaction` in `slack_helpers.py`. New config: `user_mappings.github_to_slack`, `user_mappings.bitbucket_to_slack`, `pr_review.require_human_approval` in `core.yaml`. New flags: `--no-slack-reaction`, `--no-approve`.

**New CLI verbs:**

```bash
# Phase-2-wrapper verbs (the skill stops calling python3 scripts/... directly):
adk pr-task triage <url> [--init|--finalize|--mark <id> <decision>|--default-state]
adk pr-task post <url> [--no-post|--use-mcp|--no-slack-summary]
adk pr-task report <url> [--merge-if-approved]
adk pr-task resolve-comments <url>

# Lock-handling verbs (§6.v — held for the whole review duration):
adk pr-queue claim <url> [--force]             # set taken_at + status=in_review; fail if locked
adk pr-queue heartbeat <url>                   # bump taken_at to now; called ~every 5 min during review
adk pr-queue release <url> [--status <s>]      # clear taken_at; optionally set terminal status
adk pr-queue set-status <url> <status>         # mid-review status transitions (e.g. → "reviewed")

# Auto-base verbs (drive §5.4 lifecycle from the CLI):
adk repo auto-bases list
adk repo auto-bases clean [--dry-run] [-y]
adk repo auto-bases clean --force <repo> --branch X   # force-clean one

# Add-PR-by-number:
adk pr-queue add 1234                          # default repo from core.yaml
adk pr-queue add acme/foo#1234                 # GitHub shorthand
adk pr-queue add owner/repo 1234               # two-arg form
adk pr-queue add --repo owner/name --pr 1234   # explicit form

# Verbose flag — accepted by every verb above (and existing ones):
adk pr-sync --verbose
adk pr-task prepare <url> -v
...
```

**Lock-lifetime raise:** `taken_lock_max_age_seconds` increased from 30 min to **2 hours** (default), configurable in `core.yaml`. Heartbeats every 5 min keep an active review's lock fresh; a 2h ceiling lets a crashed reviewer be reclaimed automatically without breaking long agent runs.

**Skill updates:** `SKILL.md` (`adk-pr-review`) replaces every `python3 scripts/...` line with `adk pr-task ...`. Other skills get `--branch X` plumbed through to wherever they consult the index.

**Exit:** SKILL.md `grep -c "python3 scripts"` returns 0. Every non-PR-review skill respects `--branch`. The four add-by-number forms work. `adk pr-sync --verbose 2>/dev/null` writes a structured log file with secret values redacted. `adk pr-task post <url>` posts a 3-section Slack reply (§6.y.1) tagging the author (or plain-text login if no mapping), flips the source-message reaction to match final status (§6.y.3), and calls the host approve API when §6.z passes. The §6.z test table goes green in CI.

### P7 · Install / migration — preserve every index (≈2 days, runs alongside P1-P4)

**Goal:** `./install.sh` (or `./install.sh --migrate`) detects the live layout and brings it to v4 idempotently. **MOVE, never delete.** Existing queue rows, prepared task folders, and branch indices all survive the migration intact. Re-indexing every PR would burn hours of CPU; the migration cannot inflict that.

**Preservation contract (the rule):**
- The PR queue (`pr-queue.json5`) is rewritten in place with the new field names; no row is dropped.
- Every existing `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/` task folder is MOVED to `~/.agents-devkit/skill-pr-review/<repo>_pr-<n>/`, with its `code/`, `code-index/`, `scip/`, `docs/` subfolders untouched (only PR-specific files relocate into `pr-review/`).
- Every existing branch index under `~/.agents-devkit/repos/<name>/...` is MOVED to its v4 location (`branch-<NAME>/code-index/`). `branch-meta.json` gets `created_by: "user"` (everything in-tree today was user-driven).
- Anything *outside* the preservation set (e.g. orphaned task folders without a queue row, stale `memory/`, decision-log archives) may be cleaned up — but only after the preservation set is safely in v4 layout.

**Flow:**
```
./install.sh
  ├── existing wiring (symlinks, MCP merges, hooks)
  └── migrate (default ON when v3 layout detected)
      ├── P1: terminology + queue field rename                (in-place, atomic)
      ├── P2: skill- prefix rename                            (mv old → new; no data lost)
      ├── P3: repo layout                                     (mv clone → original-clone/;
      │       mv indices → branch-<NAME>/; preserves every chunk + LanceDB table)
      ├── P4: pr-review/ subfolder                            (mv PR-specific files in;
      │       code/, code-index/, scip/, docs/ untouched)
      ├── P5: backfill prep_status on existing rows           (read state.json; set
      │       prep_status=ready iff code-index/meta.json exists + head_sha matches)
      └── cleanup (last) — orphan task folders, empty memory/  (after preservation
                                                                verified)
```

Each step writes to `~/.agents-devkit/.migration-staging/<phase>/` first using **hardlinks where possible** (instant, free, no data duplication on the same filesystem); only renames into place on success of the WHOLE batch. On failure, staging is preserved + report explains what to fix. `./install.sh --rollback-migration <timestamp>` reverts.

**Migration report:** `~/.agents-devkit/skill-setup/migrations/<ts>.md` listing every transformation, byte counts moved, references in user-authored markdown that need a manual edit, AND an "**indices preserved: N task folders, M branch indices, 0 re-indexed**" line so the user sees that no work was lost.

**Verification:** post-migration, the install runs a quick sanity check — for each preserved task folder, confirm `code-index/meta.json` exists, has a valid embed model, and `chunks.lance/` is readable. If any index fails verification, surface in the report; do not silently re-index.

**Exit:** Fresh install lands in v4 directly. Existing v3 install migrates once, idempotent on re-run. Failure mode preserves data. Verification confirms every prepared index survived.

### P8 · TUI (≈12 days, broken into sub-phases α-λ — see §10)

**Goal:** Interactive Textual app launched by `adk` (no args). Surfaces the full DAG live (including auto-base tier labels), lets the user run parallel reviews, manages repos + branches (including auto-base visibility + manual cleanup).

Detail in §10.

### P9 · Fully automated review mode (`adk auto`) (≈1.5 days)

**Goal:** Implement §7 — the headless verb that runs the full pipeline (sync + parallel reviews + Slack roll-up). Scheduler-friendly.

**Touched files:**
- New `skills/adk-cli/scripts/auto_run.py` (the orchestrator).
- `bin/adk` dispatch (`if cmd == "auto": ...`).
- `completion.py` (new top-level verb).
- `bin/adk` USAGE block.
- New tests under `tests/test_auto_run.py`.

**Logic:**
1. Run `adk pr-sync` (which does the §5 DAG + auto-base cleanup).
2. Enumerate rows passing the §6.u eligibility predicate, sort FIFO, cap at `--max-reviews`.
3. Apply guards: `--quiet-hours`, `--max-cost-usd`, `--exclude`, `--dry-run`.
4. Spawn parallel **agent subprocesses** up to `--parallel N`. The invocation is `<agent_binary> -p "/adk-pr-review <pr_url>"` — e.g. `claude -p "/adk-pr-review https://github.com/acme/foo/pull/42"`. The agent loads the skill, which makes its own `adk pr-task ...` calls (Phase 2-6). `auto_run.py` never imports `prepare_task.py` directly; it just spawns the agent.
5. Per child: stream stdout to `~/.agents-devkit/skill-setup/auto-runs/<ts>/<repo>_pr-<n>.log`; on exit, capture the final recap from `pr-review/report.md`.
6. Aggregate to `report.md`.
7. If `--report-to-slack` set: post the summary via the Slack helper.

**Safety:** Constitution §I.3 absolute (no merge). Constitution §I.4 satisfied because PR review is task-required (auto-post allowed).

**Exit:** `adk auto --dry-run` prints what it would do. `adk auto` runs end-to-end with no input. Exit-code 0 (success) / 1 (some reviews failed) / 2 (aborted by guard, e.g. quiet hours).

### P10 · `prj-adk-pr-auto` — iterative auto-improve skill (≈3 days)

**Goal:** A project-level Claude skill that runs `adk auto` at growing batch sizes (1 → 4 → all), observes failures, proposes + applies code fixes, and repeats until clean. Lives in **`<repo>/.claude/skills/prj-adk-pr-auto/`** (Claude-Code-specific; not portable; project-bound). User invokes `/prj-adk-pr-auto`; the skill resumes from persisted state.

**Why a project-level skill (not a `~/.claude/skills/` user-level one):**
- It targets THIS adk codebase's failure modes; not portable.
- It uses Claude-Code-specific features (the `Agent` tool for parallel investigation, `Bash` for running tests).
- It persists learning state inside the repo so it survives `git pull` and team members can see what's been tried.

**Directory layout:**
```
<repo>/.claude/skills/prj-adk-pr-auto/
  SKILL.md                            # main contract: process + invariants
  scripts/
    observe.py                        # parse ~/.agents-devkit/logs/ + auto-run reports
                                      # extract failure categories (prep_failed, agent_crashed,
                                      # post_failed, slack_failed, ...) with line refs
    propose_fix.py                    # given a failure category + log excerpt, draft a fix patch
                                      # using recipes from prompts/fix-recipes/
    run_iteration.py                  # one full cycle: spawn `adk auto --verbose`, capture
                                      # logs, analyze, return summary
    state.py                          # read/write state.json (iteration counter, etc.)
  prompts/
    fix-recipes/
      prep-failed-no-base.md          # recipe: when prep fails because base isn't fresh
      agent-timeout.md                # recipe: when the agent subprocess times out
      post-rate-limited.md            # recipe: when GitHub MCP returns 429
      ...
  state.json                          # iteration, max_reviews, consecutive_clean,
                                      # failures_seen, fixes_applied
```

**Iteration logic (in SKILL.md "Process"):**

1. Read `state.json`. Defaults: `iteration=1`, `max_reviews=1`, `consecutive_clean=0`.
2. Run `adk auto --max-reviews {state.max_reviews} --verbose --report-to-slack <configured-channel>`.
3. `observe.py` ingests the verbose logs + auto-run report. Categorizes outcomes:
   - **succeeded** — review ran clean, comments posted, recap fine.
   - **succeeded_with_warnings** — finished but verbose log shows recoverable warnings.
   - **failed** — review crashed, post failed, prep failed, etc.
4. **If failures > 0:**
   - For each failure category, call `propose_fix.py` with the failure context.
   - `propose_fix.py` consults `prompts/fix-recipes/<category>.md` for a known recipe; if none, escalates to an `Agent` subagent (Sonnet/Opus) to investigate root cause + propose a patch.
   - Apply the patch via `Edit` calls.
   - Run the affected tests (`pytest skills/adk-*/scripts/tests/`).
   - If tests pass: commit the fix (locally — never push), add entry to `state.fixes_applied`.
   - If tests fail: revert, escalate to the user in the next-steps section.
5. **If no failures and no warnings:** `consecutive_clean += 1`.
6. **Promotion thresholds:**
   - `consecutive_clean >= 3` AND `max_reviews == 1` → set `max_reviews = 4`, reset `consecutive_clean = 0`.
   - `consecutive_clean >= 3` AND `max_reviews == 4` → set `max_reviews = 20` (or `unlimited` from config), reset.
   - `consecutive_clean >= 3` AND `max_reviews == 20` → done; surface success report; suggest stopping.
7. Persist `state.json`. Print summary to the user.

**Invariants the skill respects:**

- **No `git push` ever.** Fixes are committed locally for inspection; the user pushes.
- **No `git merge` / branch deletion** without confirmation.
- **All `adk` CLI calls go through `--verbose`** so logs are inspectable on the next iteration.
- **Constitution §VII (no secret values in chat)** — `propose_fix.py` greps fix proposals for credential patterns and refuses to apply any patch that surfaces a secret.
- **Idempotent re-runs.** Running `/prj-adk-pr-auto` twice without code changes between runs is safe — state.json keeps the iteration counter monotonic.
- **Human-readable state.** `state.json` is a few hundred bytes max; a human can diff it across runs.

**User invocation:**

```bash
$ claude
> /prj-adk-pr-auto                # resume from state.json
> /prj-adk-pr-auto --reset        # start over (max_reviews=1, consecutive_clean=0)
> /prj-adk-pr-auto --stop-at 4    # don't promote past max_reviews=4
> /prj-adk-pr-auto --dry-run      # show what would happen; no adk auto spawn
```

**Build order:** P10 ships AFTER P9 (it depends on `adk auto`) and AFTER P6 (it depends on `--verbose`). It does NOT depend on P8 (TUI); the loop runs entirely in the terminal via the skill.

**Exit:** `/prj-adk-pr-auto` invoked on a fresh checkout runs through at least one full iteration without error. State persists. After enough iterations, the loop reaches `max_reviews=20` with 3 consecutive clean runs.

---

## 9. Agentic-team execution model

Each phase is implemented by a team of agents working in parallel where the work decomposes cleanly. The standard team shape:

```
                  ┌──────────────────────┐
                  │   Lead agent         │  Sonnet/Opus. Runs §2 read gate. Splits work.
                  │   (orchestrator)     │  Owns the final PR. Drives integration.
                  └─────┬──────┬────┬────┘
                        ↓      ↓    ↓
            ┌───────────┴┐ ┌───┴──┐ ┌┴────────┐
            │  Worker A  │ │  B   │ │  C  …   │   Haiku/Sonnet — focused edits.
            │  (file X)  │ │ (Y)  │ │ (tests) │   Outputs: a diff against base.
            └────────────┘ └──────┘ └─────────┘
                        ↓      ↓    ↓
                  ┌──────────────────────┐
                  │   Reviewer agent     │  Sonnet. Reads diffs, runs tests,
                  │   (validator)        │  greps for legacy terms, blocks on
                  └──────────┬───────────┘  rule violations.
                             ↓
                       human approval → merge
```

**Rules of engagement:**

- **One owner per file per phase.** Workers don't collide on the same file; the lead splits work along file boundaries.
- **Workers can't merge.** They produce diffs (or commits on isolated branches); the lead integrates.
- **Reviewer runs the test suite + the constitution checks** (§I.3 no auto-merge, §I.4 posting policy, §VII no secrets). It can block.
- **Read gate is the lead's job, once per phase.** Workers consume the lead's "scope brief" (file list + change recipe + invariants to preserve).
- **Time-box workers** at 30 minutes of wall-clock. If a worker doesn't converge, lead reassigns or simplifies the brief.
- **Every commit cites the phase + worker role** in the message: `P5/B: add _build_sync_plan helper`.

**Phase-by-phase team breakdown:**

| Phase | Lead | Parallel workers (one per row) | Reviewer |
|---|---|---|---|
| P1 GitHub-first | Sonnet | A: rename status enum + classifier · B: rename `head_oid` field + callers · C: rename `pr_link` field · D: terminology in SKILL.mds + README · E: migration script · F: tests | Sonnet |
| P2 skill- prefix | Sonnet | A: `_common.py` constants · B: `pr_*` modules · C: `_common.py` constants in other skill scripts · D: `shared/paths.md` + `scripts/adk_task_slug.py` · E: migration script · F: tests | Sonnet |
| P3 repo layout | Opus | A: `repo.py` core (original-clone/, branch-<NAME>/) · B: `branch-meta.json` schema + base_index.py updates · C: `cmd_rebuild_index` · D: migration script · E: `ensure_repo_clone.py` + `create_worktree.py` updates · F: tests | Sonnet |
| P4 pr-review/ subfolder | Sonnet | A: `_common.py` helper + prepare_task.py reads/writes (the prepare script, renamed in P5) · B: validate_findings.py + triage.py · C: post_comments.py + report.py · D: comment_resolver.py + queue_release.py · E: migration script · F: tests + SKILL.md artifact list | Sonnet |
| P5 sync DAG | Opus | A: queue_io.py schema + `ready_for_review` predicate · B: `_build_sync_plan` + `_build_bases` · C: `_prepare_tier` + `prep_status` writes from pr_task.py · D: `get-next` filters · E: tests · F: plan.json schema doc | Sonnet |
| P6 skill rewiring | Sonnet | A: SKILL.mds default-source paragraph · B: skill argparse `--branch` · C: `adk pr-queue add` forms · D: completion · E: tests · F: README | Sonnet |
| P7 install/migration | Opus | A: staging + rollback infrastructure · B: detection logic · C: per-phase migrators (compose existing migration scripts from P1-P5) · D: migration report writer · E: tests · F: `--rollback-migration` flag | Sonnet |
| P8α-λ TUI | Sonnet (per sub-phase) | A: Textual widgets · B: worker driver · C: agent registry · D: tests · E: heartbeat protocol | Sonnet |

**For long-running phases** (P3, P5, P8), the lead may split a sub-phase into a second team round if a worker's brief gets too large.

**Concurrency budget:** up to 4 parallel worker agents per phase by default. P8 sub-phases each get their own small team (typically 2-3 workers).

**Cross-phase serialization:** the lead of phase N+1 waits for the reviewer-approved PR of phase N to be merged into `main` before spawning workers. No parallel work across phases that touch the same files (e.g. P1 and P2 both touch `pr_queue.py` so they serialize).

---

## 10. TUI (Phase P8 in detail)

### 8.1 Scope

v1 of the TUI handles **PR reviews only** end-to-end. Architecture (§8.5) is built so other skills can slot in later as additional task types.

### 8.2 What the TUI gives you

You type `adk`. A multi-pane app opens. You can:

- **Browse** the unified queue list with per-row prep + review state icons.
- **Add a PR** by repo + number (modal that hands off to `adk pr-queue add owner/repo#N`).
- **Manage repos + branches** — add a repo (with default branch + extras), add/remove tracked branches, rebuild an index whose folder was deleted.
- **Sync** the queue (`s` runs `adk pr-sync`; the TUI tails Phase A→E in real time and updates each row's `prep_status` as it changes).
- **Watch the DAG**: a per-row indicator shows `pending → preparing (Tier-1 from base) → ready`. Failed preps show the error inline.
- **Select PRs** for review — single (`enter`) or multi-select (`space` toggles; selection order shown as `[1] [2] [3]`).
- **Review** — `r` for highlighted, `R` for all selected in order, `n` for next eligible. Configure parallelism (default 4).
- **See externally-launched workers** — `adk pr-sync` or `/adk-pr-review` running in another terminal surfaces as a read-only worker row via heartbeat files.
- **Switch agent** via `a` (default = whoever's installed first).
- **Read the recap** when each worker exits.

Interactive triage (`-i`) is **never** invoked from the TUI. External `-i` processes show as `WAITING — input expected in terminal X (PID Y)`.

### 8.3 Per-row state icons (one unified list)

```
🌱  queued — just added, no metadata yet
🔍  fetching metadata
⏳  waiting for base index (target_branch's base is building)
⚙   preparing (this PR's task folder being built)
✓   ready for review                   ← Review button enabled
⚙↻  reviewing (a worker is on it now)
📝  reviewed (post-review, awaiting merge)
✅  approved
🚫  blocked / request_changes
🔒  merged / closed
⚠   prep failed (hover shows error)
⏰  stale review (24h+, no new commits, reminder eligible)
```

A row's state is the join of `prep_status`, `taken_at`, `status`, `last_reviewed_*`.

### 8.4 Layout

```
┌─ adk · platform: github · queue: 12 · ready: 8 · reviewing: 2/4 · agent: claude ──┐
│┌─ Queue ──────────────────────────┐┌─ Details (#1240) ─────────────────────────┐│
││ [1]✓  #1234  acme/storefront-bff ││ acme/storefront-bff#1240                   ││
││ [2]⏳ #1235  acme/storefront-bff ││ Title: feat: coupon engine                 ││
││     ⚙  #1236  acme/checkout-fe   ││ Author: sujeet  ·  +312 −44 / 12 files     ││
││     ⚙↻ #1240  acme/storefront-bff (worker A) ││ Branch: feat/coupon → main      ││
││     ⚙↻ #1233  acme/checkout-fe   (worker B) ││ head_sha: a4f2c1...             ││
││ [3]✓  #1242  acme/checkout-fe    ││ prep: ready (seeded from acme/foo:main)    ││
││     ✅ #1238  acme/storefront-bff││ Slack: #eng-prs (1 thread)                 ││
││     🔒 #1232  acme/storefront-bff││ Last reviewed: 1d ago at b7d8e2 (stale)    ││
│└──────────────────────────────────┘└────────────────────────────────────────────┘│
│Filter: [open ▾]   Sort: [age ▾]   Parallel: [4 ▾]   Selected: 3 (run order: 1,2,3)│
│┌─ Workers ───────────────────────────────────────────────────────────────────────┐│
││ A · #1240 · review phase 5 · posting comments       · 04:12 · claude            ││
││ B · #1233 · review phase 2 · reading precis         · 01:38 · claude            ││
││ ⚐ ext · #1251 · prep tier-1 · embedder 70%          · another terminal · claude ││
││ C · idle                                                                          ││
│└──────────────────────────────────────────────────────────────────────────────────┘│
│┌─ Sync plan (last sync 09:14:22 — ✓ done) ──────────────────────────────────────┐│
││ Base indexes: ✓ acme/storefront-bff:main · ✓ acme/checkout-fe:main · ✓ 2/2     ││
││ Tier-1 prep:  ✓ 6/6 (all seeded from base)                                      ││
││ Tier-2 prep:  ✓ 0/0                                                              ││
│└──────────────────────────────────────────────────────────────────────────────────┘│
│┌─ Log (worker A · #1240) ────────────────────────────────────────────────────────┐│
││ 09:12:14 [phase 5] posting 4 comments via mcp__adk-mcp-github__...              ││
││ ▌                                                                                  ││
│└──────────────────────────────────────────────────────────────────────────────────┘│
├──────────────────────────────────────────────────────────────────────────────────┤
│ [s] sync  [n] next  [r] selected  [R] run all  [+] add PR  [b] repos             │
│ [k] kill  [a] agent  [space] toggle  [f] filter  [?] help  [q] quit              │
└──────────────────────────────────────────────────────────────────────────────────┘
```

The "Sync plan" pane is read from `~/.agents-devkit/tui/workers/sync-plan.json` (written by `pr-sync` in Phases B/C/D). It updates as bases land and tiers complete.

### 8.5 Architecture

```
                ┌─────────────────────────────────────────────┐
                │  adk TUI process  (Textual app)             │
                │  ┌───────────────┐  ┌────────────────────┐  │
                │  │ Skill registry│  │ Queue + plan model │  │
                │  │ (pr-review +  │  │ (polls queue +     │  │
                │  │  extensible)  │  │  sync-plan.json)   │  │
                │  └───────────────┘  └─────────┬──────────┘  │
                │  ┌───────────────┐            │             │
                │  │ Worker pool   │  ┌─────────▼──────────┐  │
                │  │ (parallel     │  │ Phase / log watcher│  │
                │  │  Popens +     │  │ per worker         │  │
                │  │  asyncio)     │  │ (state.json +      │  │
                │  └───────────────┘  │  stdout)           │  │
                │                     └────────────────────┘  │
                └────────────────┬────────────────────────────┘
                                 │ spawns
                ┌────────────────┴────────────────────────────┐
                │  Worker children (one per review):           │
                │   1. adk pr-queue claim <url>                 │  (CLI, holds lock for entire review)
                │   2. adk pr-task prepare <url>                │  (CLI, short-circuits if already prepared)
                │   3. spawn agent: claude -p "/adk-pr-review <url>"  (agent runs phases 2-6)
                │   4. heartbeat loop: adk pr-queue heartbeat <url>   (every 5 min, daemon)
                │   5. on exit: skill already called `adk pr-task report` which released the lock
                │  TUI worker file: ~/.agents-devkit/tui/workers/<pid>.json (heartbeat + state)
                └─────────────────────────────────────────────┘
```

**Worker driver** (`skills/adk-cli/scripts/tui/worker.py`):
- Calls `adk pr-queue claim <url>` first — fails fast if the row is locked.
- Calls `adk pr-queue heartbeat <url>` every ~5 minutes in a daemon thread to keep the lock fresh; stops on the agent's exit.
- Spawns the configured agent via the agent registry: the registry's `launch(slash_cmd, args)` returns the argv (`["claude", "-p", "/adk-pr-review <url>"]` by default; per-agent overrides).
- Writes the TUI heartbeat JSON every 5s (pid, pr_url, task type, agent, current_phase, started_at, last_heartbeat) to `~/.agents-devkit/tui/workers/<pid>.json`.
- Streams agent stdout/stderr to `~/.agents-devkit/tui/logs/<id>.log` AND to its parent (the TUI tails both).
- Traps SIGTERM: kills the agent child, calls `adk pr-queue release <url>` to clear the lock, exits 130.

**Key invariant: the worker driver never imports `prepare_task.py` or any Layer-3 module directly.** It only calls `adk <verb>` and spawns the agent binary. This is what makes the worker driver swappable across agent backends and resilient to internal refactors.

**Sub-phases (build order, each preceded by §2 read gate):**

| α | Foundation: launch Textual app, 4-pane skeleton, footer, `q` exits | 1d |
| β | Read-only queue view + filter + sort + detail pane | 1d |
| γ | Run sync from TUI (live-stream Phases A-E into log + sync-plan pane) | 1.5d |
| δ | Worker pool + single-PR run (`r`, `n`) — review-only (prep already done by pr-sync) | 2d |
| ε | Phase-aware progress bars + ETA from `state.json` polling | 1d |
| ζ | Multi-select + ordered batch run (`R`, `Parallel: N ▾`) | 1.5d |
| η | Add-PR modal + repo management screen (add repo, add/remove branches, rebuild, auto-base visibility + manual cleanup) | 2d |
| θ | External-process monitoring via heartbeat files | 1d |
| ι | End-of-run recap modal | 0.5d |
| κ | Agent picker + headless fallback | 0.5d |
| λ | Polish (themes, help, reattach-on-restart, detach prompt) | 1d |

**TUI total: ≈12 engineer-days.**

### 8.6 The "Review" button only enables when prep is done

Per row, the TUI computes `ready_for_review` (§4 / §5.3). The Review action (`r`, `R`, `n`) is greyed out when no selected row is ready. A row that's in `prep_status="preparing"` shows `⏳` and a progress percent inline; the user can wait or pre-select it (multi-select queues it for review the moment it becomes ready).

This is the **one-list UX**: there's no separate "queue to prepare" and "queue to review" view. The same list shows everything; the icon tells you what's happening; the button enables when the row's prereqs are met.

### 8.7 Repo management screen — auto-vs-user origin

Press `b` to switch to the repo view. Each tracked branch is tagged with its origin and (for auto bases) a TTL countdown:

```
┌─ Repos ────────────────────────────────────────────────────────────────────┐
│ acme/storefront-bff                                                         │
│   ├── main           (user · indexed 2h ago)                                │
│   ├── release/v2.1   (auto · shared by 3 PRs · 14h old)   ⚠ clean in 10h    │
│   └── feat/sso       (auto · 0 PRs · cleanup eligible)    [delete now]      │
│                                                                              │
│ acme/checkout-fe                                                            │
│   └── main           (user · INDEX MISSING)               [rebuild]          │
│                                                                              │
│ [+ Add repo]   [+ Add branch]   [⌫ Clean all eligible auto-bases]           │
└──────────────────────────────────────────────────────────────────────────────┘
```

Actions:
- `[+ Add repo]` opens a modal: URL + initial extra branches; the default branch is always added and indexed.
- `[+ Add branch]` lets you promote any tracked branch from `auto` → `user` (extends its life past the TTL) or add a brand-new tracked branch.
- `[delete now]` for an auto base with 0 active users runs `adk repo auto-bases clean --force <repo> --branch X`.
- `[rebuild]` (when `INDEX MISSING`) runs `adk repo rebuild-index <repo> --branch X`.
- `[⌫ Clean all eligible auto-bases]` runs `adk repo auto-bases clean`.

### 8.8 Extensibility (carried forward)

`SkillSpec` registry: a future skill adds one entry. The worker pool, agent dispatch, log pane, and heartbeat protocol are all generic. v1 hard-codes `skill: pr-review` in the header but routes through the registry, so the seam is visible.

---

## 11. Per-skill checklist

| Skill | P1 | P2 | P3 | P4 | P5 | P6 | P10 | P8 |
|---|---|---|---|---|---|---|---|---|
| `/adk-pr-review` | terminology + GitHub-first | skill-pr-review/ | original-clone/ worktrees | pr-review/ subfolder | prep_status writes | wrapper verbs + verbose + Slack-reply | observed by P10 | first-class in TUI |
| `/adk-implement` | terminology | n/a | reads branch-<DEFAULT>/code-index/ | n/a | n/a | `--branch` + `--verbose` | n/a | TUI v2 |
| `/adk-investigate` | terminology | skill-investigate/ | reads branch-<DEFAULT>/code-index/ | n/a | n/a | `--branch` + `--verbose` | n/a | TUI v2 |
| `/adk-document` | terminology | n/a (repo-bound writes) | reads branch-<DEFAULT>/code-index/ | n/a | n/a | `--branch` + `--verbose` | n/a | TUI v2 |
| `/adk-review` | terminology | skill-review/ | optional `--use-index` | n/a | n/a | `--branch` + `--verbose` | n/a | n/a |
| `/adk-sync` | terminology | skill-sync/ | n/a | n/a | n/a | `--verbose` | n/a | n/a |
| `/adk-setup` | terminology | skill-setup/ | knows v4 layout for `--check` | n/a | n/a | `--verbose` | n/a | n/a |
| `/adk-improve` | terminology | skill-improve/ | n/a | n/a | n/a | `--verbose` | n/a | n/a |
| `/adk-explain` | terminology | skill-explain/ | n/a | n/a | n/a | n/a | n/a | n/a |
| `/prj-adk-pr-auto` (NEW) | n/a | n/a | n/a | n/a | n/a | depends on every verb supporting `--verbose` | **the skill itself** | observed by external-worker tile in TUI |

---

## 12. Build order

**Skills + CLI first; TUI last.** The user's directive: get the auto-improve loop working via the skill + CLI before adding any TUI on top. Once `/prj-adk-pr-auto` runs cleanly at unlimited scale, the TUI is a richer view of the same machinery — but the machinery has already been hardened.

```
Week 1: P1 (GitHub-first) ‖ P2 (skill- prefix) ‖ P7-scaffold (migration framework)
Week 2: P3 (repo layout) ‖ P4 (pr-review/ subfolder)
Week 3: P5 (sync DAG + auto-base lifecycle) [highest-value]
Week 3-4: P6 (CLI completeness + skill rewiring + verbose + Slack reply)
Week 5: P9 (adk auto)                          ← scheduler-friendly headless mode
Week 5-6: P10 (prj-adk-pr-auto skill)          ← iterative auto-improve loop
Week 7-9: P8 (TUI sub-phases α-λ)              ← TUI last, after the substrate is hardened
P7 accumulates step coverage as P1-P5 land.
```

Cross-phase serialization (phase ID dependencies):
- P3 → P2 (needs `repos/` shape stable).
- P4 → P2 (skill-pr-review/ root).
- P5 → P3, P4 (`pick_base_index` looks up branch-<NAME>/; writes prep state under pr-review/).
- P6 → P3, P4 (`--branch` flag references branch dirs; wrapper verbs read from pr-review/).
- P9 → P5, P6 (drives the DAG; calls the new wrapper verbs).
- **P10 → P9, P6** (loops on `adk auto`; always uses `--verbose`).
- P8 → P5, P4, **P10** (TUI surfaces what the skill drives; benefits from `prj-adk-pr-auto` having flushed edge cases).

Total estimate: **≈32 engineer-days** (sequential). Agentic-team parallelism within each phase compresses calendar time by ~30-40%. P10 typically pays for itself by reducing the rework P8 would otherwise need.

---

## 13. Risks & open questions

| Risk | Mitigation |
|---|---|
| Migration corrupts existing data | Staging + rollback in P7. Run on a test install first. |
| Active reviews mid-migration | Migration refuses if any `taken_at` is fresh (< 30 min). User runs `adk pr-queue release` to override. |
| Multi-branch indexing balloons disk | Default = only default branch. Extras via `adk repo branch add`. Soft cap suggestion in `adk doctor`. |
| `gh` unauthenticated + MCP unreachable | `adk doctor` checks both; surfaces clearly. |
| Heartbeat files orphaned | Stale (> 60s no update) → "lost contact"; user can force-clear. |
| External worker (non-TUI launch) doesn't write a heartbeat to `tui/workers/` | The agent (claude/codex/cursor) won't know to write one. Solution: when the skill calls `adk pr-queue claim <url>`, the claim verb writes the TUI heartbeat file too (best-effort). External CLI runs (e.g. a script calling `adk pr-task prepare`) also get a heartbeat from the verb. The TUI sees external work without any cooperation from the agent process itself. |
| Agent stdout buffering breaks live tail | Set `PYTHONUNBUFFERED=1` + `-u` in worker driver. For agents we don't control, fall back to `state.json` polling. |
| Sync DAG starves Tier-2 if Tier-0/1 are huge | All three tiers share the prepare_jobs pool; Tier-2 always gets at least one worker slot via reserved capacity. |
| `prep_status="preparing"` orphaned by a crash | On `pr-sync` start, mark any `preparing` row >30 min stale as `pending` and re-process. |
| Agentic-team workers collide on the same file | Lead splits work along file boundaries; the rule "one owner per file per phase" prevents this. |
| Auto-base created mid-sync, then user adds a new PR targeting it before cleanup | The cleanup step re-reads the queue immediately before deletion; any non-terminal user blocks removal. |
| Auto-base TTL too short — base deleted then immediately needed | Default 24h; tune via `pr_sync.auto_base_ttl_hours`. The next sync re-creates it if needed (≥ threshold PRs). |
| User-promoted auto-base shouldn't be auto-cleaned | TUI's "promote to user" action flips `created_by: "user"`; cleanup never touches user-tagged. |
| `adk auto` runs while a human is also reviewing in another terminal | Each agent invocation goes through `pr-queue get-next` which claims `taken_at`. The other terminal's get-next sees the claim. No double-review. |
| `adk auto --quiet-hours` clock drift | Use system local clock; no NTP-sensitive math. Document that DST transitions may skip / extend the window by an hour twice a year. |
| `adk auto` cost overrun | `--max-cost-usd` is a pre-flight estimate (per-agent multiplier × N reviews). Conservative; doesn't account for retries. Document. |
| TUI users wonder why `adk pr-sync` is slow now | Phase B + Phase C add up-front work that pays off in Phase D. Show the breakdown in `sync-plan.json` so users see "saved 4m vs full-from-scratch". |
| Migration accidentally re-indexes everything | Preservation contract in P7: MOVE, never delete. Verification step asserts each preserved `code-index/meta.json` is readable. Migration report shows "0 re-indexed" line. |
| Verbose logs leak secrets | §6.x secret-redactor scrubs values of env vars matching `*_TOKEN`/`*_KEY`/`*_SECRET`/`*_CRED`/etc. Constitution §VII enforced. |
| Verbose log files balloon disk | One file per CLI invocation; rotated at 100 MB or pruned after 7 days by an `adk doctor` check. |
| `prj-adk-pr-auto` proposes an unsafe fix | `propose_fix.py` greps the patch for credential patterns; refuses to apply if any match. All fixes go through local commit (never push); the user inspects before pushing. |
| `prj-adk-pr-auto` loops forever | `consecutive_clean >= 3` termination at the top level; per-iteration time-box (default 30 min); `--max-iterations N` flag for paranoia. |
| `prj-adk-pr-auto` state file lost | Re-deriveable: read recent `~/.agents-devkit/skill-setup/auto-runs/<ts>/report.md` to reconstruct. `--reset` flag for fresh start. |
| Slack-author mention broken (no mapping) | Falls back to plain text `@<github-login>`. No broken `<@U…>` literal. Document mapping in SETUP.md. |
| `adk pr-task post` Slack reply fires twice on a re-run | `post-result.json` records `slack_reply_ts` after first post; subsequent runs see it set and skip the reply. |
| Reaction flip (§6.y.3) clobbers a human-added emoji | Helper only removes emojis listed in the adk-managed set (the values column of §6.y.3 + any declared in `connectors/slack.md` frontmatter). Anything else (👍, 🚀, custom team emojis) is preserved. |
| Multi-PR thread reaction goes on the wrong message | `slack.message_ts` is the message that carried the PR link (set by `adk pr-scan` per §4); `slack.thread_ts` is the thread root. Reaction targets `message_ts`. When a thread has 3 PR links across 2 messages, each PR's row points at the message that contained ITS link, so reactions don't cross-pollinate. |
| Auto-approve (§6.z) approves a PR the user expected to land manually | `--no-approve` flag + `pr_review.require_human_approval` repo-pattern list in `core.yaml`. Approve action is always reflected in the Slack reply so the human sees it inline and can revoke. Constitution §I.3 (never merge) is unchanged — approve ≠ merge. |
| Auto-approve permission check fails (reviewer is not authorized on the repo) | Probed at posting time; on permission denial, downgrade to `comment_only`, add a bullet to the Slack reply ("Could not auto-approve — user lacks approve permission"), and exit without re-trying. |
| Lock expires mid-review and another reviewer grabs the PR | `taken_lock_max_age_seconds` raised to 2h in v4; heartbeats every 5 min keep an active review fresh. If the heartbeat dies, the 2h ceiling lets a crashed reviewer be reclaimed — but only after a clear window. |
| User reads `run_review.py` in stack traces / logs and concludes it ran the review | Renamed to `prepare_task.py` in P5. Log lines that say `[pr-task-prepare] $ run_review.py …` become `[pr-task-prepare] $ prepare_task.py …`, which is honest. |
| Agent invocation is hard-coded to claude somewhere | All agent spawns go through the agent registry (§G.6 / §8.5); claude is the *default*, not the only choice. Audit P9 + P10 + TUI worker for any literal `["claude", ...]` and replace with `registry.launch(...)`. |

**Open questions to decide before P1 starts:**

1. **Bitbucket sunset date.** If Bitbucket fully drops in N months, the secondary code paths can be aggressively simplified. Plan keeps them intact.
2. **Branch limit per repo.** Default-only + N user-added + M auto? Soft cap?
3. **`defaults.repo` location** — `core.yaml` `defaults:` (current plan) or `repos.md` frontmatter?
4. **`get-next` strictness.** Hard-refuse non-ready rows, or soft `--force` to claim a not-yet-prepared PR?
5. **`prep_status` reset window.** 30 min seems right for orphan recovery; revisit after dogfooding.
6. **Auto-base threshold = 2 or 3?** Threshold-2 maximizes index-reuse but adds disk noise for branches with only 2 fleeting PRs. Default 2; consider raising after telemetry.
7. **`adk auto` default `--max-reviews`?** 20 feels safe. Adjust based on cost telemetry once we have it.
8. **Per-agent cost estimates** for `--max-cost-usd`. Where do they come from? Hard-code per-agent in `auto_run.py` for v1; defer a proper telemetry pipe.

---

## 14. Out of scope (v4)

- Linux-first parity (macOS remains primary; Linux best-effort).
- GitLab / Bitbucket Server.
- Diff viewer inside the TUI.
- Findings editor inside the TUI (use the PR UI).
- Merge button in the TUI (constitution §I.3).
- Cross-repo dependency graph view.
- Auth flows for MCP servers (per `SETUP.md`).
- v3 ← v4 rollback long-term (within-release rollback only).
- Multi-skill TUI switcher UI (architecture supports it; ships in v2).

---

## 15. Recommended next step

1. Read this plan top to bottom; flag anything surprising.
2. Run §2 (the read gate) for **P1** and write the delta note.
3. Spawn the P1 agentic team per §9. Land P1 + P2 in week 1.
4. Then P3 alone (highest-risk migration); land it. **Verify P7 migration on a real install before P3 ships** — losing existing indices would be the most painful regression.
5. Then P4 + P5 (P5 is the highest-value piece — sync DAG + auto-base lifecycle).
6. P6 alongside P5 (independent file scope) — `--verbose` and Slack-reply land here too.
7. **P9 (`adk auto`), then P10 (`prj-adk-pr-auto` skill).** Run `/prj-adk-pr-auto` against the real machine; let it converge at `max_reviews=1`, then `4`, then unlimited.
8. **P8 (TUI) LAST.** After P10 has shaken out the substrate's edge cases. The TUI is a richer view of a system that already works.
9. P7 (install/migration) keeps shipping deltas across the whole timeline.

If anything in §13 (open questions) needs a different default, decide before P1.
