---
# ~/.config/adk/docs.md
# Documentation authoring + publishing conventions. Used by adk-docs:*.

default_confluence_space: ENG
default_confluence_parent: "Engineering Home"
default_gdrive_folder_id: "1AbCdEf..."
doc_templates_path: ~/.config/adk/templates/
adr_path: docs/adr/
runbook_path: docs/runbooks/
changelog_path: CHANGELOG.md
mermaid_render_mode: light_and_dark   # light | dark | light_and_dark
audience_default: engineer            # engineer | pm | em | mixed
labels:
  default_publish_label: adk-published
  reviewer_required_label: needs-review
---

# Notes

- The `default_confluence_space` is where new pages go unless overridden by a skill flag.
- The `default_gdrive_folder_id` is the GDrive folder Mark's content goes into when published as a Google Doc.
- The `audience_default` calibrates prose tone:
  - `engineer` — dense, technical, code-heavy.
  - `pm` — concrete, decision-oriented, less jargon.
  - `em` — risk-aware, milestone-shaped.
  - `mixed` — middle ground; explain jargon on first use.
- ADRs go to `docs/adr/<n>-<slug>.md` per the path above.
- Runbooks go to `docs/runbooks/<service-or-domain>.md`.
