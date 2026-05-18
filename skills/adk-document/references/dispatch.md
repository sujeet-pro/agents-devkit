# adk-document — type dispatch

> Routes by `--type`. Each type maps to a template + voice + length target.

| --type | What it produces | Reference |
|---|---|---|
| `runbook` | Symptom → diagnose → mitigate → escalate | `runbook.md` |
| `adr` | Status / context / decision / consequences / alternatives | `adr.md` |
| `rca` | Summary / timeline / detection / mitigation / root-cause / contributing / action-items / refs | `rca.md` |
| `pr-body` | Summary / risk / test plan / breaking / follow-ups | `pr-body.md` |
| `commit-msg` | Subject ≤72 / body @ 72 / why-not-what | `commit-msg.md` |
| `changelog` | KaC or semantic-release format | `changelog.md` |
| `diagram` | Mermaid; ≤15 nodes; flowchart/sequence/class/state/ER/etc. | `diagram.md` |
| `readme` | What / why / install / use / contribute | `readme.md` |
| `migration-guide` | Before / after / step-by-step / rollback | `migration-guide.md` |
| `api-reference` | Endpoint × resource grid | `api-reference.md` |
| `experiment-report` | Inputs / verdict / evidence / next | `experiment-report.md` |
| `incident-summary` | One-pager exec form of an incident | `incident-summary.md` |
| `handoff` | Capture session state for resume (paired with `/adk-review:review-handoff` legacy flow) | `handoff.md` |
| `onboarding` | Day-one tasks + env + first task + who-to-ask | `onboarding.md` |

If `--type` is missing, the skill infers from the input shape (e.g. a Statsig URL → `experiment-report`; a DD incident URL → `incident-summary`).

## When the type doesn't fit

- "Write a tutorial" → `readme` with `--audience mixed`.
- "Write a design doc" → currently maps to `adr` with the alternatives section emphasized; flag if you want a dedicated `design-doc` type.
