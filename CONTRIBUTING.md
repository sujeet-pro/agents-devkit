# Contributing to adk — agents-devkit

Thanks for your interest in adk. This is a single-repo, multi-agent skill kit; contributions are welcome — bug reports, fixes, new skills, sub-flows, MCP wiring, docs, you name it.

Please read this whole file before opening your first PR. It's short.

## 1. Code of conduct

This project follows the [Contributor Covenant 2.1](./CODE_OF_CONDUCT.md). Be kind, be specific, assume good faith. Enforcement contact: `sujeet@onequince.com`.

## 2. Hard rules (the constitution)

Every contribution — code, docs, even a one-line README tweak — is bound by `shared/constitution.md`. The high-impact rules:

- **§I — Shared state.** No force-pushes to remotes you don't own, no merging PRs autonomously, no pushing to `main` / `master` / `release/*` / `prod/*`. Posting / commenting / mutating shared destinations (Slack, Jira, Confluence, Statsig, dashboards) is gated on per-invocation human confirmation. `--auto` waives clarifying questions; it does NOT waive these gates.
- **§II — Honesty.** Quote evidence (`path/to/file.py:42`) for any non-trivial claim. State confidence (`low / medium / high`). Refuse to invent results when an MCP or env var is unreachable — say so and name the gap.
- **§V — Code edits.** Smallest correct change. No drive-by cleanup, no opportunistic refactors, no features the task didn't ask for. Read every file before writing it. Match existing conventions.
- **§VII — Secrets.** Never bring credential values into agent context. No `cat ~/.zshenv`, no `echo $FOO_TOKEN_CRED`, no `Read` on `~/.config/creds/*/*`. Presence-only diagnostics; exercise the credential in a script that only emits a status code. See `shared/constitution.md` §VII for the full list of off-limits files and env-var-name suffixes.

The constitution is non-negotiable. PRs that violate it will not be merged.

## 3. Dev setup

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit

# Wire the kit into your active agent(s). Idempotent.
./install.sh                            # autodetects installed agents
./install.sh --target claude            # one agent
./install.sh --dry-run                  # preview without writing
./install.sh --uninstall                # remove by marker; preserves your overrides

# Python deps for the test suite.
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r skills/adk-cli/scripts/requirements.txt
pip install -r skills/adk-pr-review/scripts/requirements.txt
pip install pytest

# Run the suite.
pytest                                  # full repo
pytest tui/tests/                       # one slice
pytest -k recap_screen                  # one test
```

`./install.sh --check` (or `/adk-setup --check` from inside your agent) verifies env vars, CLI deps, and MCP reachability.

Full env-var + CLI-deps walkthrough: `SETUP.md`.

## 4. Branch naming

```
<type>/<short-slug>
```

`<type>` matches the commit-message types in §5. `<short-slug>` is kebab-case, ≤4 words, descriptive of the change — not the issue number.

Examples:

```
feat/recap-modal-clip-fix
fix/tui-screen-stack-race
docs/contributing-guide
refactor/code-index-batch-embed
```

Branch off `main`. Keep branches short-lived; rebase on `main` before opening the PR.

## 5. Commit message style

Conventional Commits. Look at `git log --oneline -20` for the de facto style. The shape:

```
<type>(<scope>): <imperative summary ≤72 chars>

