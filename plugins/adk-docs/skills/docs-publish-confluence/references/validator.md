# `docs-publish-confluence` — per-phase validator

Logged to `.temp/task-<slug>/validation/docs-publish-confluence.md`.

## Phase 0

- [ ] `<md-file>` exists and is readable.
- [ ] Title resolved (from frontmatter, H1, or filename).
- [ ] `.temp/task-<slug>/` exists, gitignored.
- [ ] `source.md` (audit copy) written.

## Phase 1

- [ ] `bin/adk-info --check` == 0.
- [ ] Workspace Atlassian connector is `connected` per
      `claude mcp list` (or equivalent).
- [ ] Space `<space>` exists (connector query).
- [ ] Parent `<parent>` exists in the space (connector query).
- [ ] If markdown has mermaid fences: Mermaid macro availability in
      the space is recorded (available / fallback).

## Phase 2

- [ ] `storage.xhtml` exists and is valid XML.
- [ ] Every code fence in `source.md` is wrapped in
      `ac:structured-macro ac:name="code"` OR `"mermaid"`.
- [ ] Admonitions converted to info/warning/tip panels.
- [ ] No `<script>` / inline JavaScript.

## Phase 3 — idempotency

- [ ] `existence-check.md` recorded query result.
- [ ] If multiple matches (ambiguous), stop; do not auto-pick.
- [ ] Action decided: `new` | `update` | `defer`.
- [ ] If `defer` is the default (human last-editor), an explicit
      opt-in path is surfaced.

## Phase 4

- [ ] `publish-plan.md` matches the data the connector will send.
- [ ] User confirmed via the ask-once gate (required even under
      `--auto`).
- [ ] On update: expected version passed to connector (optimistic
      concurrency).
- [ ] On new: parent id passed.
- [ ] Connector returned 200/201 for the write.
- [ ] Any non-2xx is surfaced verbatim; no retry loop.

## Phase 5 — verify

- [ ] Re-fetched page by id.
- [ ] `published.md` records final version, URL, labels.
- [ ] Storage re-fetch diff: zero meaningful diff (macro ids and
      whitespace excepted).
- [ ] Labels = union of existing + requested.
- [ ] Final URL is valid (HTTP shape + space + page id consistent).

## Content guardrails

- [ ] Never created a duplicate page.
- [ ] Never overwrote a human-authored page without the second,
      explicit opt-in.
- [ ] Never changed restrictions / sharing.
- [ ] No secret patterns in `storage.xhtml`.

## On failure

- Log + block next phase.
- After 3 same-kind failures, stop and surface.
