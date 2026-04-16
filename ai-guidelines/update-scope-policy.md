# Update Scope Policy

## Goal
When a workflow or guidance change is proposed, decide whether it affects:
- one skill
- one skill family
- all published skills
- project-only skills
- docs and attribution only

## Decision Table
| Change Type | Scope |
| --- | --- |
| Core constitution change | All published skills + all project-only skills |
| Shared research method change | All published skills + all project-only skills |
| Shared brainstorming workflow change | All published skills + all project-only skills |
| Response style change | All published skills + all project-only skills |
| Review-specific workflow change | `adk-review-*` family only |
| Build or implementation workflow change | `adk-build-*`, `adk-refactor`, `adk-migrate` |
| Docs authoring change | `adk-write-*` family only |
| Source-specific syntax or capability change | Only mapped skills in `sources/registry.json` |
| Repo maintenance behavior change | Project-only skills only |
| Attribution-only change | Docs + `NOTICE.md` + registry |

## Scope Test
Ask these questions in order:
1. Does this change alter the constitution?
2. Does it alter a shared method used by most skills?
3. Does it alter one task family only?
4. Does it alter one upstream tool or repo mapping only?
5. Does it only affect project maintenance?
6. Does it only affect docs or attribution?

## Required Output For The Updater
- proposed change
- affected scope
- why that scope applies
- files to update
- validation required

## Examples
- New research rule requiring explicit verified/inferred/open labeling:
  - scope: all published skills + project-only skills
- New PR review severity rubric:
  - scope: `adk-review-pr`, `adk-review-local-changes`, `adk-address-review-feedback`
- New browser automation tool syntax:
  - scope: only skills mapped to that tool in `sources/registry.json`

## Safety Rule
If the scope is unclear:
- do not apply bulk changes
- stop at analysis
- present the smallest safe scope first