<optional body — wrap at ~72 cols; explain WHY, not what>
```

Types in active use: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `cleanup`. Scope is the slice that changed (`tui`, `pr-review`, `cli`, `install`, `tests`, `scripts`, …). For sub-flows or the TUI's Greek-letter sub-phases, the scope can include the letter (e.g. `feat(tui): λ — …`).

Examples from history:

```
fix(tui): timer-driven reloads target default screen + unmount-safe
feat(tui): ι — end-of-run recap modal after batch finishes
refactor(scripts): hoist shared helpers to adk_common.py
docs: apply Karpathy framework patches (Phase 1B P-002/P-003/P-004)
```

**No agent attribution lines.** The project does not include `Co-Authored-By: Claude …` or `🤖 Generated with …` footers in commit messages. Author your own commits.

If you used an agent (Claude Code, Cursor, Codex, Junie) to draft a change, that's fine — but the human running the agent reviews + commits + takes responsibility.

## 6. PR expectations

1. **One concern per PR.** A bug fix doesn't need a refactor next to it. If you spotted something else worth fixing, file an issue or open a separate PR.
2. **Tests for new behavior.** New features land with at least one happy-path and one boundary test. Bug fixes land with the regression test that would have caught the bug.
3. **Validators must pass.** Run `pytest` locally before pushing. CI runs the same suite (`.github/workflows/test.yml`) and will block merge on a red.
4. **Fill in the PR template.** Summary, test plan, constitution checklist. The template is at `.github/PULL_REQUEST_TEMPLATE.md` (lands with Track C of the rc1 plan).
5. **Don't push to protected branches.** `main` is protected (constitution §I.2). Open a PR.
6. **Don't merge your own PR autonomously.** Even when CI is green, merge is a human action. Recommend, don't click.

Review turnaround is best-effort. Ping in the PR thread if it's been quiet for >7 days.

## 7. The question-first contract (relevant for skill changes)

Every skill walks `shared/question-first.md` before executing:

- Default mode is **auto** — the agent picks the recommended default for each fork, logs the choice to `~/.agents-devkit/improve/learning/decisions.jsonl`, and narrates the pick so the user can interrupt.
- `-i` / `--interactive` actually asks (cap 3 user-facing questions).
- "I don't know" hands off to `/adk-explain`.

If you're adding a new skill or a sub-flow, your SKILL.md must (a) list the `fork_id`s the skill emits, (b) define a recommended default per fork, and (c) NOT require interactive input to make progress.

Shared-state writes (Slack post, PR comment, Confluence page update, Statsig mutation) ALWAYS confirm per invocation, regardless of mode (constitution §I.4).

## 8. The decision-log obligation

Every non-trivial fork your skill resolves gets one JSONL line in `~/.agents-devkit/improve/learning/decisions.jsonl`. Schema: `shared/decision-log-schema.md`. These lines feed `/adk-improve`, which proposes default updates to `~/.agents-devkit/config/core.yaml`.

If you're touching a skill, audit its decision-log emissions:

- Every user-answered question logged with `fork_type: user-answered`.
- Every silent-default with `fork_type: auto-defaulted` and an `evidence` field.
- Every override hit with `fork_type: override-applied`.
- Every inferred-from-context choice with `fork_type: inferred`.

Don't log free-form prose. Don't log PII. Don't log credential values.

## 9. File layout & where things go

- **Skills**: `skills/adk-<name>/SKILL.md` (the spec), `skills/adk-<name>/references/<sub-flow>.md` (the sub-flows), `skills/adk-<name>/scripts/` (any Python helpers).
- **Shared rules**: `shared/constitution.md`, `shared/paths.md`, `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`, `shared/decision-log-schema.md`. All loaded by every skill at runtime.
- **MCP wiring**: `mcp/adk-mcp-*.json` — one file per MCP. `install.sh` merges these into each agent's config.
- **Per-agent installers**: `agents-claude/`, `agents-cursor/`, `agents-codex/`, `agents-junie/`. Per-agent gaps documented in each folder's README.
- **CLI binary**: `bin/adk` (shell shim) → `scripts/adk_cli.py`. Sub-verbs in `scripts/lib/cli/`.
- **TUI**: `tui/` (Textual). Tests under `tui/tests/`.
- **Docs**: `docs/` — plans, archive, progress. Active plans at the top level of `docs/plans/`; historical sessions under `docs/plans/archive/<session>/`.
- **Tests**: collocated under each slice — `tui/tests/`, `skills/adk-cli/scripts/tests/`, `skills/adk-pr-review/scripts/tests/`.
- **Task folders**: `<repo>/.temp/adk/<skill>/<task>/` (repo-bound skills) or `~/.agents-devkit/<area>/<task>/` (global skills). Both gitignored. See `shared/paths.md` for the full layout.

## 10. Releasing

Release tagging lives in `docs/plans/release-readiness-v4-rc1.md` (Track F). Contributors don't tag releases; the maintainer does, after CI is green and the human-confirmation gate in constitution §I has been satisfied.

## 11. Questions

Open a GitHub Discussion (preferred for "is this a bug or did I misconfigure something?") or an issue using the appropriate template. Email the maintainer (`sujeet@onequince.com`) only for security reports — see `SECURITY.md`.
