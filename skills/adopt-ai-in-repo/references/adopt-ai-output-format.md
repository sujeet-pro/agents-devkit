# Output Format for `adk-adopt-ai-in-repo`

The skill always produces two layers of output: a **default** (concise, decision-oriented) report and an **on-request detailed** report.

## Status banner (always first)

Lead the report with one of:

```
ADOPT-AI-DRAFT (plan only)  |  ADOPT-AI-BOOTSTRAPPED <n files>  |  ADOPT-AI-REFRESHED <n files>  |  AWAITING-APPROVAL-FOR-PLAN
```

## Default report (always shown)

```
<status banner>

## Adopt AI: <repo path>
- Mode: <fresh-bootstrap | refresh>
- Scope: <all | <stack>>
- Hooks: <wired | skipped>
- Merge aggressiveness: <preserve-and-merge | replace-managed-only | report-conflicts-only>  (refresh only)
- Commit policy: <leave-unstaged | stage-all | commit-with-message>

## Detected stack
- Repo type: <single-app | monorepo | service | library | infra | docs | data>
- Languages: <list>
- Frameworks: <list>
- Package manager: <name + version>
- Lint / format: <tool + config path>
- Typecheck: <tool + command>
- Tests: <framework + command + scope>
- Build: <tool + command>
- CI: <provider + key workflow paths>
- Commit convention: <conventional / plain / other> (evidence: last 50 commits)
- PR convention: <template path or "none">

## Generated file tree
<tree of files generated, with NEW / UPDATED / SKIPPED-NO-CHANGE / SKIPPED-USER-CONTENT marker per file>

## Skill catalog
- .claude/skills/development/SKILL.md
- .claude/skills/refactor/SKILL.md
- ... (one row per generated wrapper)

## Hook coverage  (if hooks wired)
- pre-commit: <command(s) wired>  → `ai-guidelines/scripts/run_project_checks.py format-and-lint`
- pre-push: <command(s) wired>    → `ai-guidelines/scripts/run_project_checks.py typecheck-and-test`
- refresh-after-stack-change: <trigger paths>  → suggests `adk-adopt-ai-in-repo --refresh`

## Validation (per `adopt-ai-validator.md`)
- Phase 1 (pre-execution): OK
- Phase 2 (mid-flow gates): OK
- Phase 3 (pre-handoff): OK
- Phase 4 (post-execution): OK
- Validator log: `.temp/notes/adopt-ai-<repo-slug>-validator.md`

## Decisions auto-picked (if --auto)
- <decision> — <one-line rationale>

## Manual follow-up
- <bulleted, prioritized — e.g., "review the merge diff for `AGENTS.md` at .temp/notes/...">
- <e.g., "the e2e command in `scripts-and-commands.md` requires Docker; install before relying on it">

Need more detail on any section? Pass `--verbose` or ask explicitly.
```

## Detailed report (on request, or under `--verbose`)

Add to the default:

- Full evidence summary from the `repo-analysis-playbook.md` pass.
- Per-file rationale (why this file, why these contents).
- Command-validation output (which `lint`/`format`/`test` commands were run during validation and their exit codes).
- Merge diff for any preserved user content.
- Full hook config (`.cursor/hooks.json`, `.claude/settings.json`) inline.
- The full skill-wrapper Markdown for one wrapper as a reference.

## Decisions auto-picked under `--auto`

When running under `--auto`, the report MUST list each decision the skill auto-picked, with a one-line rationale, so the user can audit retrospectively. The list always includes:

- mode (auto-detected)
- scope (default `all`)
- hooks (default `wire-hooks`)
- merge aggressiveness (default `preserve-and-merge`)
- commit policy (default `leave-unstaged`)

## Verbosity rules

- Lead with the status banner, then the detected stack, then the generated file tree.
- Use bullets for process and counts; reserve prose for the manual follow-up rationale.
- Do not dump long context unprompted; offer it instead.
- Keep raw inspection notes, full evidence summary, and merge diffs in `.temp/notes/`.
