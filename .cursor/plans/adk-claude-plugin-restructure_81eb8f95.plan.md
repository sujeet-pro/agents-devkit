---
name: adk-claude-plugin-restructure
overview: "Convert the entire `agents-devkit` repo into a single Claude plugin named `adk` (with `.claude-plugin/plugin.json` at root, skills under `skills/<name>/` without `adk-` prefix). Preserve install paths via `npx skills` + a local symlink installer that mirrors a parallel `agents-skills/adk-<name>/` tree for other agents. Migrate all 39 existing skills (renamed, contracts kept, references rewritten), then add ~25 new skills covering the developer end-to-end loop (auto-router, setup, requirements, scoping, context-gather, .temp-folder, doc-site, datadog, mixpanel, cicd, plus separate fix/review modes per skill). Honor the rule: do not touch `docs/` or `gh-pages/`."
todos:
  - id: phase0-clone-current
    content: "Phase 0: Re-read the CURRENT repo end-to-end (every existing skill SKILL.md, references/, agents-claude/*, hooks/*, mcp-config/*, cli/*, global-prompts/*, workflows/*) and write a current-state inventory to .temp/plans/restructure-current-state.md"
    status: completed
  - id: phase0-clone-refs
    content: "Phase 0: Clone or refresh ALL reference repos in .temp/reference-repos/: agent-os, design-os, anthropic-skills, cursor-skills (any others currently referenced by the repo). Deep-read each and write per-repo findings to .temp/plans/restructure-references-<repo>.md"
    status: completed
  - id: phase0-local-pkgs
    content: "Phase 0: Inventory local ~/personal/pagesmith and ~/personal/diagramkit skills (their SKILL.md contracts + how they expect to be wrapped) and write to .temp/plans/restructure-local-deps.md"
    status: completed
  - id: phase0-catalog
    content: "Phase 0: Lock the final skill catalog (skills to migrate, rename, split, drop, add) and dependency graph in .temp/plans/restructure-architecture.md"
    status: completed
  - id: phase1-scaffold
    content: "Phase 1: Scaffold the new repo layout - .claude-plugin/plugin.json, empty skills/, agents/, hooks/hooks.json, .mcp.json, bin/, agents-skills/, monitors/, settings.json, marketplace.json. NO shared/ dir - interaction-contract is inlined per skill (see Architecture section)"
    status: completed
  - id: phase1-canonical
    content: "Phase 1: Create bin/canonical/interaction-contract.md (single source of truth) and bin/adk-sync-contracts script that propagates byte-identical copies into every skill's references/interaction-contract.md"
    status: completed
  - id: phase1-package
    content: "Phase 1: Update package.json (drop CLI bin, keep skills entries for npx skills), README, AGENTS.md, CLAUDE.md, GEMINI.md to describe the repo-as-plugin model"
    status: completed
  - id: phase2-meta-skills
    content: "Phase 2: Author the 4 meta skills (auto, setup, temp-folder, mode-contract) with full SKILL.md + references/ including how-it-works.md mermaid diagrams"
    status: completed
  - id: phase3-migrate-existing
    content: "Phase 3: Migrate all 39 existing adk-* skills - rename folders to drop adk-, rewrite SKILL.md frontmatter, update cross-references to dual form (@adk:name + adk-name), keep interaction-contract.md INLINE in each skill (synced via bin/adk-sync-contracts, not symlinked)"
    status: completed
  - id: phase3-add-required-refs
    content: "Phase 3: Add references/how-it-works.md (with mermaid decision diagram) and references/modes.md to every migrated skill"
    status: completed
  - id: phase3-symlinks
    content: "Phase 3: Create agents-skills/adk-<name>/ symlinks pointing to skills/<name>/ for npx skills + non-Claude agents (folder-level symlinks, not file-level, so interaction-contract.md travels with the skill)"
    status: completed
  - id: phase4-context
    content: "Phase 4: Author new discovery skills - context-gather (Jira/Confluence/Slack/GDocs/Gmail link follower), requirements (iterative), scoping"
    status: completed
  - id: phase4-frontend
    content: "Phase 4: Author frontend-mockup (5-sample HTML preview generator) and enhance frontend-design to call into it during plan mode"
    status: completed
  - id: phase4-build-review
    content: "Phase 4: Author build-bugfix (split from build-feature), review-doc (with supporting-doc context), and add fix-mode to review-pr / review-local / audit-repo"
    status: completed
  - id: phase4-doc-site
    content: "Phase 4: Author doc-site-setup (wraps ~/personal/pagesmith skills) and doc-site-diagrams (wraps ~/personal/diagramkit), referencing local installed packages"
    status: completed
  - id: phase4-observability
    content: "Phase 4: Author observability-datadog, analytics-mixpanel, observability-incident skills - MCP-driven with REST fallback"
    status: completed
  - id: phase4-cicd
    content: "Phase 4: Author cicd-monitor (gh run watch on current PR) and cicd-fix (parse failed-job logs, propose + apply fix)"
    status: completed
  - id: phase4-browser-validate
    content: "Phase 4: Author validate-browser skill - drives a browser via cursor-ide-browser MCP (or playwright fallback) to verify UI changes / bug fixes / preview HTMLs. Modes: verify-fix, visual-check, console-audit, interaction-test, a11y-audit. Outputs screenshots + console + network logs to .temp/task-<slug>/browser-validation/"
    status: completed
  - id: phase4-misc
    content: "Phase 4: Author audit-pr, plan-proposal (split from brainstorm), personal-skill-create"
    status: completed
  - id: phase4-publish-rewrite
    content: "Phase 4: Rewrite publish-github + publish-commit to use gh CLI exclusively (drop MCP fallback per user note 13)"
    status: completed
  - id: phase4-wire-browser-validate
    content: "Phase 4: Wire validate-browser into the auto-skill orchestration flow as Phase D2 (post-build, post-fix) - mandatory whenever the change touched any frontend skill or produced .temp/task-<slug>/preview/*.html. Update frontend-feature, frontend-mockup, build-bugfix, review-pr (fix-mode), audit-site to call validate-browser as their final validation step"
    status: completed
  - id: phase5-agents
    content: "Phase 5: Write subagent files in agents/ - Claude format only (drop agents-cursor/, agents-codex/), one per role: brainstorm-facilitator, implementer, code-reviewer, debugger, test-engineer, doc-writer, plan-reviewer, research-agent, security-reviewer + new dispatcher agent for auto-skill orchestration"
    status: completed
  - id: phase6-bin
    content: "Phase 6: Author bin/adk-install (symlink installer for non-Claude agents), bin/adk-mcp-install (.mcp.json + ~/.zshenv -> claude mcp add), bin/adk-setup (Homebrew + CLI tools, macOS only), bin/adk-doctor (validate everything)"
    status: completed
  - id: phase7-validator
    content: "Phase 7: Rewrite cli/lib/validate.mjs as bin/adk-validate enforcing: SKILL.md present, frontmatter name matches folder, dual-form cross-refs, required reference files present (how-it-works.md, validator.md, modes.md, interaction-contract.md symlink), agents-skills symlinks intact"
    status: completed
  - id: phase7-manifest
    content: "Phase 7: Regenerate skills-manifest.json from new structure (still emitted for npx skills) and run validator"
    status: completed
  - id: phase8-cleanup
    content: "Phase 8: Remove obsolete files - agents-cursor/, agents-codex/, cli/ (except generate-skill-docs.mjs + validate-content.mjs moved to bin/), mcp-config/, global-prompts/, workflows/, hooks/cursor.json, hooks/codex.json"
    status: completed
  - id: phase8-finalcheck
    content: "Phase 8: Final pass - run validator, verify docs/ and gh-pages/ untouched, write summary to .temp/reports/restructure-summary.md"
    status: completed
