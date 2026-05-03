---
title: 'adk-docs:docs-changelog'
description: '  Append or update a CHANGELOG.md entry from a set of commits or a release-tag range. Reads `git log <from>..<to>` and groups commits by type (Added / Changed / Deprecated / Removed / Fixed / Security per Keep a Changelog; or feat / fix / chore per semantic-release). Matches the existing changelog style detected from the file. Calls out breaking changes in a dedicated section at the top of the version block so downstream consumers see them first. Each entry is one user-readable sentence — not a git-log paste. With --fix, writes the entry into CHANGELOG.md at the canonical position (before the previous version block) and stages the change; does NOT commit. Use when prepping a release or after a feature merge. Do NOT use for PR descriptions (/adk-docs:docs-pr-description), commit messages (/adk-docs:docs-commit-message), or authoring a new doc (/adk-docs:docs-write).'
plugin: 'adk-docs'
skill: 'docs-changelog'
source: 'plugins/adk-docs/skills/docs-changelog/SKILL.md'
group: 'docs-skills'
order: 3101
---
# adk-docs:docs-changelog

## Source

`plugins/adk-docs/skills/docs-changelog/SKILL.md`

## Skill Body

# docs-changelog — append a user-readable changelog entry

Release-notes craft. Each entry is one human-readable sentence. Breaking
changes get top billing in the version block.

## When to use

- "update changelog for v1.2.0"
- "changelog entry for the latest release tag"
- "write release notes for v2.0.0"
- "append today's merged features to CHANGELOG.md"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| PR description | `/adk-docs:docs-pr-description` |
| Commit message | `/adk-docs:docs-commit-message` |
| New doc / README / runbook | `/adk-docs:docs-write` |
| Publish CHANGELOG to Confluence | `/adk-docs:docs-publish-confluence` |

## Common prompts

- "update changelog for v1.2.0"
- "release notes for v2.0.0"
- "changelog entry"
- "what's new since v1.1.0"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<from-tag>` | yes | — |
| `<to-tag>` | no | `HEAD` |
| `--auto` | no | (default) |
| `--fix` | no | off; with it, writes the entry into `CHANGELOG.md` and stages |

## Workflow

```
Phase 0 — prompt expansion
  - Resolve repo; find CHANGELOG.md (docs.md.changelog_path default).
  - Resolve <from-tag>, <to-tag>.
  - Pick slug (e.g. changelog-<to-tag>); create .temp/task-<slug>/.

Phase 1 — preflight
  - bin/adk-info --check.
  - Verify <from-tag>..<to-tag> resolves: git rev-parse <from-tag> and <to-tag>.
  - Detect existing changelog style (Keep a Changelog | semantic-release | free-form).
    See references/keep-a-changelog-format.md.

Phase 2 — gather evidence
  - git log <from>..<to> --pretty=format:%H%x1f%s%x1f%b%x1e > commits.txt.
  - Classify each commit: Added / Changed / Deprecated / Removed / Fixed /
    Security (per Keep a Changelog) or feat / fix / chore (per semantic).
  - Detect breaking changes per references/breaking-change-callout.md.

Phase 3 — draft
  - Build one entry per group. Each entry: one user-readable sentence
    (NOT a commit subject paste).
  - Breaking changes land in a dedicated section at the top of the
    version block.
  - Entries reference the PR number or commit SHA at the end.

Phase 4 — validate + optional --fix
  - Validator: no invented items (every entry traces to a commit);
    breaking-changes section present if any breaking commits;
    matches existing style.
  - --fix: insert the new entry BEFORE the previous version block;
    preserve existing formatting; git add CHANGELOG.md (stage only).
```

See `references/workflow.md`.

## Persona

> "User-readable changelog, not git-log-paste." Each entry is a sentence
> the downstream consumer can act on: "adds support for partial
> refunds on gift orders" beats "feat(orders): partial-refund hook".

See `references/persona.md`.

## Constitution

**Must do:**

1. Match the existing changelog style (Keep a Changelog, semantic-
   release, free-form) detected from the file.
2. Call out breaking changes prominently — dedicated section at the
   top of the version block, per
   `references/breaking-change-callout.md`.
3. Each entry is one user-readable sentence. Link to the PR or commit
   for detail.
4. Group by type; order groups per the detected style.

**Must not do:**

1. Invent items not in the `<from>..<to>` range.
2. Paste commit subjects verbatim as changelog entries.
3. Auto-commit. This skill stages only; the user commits separately.
4. Overwrite an existing version block without explicit user opt-in
   (refreshing a release's changelog is a `-i --fix` flow).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Git-log paste as changelog entries.
- Missing a breaking-changes section when one is needed.
- One giant "Other" bucket with every non-feature change.
- Inventing items to "round out" the release notes.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + timestamp |
| `.temp/task-<slug>/commits.txt` | Raw git-log output |
| `.temp/task-<slug>/classified.md` | Commits grouped by type with breaking-change flags |
| `.temp/task-<slug>/changelog-entry.md` | The new version block to insert |
| `.temp/task-<slug>/report.md` | Final consolidated report |
| `CHANGELOG.md` | (under `--fix`) with the new entry inserted |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | User-readable-release-notes persona |
| `references/workflow.md` | Phase 0–4 stage detail |
| `references/modes.md` | `--auto / -i / --fix` for this skill |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked changelog entries (Keep a Changelog + semantic-release) |
| `references/output-format.md` | Exact `changelog-entry.md` shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid flow |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/keep-a-changelog-format.md` | Keep a Changelog structure + detection rules |
| `references/breaking-change-callout.md` | Breaking-change placement + phrasing rules |

## Additional links

- https://keepachangelog.com/ — the Keep a Changelog spec (quoted ≤15 words; linked for the rest).
- semantic-release upstream docs for auto-generated changelog comparisons.
