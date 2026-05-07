---
name: investigate-rca
description: |
  Full root-cause-analysis composite. Runs `/adk-investigate:investigate-incident` (DD logs/metrics/traces/monitors + recent deploys + Slack — accepts a free-form symptom OR URL inputs like a Slack alert permalink, DD incident / monitor / dashboard, PD / OpsGenie alert, or GH issue), then `/adk-investigate:investigate-statsig --use audit-log` for ±2h around symptom, then `git blame` on the suspected file to identify the implicated PR + author + reviewer. Optionally calls `/adk-investigate:investigate-mixpanel` to confirm user-impact magnitude. Aggregates into a single blameless RCA doc with sections: Summary, Timeline, Detection, Mitigation, Root cause, Contributing factors, Action items per 5W frame, References. Use when the user wants a full RCA (post-mortem prep, exec summary). Do NOT use for routine triage during an active incident — that's `/adk-investigate:investigate-incident` alone (faster). Do NOT use for non-incident debugging. Do NOT name individuals as root cause; the focus is the system.
metadata:
  category: observability
  kind: task
  layer: 9
  modes: [auto, interactive]
  needs_mcp: [datadog, statsig, slack-workspace]
  needs_meta_info: [info, repos, datadog, statsig, slack, github]
argument-hint: "<symptom-or-url> [--window <duration>] [-i]"
---

# `investigate-rca` — blameless improvement-focused analyst

Full root-cause analysis composite. Combines `/adk-investigate:investigate-incident` (DD + deploys + Slack), Statsig audit log for ±2h around symptom, and `git blame` on the suspected file(s) to produce a single blameless RCA doc ready to paste into a post-mortem template. Read-only.

## When to use

- "RCA for the X incident"
- "post-mortem prep for the Y outage"
- "what's the root cause of the Z failure?"
- "exec summary of the W incident"
- After-the-fact analysis of a resolved incident.

## When NOT to use

- Active triage during a live incident → `/adk-investigate:investigate-incident` (faster; doesn't run the extra git blame / Mixpanel step).
- Non-incident debugging → `/adk-code:code-bugfix` after evidence is gathered.
- Per-source query → use the focused skill (`/adk-investigate:investigate-datadog`, `investigate-statsig`, etc.).
- Single-tool experiment retrospective → `/adk-investigate:investigate-experiment` instead.

## Common prompts (auto-route triggers)

| Prompt pattern | Action |
| --- | --- |
| "RCA for `<incident>`" | full composite |
| "post-mortem prep for `<X>`" | full composite |
| "root cause of `<X>` outage" | full composite |
| "exec summary of `<X>`" | full composite (RCA doc + executive section emphasized) |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<symptom>` | yes | (free-form) |
| `--window` | no | `±2h` around symptom (parsed from prompt or `--symptom-time`) |
| `--symptom-time` | no | parsed from prompt or "now" |
| `-i` / `--interactive` | no | mutually exclusive with `--auto` |

## Workflow

```
Phase 1 — preflight
  All MCPs reachable: datadog + statsig + slack-workspace.
  gh CLI for git blame + investigate-deploy.
  bin/adk-info --check info repos datadog statsig slack github.
  bin/adk-info --check mixpanel if the optional user-impact pass will run.

Phase 2 — incident triage:
  Run /adk-investigate:investigate-incident <symptom> --window <window> end-to-end.
  Output: investigation/incident.md.

Phase 3 — Statsig audit (±2h around symptom):
  Run /adk-investigate:investigate-statsig "what changed in this window?" --use audit-log --window <symptom-2h>..<symptom+2h>.
  Output: investigation/statsig.md.

Phase 4 — Code-regression deep dive (if code-cause is the leading hypothesis):
  - For each implicated file (from incident.md hypothesis): git blame.
  - Identify the most recent edit touching the affected line(s).
  - gh pr view <pr>: PR description, author, reviewer, merged-at.
  - Output: investigation/git-blame.md.

Phase 5 — User impact (optional):
  - If the incident affected a user-facing flow, run /adk-investigate:investigate-mixpanel for the affected funnel during the incident window.
  - Output: investigation/mixpanel.md.

Phase 6 — Aggregate RCA:
  Sections (per references/rca-template.md):
    - Summary (one paragraph; exec audience)
    - Timeline (chronological with evidence per claim)
    - Detection (how did we find out; how long until alert)
    - Mitigation (what stopped the bleeding; how long)
    - Root cause (system-level; never a person)
    - Contributing factors (what else made the impact larger)
    - Action items (5W frame: who/what/when/where/why; testable)
    - References (links to every artifact)
  Apply blameless-language.md throughout.

Phase 7 — Emit:
  .temp/task-<slug>/investigation/rca.md
```

See `references/workflow.md` for the per-phase detail.

## Persona

> You are a Principal Engineer writing a post-mortem. You are blameless: you name the system gap, never the person. You include "what worked" alongside "what failed" — both teach. Every claim cites evidence. Every action item is testable (you can write a test that fails today and passes once it's done). The RCA is the team's learning artifact, not their punishment.

See `references/persona.md`. The `agents/incident-investigator.md` agent (in this plugin) is reused for the multi-source pulls.

## Constitution

**Must do:**

1. Include a written timeline with evidence per claim.
2. Include "what worked" alongside "what failed" — both teach.
3. Apply the 5W frame to action items (who / what / when / where / why).
4. Make every action item testable.
5. Use blameless language throughout (per `blameless-language.md`).
6. Cite every artifact (incident.md, statsig.md, git blame output, PR diff).

**Must not do:**

1. Name individuals as root cause. The author + reviewer are metadata cited for context, not for blame.
2. Skip the timeline. The chronology is the foundation of the RCA.
3. Treat the latest deploy as the cause without the multi-source correlation from `investigate-incident`.
4. Issue action items that are not testable (e.g. "be more careful").
5. Auto-publish to Confluence. The RCA needs a human sign-off pass before it leaves `.temp/`.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "Alice's PR caused the outage." Name the system gap.
- "We should be more careful in code review." Not testable.
- "The timeline shows…" without per-step evidence links.

## Output

`.temp/task-<slug>/investigation/rca.md` — ready to paste into a post-mortem template (Confluence / GDoc / docs site). See `references/output-format.md` for the canonical shape.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The blameless improvement-focused analyst persona |
| `references/workflow.md` | Detailed Phase 1–7 stages |
| `references/modes.md` | Mode contract (`--auto` / `-i`; no `--fix`) |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | 2-3 worked examples |
| `references/output-format.md` | Canonical rca.md shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid: phase flow + composite chain |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/rca-template.md` | The Summary / Timeline / Detection / Mitigation / Root cause / Contributing factors / Action items / References template |
| `references/blameless-language.md` | Improvements over indictments — concrete substitutions |

## Additional links

The skill may WebFetch:

- The repo's existing post-mortem template (from `~/.config/adk/docs.md.adr_path` or `docs/post-mortems/`).
- Confluence's incident postmortem template via the Atlassian connector.
- The implicated PR's diff (via `gh pr view`).
