---
title: 'adk-cli'
description: 'Python package home for the `adk` CLI subcommands. NOT a slash-invokable skill — install.py skips this directory when symlinking skills into agent skill dirs. The `adk` binary at `<repo>/bin/adk` is symlinked to...'
skill: 'adk-cli'
source: 'skills/adk-cli/SKILL.md'
group: 'skills'
order: 1000
---
# adk-cli

Python package home for the `adk` CLI subcommands. NOT a slash-invokable skill — install.py skips this directory when symlinking skills into agent skill dirs. The `adk` binary at `<repo>/bin/adk` is symlinked to `~/.local/bin/adk` at install time and dispatches to the modules under `scripts/`.

## Source

`skills/adk-cli/SKILL.md`

## Frontmatter

```yaml
name: adk-cli
description: Python package home for the `adk` CLI subcommands. NOT a slash-invokable skill — install.py skips this directory when symlinking skills into agent skill dirs. The `adk` binary at `<repo>/bin/adk` is symlinked to `~/.local/bin/adk` at install time and dispatches to the modules under `scripts/`.
disable-model-invocation: true
```

## Workflow body

# adk-cli — CLI subcommand package

This folder is the Python module home for the `adk` shell command. It is not
invokable as a slash-skill (`disable-model-invocation: true`) and `install.py`
skips it when fanning skills out into each host's skill directory.

The dispatcher is `<repo>/bin/adk`, which is symlinked into `~/.local/bin/adk`
at install time.

## Subcommand surface

```
adk pr-scan       walk Slack channels → upsert PR rows into the queue
adk pr-queue …    list / show / add / update / clean / ready-to-merge / release
adk skill-run …   run any /adk-* skill in Claude / Cursor / Codex / custom harness
adk repo …        add / update / list / branch / migrate — clone + per-branch index
adk doctor        validate env, deps, MCPs, ollama server, token presence
adk completion …  emit a bash | zsh | fish completion script
```

Every subcommand accepts `-y` / `--yes` for headless / smart-default operation
(no prompts). Skills can shell out via `adk <subcmd> -y …`.

## Files under scripts/

- `pr_scan.py` — `adk pr-scan`. Walks main message AND thread replies, emits
  one row per (PR-link, message-ts) so reactions land on the right message.
  `--channels` / `--channels-only` override the configured channel list.
- `pr_queue.py` — `adk pr-queue …`. Single-shot add from a slack permalink OR
  PR URL; cheap meta refresh on one row; lock release; merged-row cleanup; the
  ready-to-merge summary used at the tail of every review.
- `repo.py` — `adk repo …`. Clones repos to `$ADK_DATA_HOME/repos/<name>/`
  and indexes each tracked branch at
  `$ADK_DATA_HOME/repos/.indices/<name>/branches/<slug>/code-index/`.
  Default branch is auto-indexed by `add`; use `--branch X` (multi-arg) on
  `add`/`update`, and the `repo branch {add,remove,list}` subgroup to manage
  branches. Incremental reindex on `update` when HEAD has moved.
- `doctor.py` — `adk doctor`. Plain-text table of pass/warn/fail per check.
  `--tui` uses textual when importable; falls back to plain text otherwise.
- `completion.py` — `adk completion bash|zsh|fish`. Emits a static script.
  install.py installs them to the conventional user paths (unless `--no-completions`).
- `queue_io.py` — concurrency-safe queue read/update/merge + the atomic
  acquire_next_row / release_row used by `/adk-pr-review` no-arg mode.
- `slack_helpers.py` — slack web-api client (read + reactions + thread reply).
- `queue_release.py` — `release_after_review` called by `/adk-pr-review`'s
  report.py tail to update queue status + reconcile Slack reactions.
- `agent_harness.py` — shared model-depth defaults and command builders for
  Claude / Cursor / Codex / custom runners.
- `skill_run.py` — `adk skill-run`, a generic harness launcher for any ADK
  slash skill. `--detailed` forwards programmatic-detail intent; `--deep`
  selects the runner's stronger model profile.

## Queue location

`$ADK_CONFIG_HOME/pr-queue.json5`.

## Constitutional posture

- Slack token: PRESENCE only. `doctor` never reads the value (§VII).
- Queue updates: every write goes through `file_lock` on a `.lock` sidecar.
- Cleanups: `pr-queue clean --all` requires `--yes`; the constitution §I.7
  inhibits any blanket delete the user didn't explicitly ask for.

## References shipped

_(References authored on first real use of each sub-flow.)_