isProject: false
---

# ADK Claude Plugin Restructure

## 1. End-state architecture

The whole repo is the `adk` Claude plugin. Skills inside `skills/` use bare names (e.g., `plan-brainstorm`); Claude invokes them as `/adk:plan-brainstorm`. A parallel `agents-skills/adk-<name>/` tree of symlinks exposes the same content under `adk-` prefixed names for `npx skills` and non-Claude agents (Cursor, Codex, Gemini, Antigravity).

```
agents-devkit/                            # === THIS REPO IS THE adk PLUGIN ===
├── .claude-plugin/
│   ├── plugin.json                       # name: "adk"
│   └── marketplace.json                  # for distribution
├── skills/                               # ~55 skills, NO adk- prefix
│   ├── auto/                             # NEW: prompt-routing meta-skill
│   ├── setup/                            # NEW: deps + MCP + CLI bootstrap
│   ├── temp-folder/                      # NEW: .temp/task-<slug>/ enforcer
│   ├── plan-brainstorm/                  # MIGRATED from adk-plan-brainstorm
│   │   ├── SKILL.md                      #   frontmatter name: plan-brainstorm
│   │   └── references/
│   │       ├── how-it-works.md           # NEW required: decision-flow diagrams
│   │       ├── modes.md                  # NEW required: fix | review | auto
│   │       ├── persona.md, workflow.md, clarifying-questions.md, output-format.md,
│   │       ├── artifact-format.md, validator.md, anti-patterns.md, examples.md
│   │       └── interaction-contract.md   # PHYSICAL COPY (not symlink) — synced from bin/canonical/
│   └── ... (all other skills, see catalog below)
├── agents/                               # collapsed from 3 dirs to one
│   ├── brainstorm-facilitator.md
│   ├── implementer.md, code-reviewer.md, debugger.md, test-engineer.md,
│   ├── doc-writer.md, plan-reviewer.md, research-agent.md, security-reviewer.md
│   └── (Claude-only frontmatter — Cursor/Codex variants dropped per user note 1)
├── commands/                             # OPTIONAL flat slash-commands (lighter than skills)
├── hooks/
│   └── hooks.json                        # canonical Claude plugin hook config
├── .mcp.json                             # plugin-bundled MCP servers (template)
├── .lsp.json                             # OMITTED unless we have LSPs to ship
├── monitors/monitors.json                # background watchers (e.g., gh PR status)
├── settings.json                         # plugin defaults
├── bin/                                  # in PATH when plugin enabled
│   ├── canonical/
│   │   └── interaction-contract.md       # SINGLE SOURCE OF TRUTH (not shipped to skills folders directly)
│   ├── adk-install                       # local symlink installer for non-Claude agents
│   ├── adk-mcp-install                   # reads .mcp.json + ~/.zshenv → claude mcp add
│   ├── adk-setup                         # brew installs + cli configs (macOS only)
│   ├── adk-sync-contracts                # propagates bin/canonical/* into every skill's references/ (run by validator)
│   ├── adk-validate                      # validator (incl. drift check on interaction-contract copies)
│   └── adk-doctor                        # validates everything is wired
├── agents-skills/                        # NEW: parallel tree for non-Claude agents
│   └── adk-<name>                        # FOLDER-LEVEL symlink → ../../skills/<name>
│                                         #   so references/interaction-contract.md travels along
├── package.json                          # keeps `npx skills` compatibility
├── README.md, CONTRIBUTING.md, LICENSE
├── AGENTS.md, CLAUDE.md, GEMINI.md       # repo-as-plugin author guidance
├── .temp/                                # untracked working artifacts
└── docs/, gh-pages/                      # UNTOUCHED per user
```

