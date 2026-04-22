# `auto` — dispatch matrix

Triggers → skill set → subagent. Multiple rows can fire per task.

| Trigger | Skill(s) | Subagent | Sequencing |
| --- | --- | --- | --- |
| Prompt has any link (Jira/Confluence/Slack/GDoc/Gmail/GH) | `context-gather` | `research-agent` | Phase A, before Phase B |
| Always | `requirements`, `scoping` | `brainstorm-facilitator` | Phase B |
| Code change required | `build-feature` (default) | `implementer` | Phase C |
| Bug with reproducer | `build-bugfix` | `implementer` | Phase C |
| Restructure without behavior change | `build-refactor` | `implementer` | Phase C |
| Framework / library version bump | `build-migrate` | `implementer` | Phase C |
| Dep upgrade only | `build-deps` | `implementer` | Phase C |
| New behavior to lock in | `build-test` | `test-engineer` | Phase C, parallel with implementer |
| Doc deliverable in scope | `docs-write` | `doc-writer` | Phase C, parallel |
| UI touched | `frontend-design` then `frontend-mockup` | (no subagent; auto runs them) | Phase C, BEFORE implementer |
| Frontend code change | `frontend-feature` | `implementer` | Phase C, after design+mockup |
| New CSR app from scratch | `frontend-react-csr` | `implementer` | Phase C |
| Change touches auth / payments / secrets | `audit-repo` (security focus) | `security-reviewer` | Phase D1 |
| Always at end of code-change task | `review-local` | `code-reviewer` | Phase D1 (aggregate) |
| UI touched OR preview/*.html exists | `validate-browser` | (no subagent; runs locally) | Phase D2 |
| Code-change task complete + green | `publish-commit` | (no subagent) | Phase D3 |
| Push + PR | `publish-github` (gh CLI) | (no subagent) | Phase D3 |
| Push to Bitbucket repo | `publish-bitbucket` | (no subagent) | Phase D3 (instead of github) |
| Doc deliverable on Confluence | `publish-confluence` | (no subagent) | Phase D3 |
| Doc deliverable on Google Drive | `publish-gdrive` | (no subagent) | Phase D3 |
| PR pushed | `cicd-monitor` | (no subagent; uses monitors/monitors.json) | Phase D3 |
| CI failed | `cicd-fix` | `debugger` | Phase D3 (loops back to C if code change) |
| Investigate Datadog incident | `observability-incident` | `debugger` | Standalone (not in normal Phase C) |
| Datadog query | `observability-datadog` | (no subagent) | Standalone |
| Mixpanel query | `analytics-mixpanel` | (no subagent) | Standalone |
| Repo audit | `audit-repo` | `code-reviewer` + `security-reviewer` parallel | Standalone |
| Site audit | `audit-site` | (no subagent) | Standalone |
| Single-PR audit | `audit-pr` | `code-reviewer` | Standalone |
| Adopt AI in a fresh repo | `adopt-ai-in-repo` | (no subagent) | Standalone |
| User wants to compose own skill | `personal-skill-create` | (no subagent) | Standalone |
| Setup docs site | `doc-site-setup` then `doc-site-diagrams` | (no subagent) | Standalone |