Reference for the plugin layout: [Claude plugins](https://docs.claude.com/en/docs/claude-code/plugins) and [plugins reference](https://docs.claude.com/en/docs/claude-code/plugins-reference) (`.claude-plugin/plugin.json`, root-level `skills/`, `agents/`, `hooks/`, `.mcp.json`, `bin/`, etc.).

### Skill folder rules

Per Claude plugins reference, when `skills` field in `plugin.json` points to a directory whose `SKILL.md` files set frontmatter `name`, that name is used for invocation regardless of the directory basename. We rely on this so the source-of-truth folder name (`plan-brainstorm/`) is what humans see; the invocation `/adk:plan-brainstorm` is enforced by frontmatter.

Each skill's `SKILL.md` cross-references other skills using BOTH forms on first mention so the same file works in Claude (`@adk:plan-brainstorm`) and in plain-agent contexts (`adk-plan-brainstorm`):

```
Hand off to @adk:plan-spec (a.k.a. `adk-plan-spec`).
```

A skill may only depend on:

1. Files inside its own `references/` (every skill is fully self-contained; no symlinks out of the skill folder)
2. Other skills (referenced by name, both forms)
3. Subagents in `agents/<name>.md` (referenced by name)

No relative paths into another skill folder. The single piece of boilerplate that must be byte-identical across every skill — `references/interaction-contract.md` — is a **physical copy in every skill folder**, kept in sync by `bin/adk-sync-contracts` from the canonical source at `bin/canonical/interaction-contract.md`. The validator (`bin/adk-validate`) FAILS if any copy drifts. This makes every skill folder portable to any install path: Claude plugin install, `npx skills add`, folder-level symlink to `~/.cursor/skills/`, or copy-pasted into a project.

### Why no `shared/` directory

Considered and rejected. The `shared/interaction-contract.md → symlink` model only resolves for the Claude plugin install (where the whole plugin tree lands on disk). It breaks for: `npx skills add` (copies skill folders only), `bin/adk-install` symlinking individual skill folders into `~/.cursor/skills/`, and any "copy this skill folder into another repo" workflow. The inline-copy + propagation script model preserves portability and matches what the existing repo already does (`global-prompts/interaction-contract.md` propagated into every skill).

## 2. Skill catalog (target ~55 skills)

Migrated and renamed from existing 39 (drop `adk-` prefix), plus new skills. **Bold = new skill.** *Italic = restructured/split from existing.*

### Layer 0 — Meta / orchestration

- `**auto`** — Reads the prompt, expands it, picks initial skill set, runs brainstorm subagent for scope, then dispatches per-task subagents loaded with specific skills.
- `**setup`** — Verifies & installs deps (Homebrew on macOS), CLI tools (gh, jq, fd, ripgrep, fzf, claude), MCP servers, env vars from `~/.zshenv`. Idempotent.
- `**temp-folder**` — Enforces `.temp/task-<slug>/{plan.md, spec.md, design.md, requirements.md, scope.md, preview/*.html, validation.md}` layout. Every other skill writes through this contract.
- `**mode-contract**` — Documents the universal `--mode fix | review | auto` switch every applicable skill must support. (Reference-only skill, model-invocation disabled.)

### Layer 1 — Discovery & context

- `**context-gather**` — Follows links in a prompt/PR/doc to Jira / Confluence / Google Docs / Slack / Gmail (via MCP), pulls relevant snippets, summarizes, dedupes, attaches to current `.temp/task-<slug>/context.md`.
- `*plan-research`* (migrated) — Web + repo research with Verified / Inferred / Open buckets.
- `**requirements*`* — Iterative requirement-gathering session (brainstorm-style continuous Q&A) → `requirements.md`.
- `**scoping**` — After requirements, decides in/out of scope, blast radius, success criteria, milestones → `scope.md`.

### Layer 2 — Plan / spec / design

- `*plan-brainstorm`* (migrated)
- `*plan-spec`* (migrated)
- *`plan-design`* (migrated)
- *`plan-roadmap`* (migrated)
- *`plan-proposal`* (NEW, split from existing brainstorm) — formal proposal artifact for stakeholder review.

### Layer 3 — Frontend & UI

- *`frontend-design`* (migrated, **enhanced**) — During plan mode, generates 5 UI sample variants (HTML mockups in `.temp/task-<slug>/preview/sample-{1..5}.html`) before code.
- *`frontend-feature`* (migrated)
- *`frontend-react-csr`* (migrated)
- `**frontend-mockup`** — Standalone UI mockup generator (5-sample preview), reusable from any other skill.

### Layer 4 — Build (code-changing)

- *`build-feature`*, *`build-refactor`*, *`build-migrate`*, *`build-test`*, *`build-deps`* (all migrated)
- `**build-bugfix`** — Split out from `build-feature` (root-cause + minimal patch flow).

### Layer 5 — Review

- *`review-pr`* (migrated; **fix mode** added — auto-applies its own findings)
- *`review-local`* (migrated; fix mode added)
- *`review-feedback`* (migrated)
- *`review-handoff`* (migrated)
- `**review-doc`** — Migrated/renamed from `adk-docs-review`; supports passing supporting docs (Confluence, Google Doc, Slack channel, Gmail thread) for added context. Modes: review (post comments) | fix (apply edits).
- `**validate-browser*`* — Drives a real browser via the `cursor-ide-browser` MCP server (or playwright fallback) to validate any UI work end-to-end. Run automatically by `frontend-feature`, `frontend-mockup`, `build-bugfix` (when the bug is UI-affecting), `review-pr --mode fix` (when changes touch frontend), and `audit-site`. Modes:
  - `verify-fix` — Reproduce the original bug repro steps; assert the fix holds (no console errors of the prior signature, expected DOM state present, screenshot diff against pre-fix baseline).
  - `visual-check` — Capture viewport screenshots at 360 / 768 / 1280 widths; diff against approved baseline in `.temp/task-<slug>/browser-validation/baseline/`.
  - `console-audit` — Navigate target URLs; collect all console errors / warnings / network failures into a severity-tiered report.
  - `interaction-test` — Walk through user-defined interaction scripts (click, type, hover); assert state transitions and accessibility (focus, aria, keyboard).
  - `a11y-audit` — Run an axe-core scan per page; report violations with WCAG references.
  - All output (screenshots, console logs, network HAR, axe results) lands under `.temp/task-<slug>/browser-validation/<mode>/`. Non-zero exit fails the parent skill's validator phase.

### Layer 6 — Docs

- `*docs-write`* (migrated)
- `**doc-site-setup*`* — Replaces `adk-doc-site-setup`; wraps the LOCAL `~/personal/pagesmith` skills (`pagesmith-docs-setup`, `pagesmith-docs-add-page`, `pagesmith-docs-configure-nav`, `pagesmith-docs-customize-theme`, `pagesmith-docs-add-search`, `pagesmith-docs-deploy-gh-pages`, `pagesmith-generate-docs`).
- `**doc-site-diagrams**` — Wraps the LOCAL `~/personal/diagramkit` (mermaid / graphviz / drawio / excalidraw rendering).
- `*visualize-diagram`* (migrated)
- `*visualize-chart`* (migrated)

### Layer 7 — Audit

- *`audit-repo`* (migrated; fix mode added)
- *`audit-site`* (migrated)
- `**audit-pr`** — Optional thinner audit scoped to a single PR (different from `review-pr`).

### Layer 8 — Publish & ship

- *`publish-commit`* (migrated; uses `gh` CLI exclusively)
- *`publish-github`* (migrated; **all ops via `gh` CLI**, MCP fallback removed)
- *`publish-bitbucket`* (migrated)
- *`publish-confluence`* (migrated)
- *`publish-gdrive`* (migrated)
- `**cicd-monitor`** — Watches GitHub Actions on the current PR (`gh run watch`), reports failures, hands off to `cicd-fix`.
- `**cicd-fix*`* — Pulls failing job logs, identifies root cause, applies fix, pushes.

### Layer 9 — Observability & analytics

- `**observability-datadog**` — Query Datadog (logs, metrics, monitors, traces) via the `plugin-datadog-datadog` MCP server; modes: investigate | dashboard-summary | alert-triage.
- `**analytics-mixpanel**` — Query Mixpanel via MCP (or REST fallback); modes: funnel | cohort | usage-summary.
- `**observability-incident**` — Combines Datadog + recent deploys + Slack channel scrape for an incident summary.

### Layer 10 — Repo bootstrap

- `*adopt-ai-in-repo`* (migrated)
- `**personal-skill-create`** — Templates a user's own skill that composes existing `adk` skills (so users can build their own workflows).

### Top-level routers (kept for human discoverability, NOT for auto-invocation)

- `adk` (root router, points at `auto`)
- `plan`, `build`, `review`, `docs`, `audit`, `publish`, `visualize`, `frontend`, `observability` (one router per layer)

## 3. Auto-skill orchestration flow

```mermaid
flowchart TD
    Prompt["User prompt"] --> AutoSkill["auto skill activates"]
    AutoSkill --> Expand["Phase A: prompt expansion + classify domain"]
    Expand --> Plan["Phase B: brainstorm subagent + scoping subagent (loaded with plan-brainstorm + scoping)"]
    Plan --> ReqOK{Scope locked?}
    ReqOK -- no --> Plan
    ReqOK -- yes --> Dispatch["Phase C: dispatcher decides skill set per task slice"]
    Dispatch --> Parallel["Spawn N parallel subagents via Task tool"]
    Parallel --> Build["implementer + build-feature"]
    Parallel --> Doc["doc-writer + docs-write"]
    Parallel --> Test["test-engineer + build-test"]
    Build --> Validate["Phase D1: review-local + per-skill validator gate"]
    Doc --> Validate
    Test --> Validate
    Validate --> UiTouched{UI touched OR preview/*.html exists?}
    UiTouched -- yes --> Browser["Phase D2: validate-browser (verify-fix / visual-check / console-audit / a11y-audit)"]
    UiTouched -- no --> Pass{All green?}
    Browser --> Pass
    Pass -- no --> Dispatch
    Pass -- yes --> Publish["publish-commit + publish-github + cicd-monitor"]
    Publish --> CiPass{CI green?}
    CiPass -- no --> CiFix["cicd-fix"]
    CiFix --> Dispatch
    CiPass -- yes --> Done["Done"]
```



## 4. Skill dependency graph (high level)

```mermaid
flowchart LR
    auto --> requirements
    auto --> scoping
    requirements --> contextGather["context-gather"]
    requirements --> planBrainstorm["plan-brainstorm"]
    scoping --> planSpec["plan-spec"]
    scoping --> planDesign["plan-design"]
    planSpec --> planRoadmap["plan-roadmap"]
    planRoadmap --> buildFeature["build-feature"]
    buildFeature --> buildTest["build-test"]
    buildFeature --> reviewLocal["review-local"]
    reviewLocal --> publishCommit["publish-commit"]
    publishCommit --> publishGithub["publish-github"]
    publishGithub --> cicdMonitor["cicd-monitor"]
    cicdMonitor --> cicdFix["cicd-fix"]
    auto --> frontendDesign["frontend-design"]
    frontendDesign --> frontendMockup["frontend-mockup"]
    frontendMockup --> validateBrowser["validate-browser"]
    frontendMockup --> frontendFeature["frontend-feature"]
    frontendFeature --> validateBrowser
    buildBugfix["build-bugfix"] --> validateBrowser
    validateBrowser --> reviewLocal
    auto --> reviewPr["review-pr"]
    reviewPr --> reviewFeedback["review-feedback"]
    reviewPr --> contextGather
    docsWrite["docs-write"] --> docSiteSetup["doc-site-setup"]
    docSiteSetup --> docSiteDiagrams["doc-site-diagrams"]
    auto --> auditRepo["audit-repo"]
    setup --> all["all skills"]
    tempFolder["temp-folder"] --> all
```



## 5. Mode contract (every applicable skill)

```
--mode auto      # default — runs brainstorm + plan + execute end-to-end
--mode review    # produces findings only; writes review.md or posts comments; never edits source
--mode fix       # auto-applies its own findings, then validates
--auto           # skip approval gates (orthogonal to --mode)
```

Documented once in `skills/mode-contract/SKILL.md`; each skill that supports modes states which subset it supports in its frontmatter.

## 6. .temp/ task-folder convention

Every task creates `.temp/task-<slug>/` with the same canonical sub-paths:

```
.temp/task-<slug>/
├── context.md                              # gathered from links / Jira / Confluence / Slack
├── requirements.md                         # output of `requirements` skill
├── scope.md                                # output of `scoping` skill
├── brainstorm.md                           # output of `plan-brainstorm`
├── spec.md, design.md, roadmap.md
├── preview/sample-{1..5}.html              # frontend-mockup output
├── plan.md                                 # final implementation plan
├── validation/<phase>.md                   # per-phase validator logs
├── browser-validation/                     # output of `validate-browser` skill
│   ├── verify-fix/{screenshots,console,network,report.md}
│   ├── visual-check/{baseline,actual,diff}/<viewport>.png
│   ├── console-audit/report.md + raw.json
│   ├── interaction-test/{trace.md, screenshots/}
│   └── a11y-audit/report.md + axe.json
└── report.md                               # final deliverable report
```

Enforced by the `temp-folder` skill (which any other skill calls into for path resolution).

## 7. Cross-reference convention inside SKILL.md

```
After this, hand off to @adk:plan-spec (a.k.a. `adk-plan-spec`).
Spawn the implementer subagent (`agents/implementer.md`) loaded with @adk:build-feature.
See `references/workflow.md` for the full step list.
```

Both forms appear on first mention in any cross-reference; subsequent mentions can use either form.

## 8. Install paths

- **Primary — Claude plugin install:** `claude /plugin install adk` from a marketplace, OR `claude --plugin-dir ./agents-devkit` for dev. Plugin root contains everything (`.claude-plugin/plugin.json`, `skills/`, `agents/`, `hooks/`, `.mcp.json`, `bin/`).
- `**npx skills add sujeet-pro/agents-devkit`:** Picks up the parallel `agents-skills/` tree (folders prefixed `adk-<name>/`, each with a `SKILL.md` symlink → `skills/<name>/SKILL.md`).
- **Local symlink for multi-agent (`bin/adk-install`):** Symlinks `skills/` into `~/.claude/plugins/adk/skills/` AND `agents-skills/adk-<name>/` into `~/.cursor/skills/`, `~/.codex/skills/`, `~/.agents/skills/`, `~/.gemini/skills/`. macOS only (per user). ~150 LOC, replaces today's 18-file `cli/` tree.
- **MCP setup:** `bin/adk-mcp-install` reads `.mcp.json`, expands `${ENV_VAR}` from `~/.zshenv`, runs `claude mcp add ...` (or writes to `~/.claude/settings.json`).

## 9. MCP defaults (env vars from `~/.zshenv`)

Bundled in `.mcp.json` (commented-out by default; `adk-mcp-install` toggles on per user choice):

- `github` — already standard
- `bitbucket`, `jira`, `confluence` — Atlassian
- `google-drive` — for Google Doc context-gather
- `slack` — for Slack channel scrape
- `gmail` — for thread context
- `datadog` — for `observability-datadog`
- `mixpanel` — for `analytics-mixpanel`
- `brainstorming` — optional state store
- `cursor-ide-browser` — for `validate-browser` (preferred). Fallback: `playwright` MCP, then bare `npx playwright` if neither MCP is configured.

## 10. Phase-0 reference work (deep-read everything before any code)

Clone or refresh into `.temp/reference-repos/` and write per-repo findings to `.temp/plans/restructure-references-<repo>.md`:

- `https://github.com/buildermethods/agent-os` — for the `commands/` flat-skill model, `profiles/default/`, standards-injection pattern, and `scripts/project-install.sh` install model.
- `https://github.com/buildermethods/design-os` — for the structured product-design conversation model and `data-shape` / `design-tokens` / `design-screen` / `screenshot-design` flow.
- `https://github.com/anthropics/skills` (and any other repos referenced under existing reference materials) — to recheck the canonical SKILL.md format.
- Local: `~/personal/pagesmith` (read every `packages/docs/skills/pagesmith-*/SKILL.md` and `packages/docs/REFERENCE.md`) — these are wrapped by `doc-site-setup`.
- Local: `~/personal/diagramkit` (read every skill / CLI doc) — wrapped by `doc-site-diagrams`.
- The CURRENT `agents-devkit` repo itself — every existing `skills/adk-*/SKILL.md` and every `references/`* file, so the migration can be verbatim where appropriate (preserve language, update pointers, drop obsolete sections).

Findings consolidated into `.temp/plans/restructure-architecture.md` before any source change.

## 11. Files to remove (made obsolete)

- `agents-cursor/`, `agents-codex/` — collapsed into `agents/` (Claude-only per user note 1)
- `cli/` (18 files) — replaced by ~6 scripts in `bin/` (install, mcp-install, setup, sync-contracts, validate, doctor)
- `mcp-config/servers/*.json` — replaced by single `.mcp.json` at plugin root
- `global-prompts/interaction-contract.md` — moves to `bin/canonical/interaction-contract.md` (single source, propagated into every skill by `bin/adk-sync-contracts`); `temp-folder.md` becomes the `temp-folder` skill
- `workflows/*.yaml` — replaced by composable subagent dispatch from `auto`
- `hooks/cursor.json`, `hooks/codex.json` — kept only `claude.json` → renamed `hooks/hooks.json`
- `skills-manifest.json` — auto-regenerated by validator from `skills/` (still emitted for `npx skills`)

## 12. Files to keep untouched

- `docs/` and `gh-pages/` (per user)
- `.git/`, `LICENSE`, `package.json` (modified, not removed)
- `cli/lib/generate-skill-docs.mjs` and `cli/lib/validate-content.mjs` are kept as `bin/` helpers that the docs build uses

## 13. Phased execution

Even though delivery is "all-in-one", I will work through phases sequentially and write everything to `.temp/plans/restructure-*.md` first, then commit in one large PR.

- Phase 0: deep-read CURRENT repo + clone-and-read agent-os, design-os, plus inventory ~/personal/pagesmith and ~/personal/diagramkit. Lock the final skill catalog and dependency graph in `.temp/plans/restructure-architecture.md`.
- Phase 1: scaffold the new layout — `.claude-plugin/plugin.json`, empty `skills/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `bin/`* (incl. `bin/canonical/interaction-contract.md` + `bin/adk-sync-contracts`), `agents-skills/`, `package.json`, `README.md`. (No skill content yet, just structure.)
- Phase 2: write the 4 meta skills (`auto`, `setup`, `temp-folder`, `mode-contract`) — these set conventions every other skill follows.
- Phase 3: migrate the 39 existing skills — rename folders, rewrite `SKILL.md` frontmatter (`name:` field), update cross-references to dual form, add the new required `references/how-it-works.md` (with mermaid decision diagram) and `references/modes.md`. Run `bin/adk-sync-contracts` to seed every skill's `references/interaction-contract.md`. Create folder-level symlinks under `agents-skills/adk-<name>/`.
- Phase 4: write the new domain skills (`requirements`, `scoping`, `context-gather`, `frontend-mockup`, `build-bugfix`, `review-doc`, `validate-browser`, `doc-site-setup`, `doc-site-diagrams`, `observability-datadog`, `analytics-mixpanel`, `observability-incident`, `cicd-monitor`, `cicd-fix`, `audit-pr`, `publish-commit` `gh`-only rewrite, `personal-skill-create`, `plan-proposal`). Wire `validate-browser` into `frontend-feature`, `frontend-mockup`, `build-bugfix`, `review-pr --mode fix`, `audit-site` as their final validation step.
- Phase 5: write the subagent files in `agents/` (Claude format only).
- Phase 6: write the bin scripts (`adk-install`, `adk-mcp-install`, `adk-setup`, `adk-sync-contracts`, `adk-validate`, `adk-doctor`).
- Phase 7: validator enforces: every skill has `SKILL.md`, frontmatter `name` matches folder, dual-form cross-refs, required reference files present (`how-it-works.md`, `modes.md`, `validator.md`, `interaction-contract.md` byte-identical to canonical), `agents-skills/` symlinks intact. Run validator.
- Phase 8: regenerate `skills-manifest.json`, update `AGENTS.md` / `CLAUDE.md` to describe the new repo-as-plugin model.

## 14. Out of scope (explicit)

- Any change to `docs/` or `gh-pages/`.
- Windows support.
- Authoring inside the user's home directory (only the install script touches `~/`).
- Submitting the plugin to the official Anthropic marketplace (we ship a private `marketplace.json`, but the user runs the submit form themselves).

