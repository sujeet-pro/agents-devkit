---
title: 'plan-proposal'
description: 'Author a formal stakeholder proposal — a one-pager (or short multi-page) doc with: problem, options considered, recommendation with rationale, cost/risk/timeline, decision asked of the audience.'
artifact_kind: skill
skill_name: plan-proposal
category: plan
---
# plan-proposal

Author a formal stakeholder proposal — a one-pager (or short multi-page) doc with: problem, options considered, recommendation with rationale, cost/risk/timeline, decision asked of the audience. Different from `@adk:plan-brainstorm` (a.k.a. `adk-plan-brainstorm`) (which is the iterative thinking process) and from `@adk:plan-spec` (a.k.a. `adk-plan-spec`) (which is the implementation spec). Use when a decision needs to be presented to a wider audience (manager, architecture review, leadership) BEFORE plan-spec / plan-roadmap. Do not use for an internal implementation plan (use `@adk:plan-roadmap` (a.k.a. `adk-plan-roadmap`)).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-plan-proposal` form via `agents-skills/`.

```text
/adk:plan-proposal            # interactive run (Claude Code)
/adk:plan-proposal --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-plan-proposal` (resolved through the
`agents-skills/adk-plan-proposal/` symlink).

## Source

Direct from `skills/plan-proposal/SKILL.md` — this page is auto-generated.

## When to use

- Before plan-spec, you need stakeholder buy-in on a directional choice.
- You have 2-3 viable options and want a written recommendation that captures the trade-offs.
- The audience is non-engineering or cross-functional (PM, design, SRE, leadership).

## When NOT to use

- Iterative ambiguity-closing → `@adk:plan-brainstorm`.
- Detailed implementation spec → `@adk:plan-spec`.
- Architecture write-up for engineers only → `@adk:plan-design`.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<problem>` | yes | One sentence; what needs deciding |
| `<audience>` | yes | Manager / architecture / leadership / cross-functional |
| `<options>` | optional | If empty, brainstorm first via `@adk:plan-brainstorm` |
| `<deadline>` | optional | When the decision is needed |

## Workflow

1. Phase 1 validator. Audience known. Problem stated in one sentence.
2. If `<options>` is empty, dispatch `@adk:plan-brainstorm` first.
3. Read brainstorm.md (if exists). Refine to 2-3 options the audience can choose between.
4. For each option, capture: what it is, cost (eng-weeks), risk, timeline, reversibility, key trade-off.
5. Pick a recommendation. Write rationale (3-5 sentences).
6. Frame the **decision asked**: one sentence the audience can answer yes/no.
7. Write `proposal.md` per the template.
8. Phase 4 validator. Approval gate (you, the human author, sign off before sending).

## Output

`.temp/task-<slug>/proposal.md`:

```markdown
# Proposal — <one-sentence problem>

**Audience:** <names / forum>
**Author:** <user>
**Date:** <today>
**Decision needed by:** <deadline>

## TL;DR
- Problem: <one sentence>
- Recommend: <option name>
- Why: <one-sentence rationale>
- Decision asked: <yes/no question>

## Background (≤150 words)
<context the audience needs>

## Options

### Option A: <name>
- What: <one paragraph>
- Cost: <eng-weeks>
- Risk: <low/med/high + one sentence>
- Timeline: <weeks>
- Reversibility: <easy/moderate/hard>
- Key trade-off: <one sentence>

### Option B: <name>
...

### Option C: <name>
...

## Recommendation: Option <X>
<3-5 sentence rationale, addressing why-not the others>

## Decision asked
> <one-sentence yes/no question>

## Open questions
- <if any>

## Appendix (optional)
- Brainstorm notes: link to brainstorm.md
- References: ...
```

## Mode

`auto` only.

## Anti-patterns

- More than 3 options. The audience cannot decide.
- "Recommendation" with no rationale.
- Buried decision-asked.
- Eng-jargon in audience-facing sections.
- Page count > 2 for a stakeholder proposal.
- Missing cost/risk/timeline numbers.

## References

Standard set + `references/proposal-template.md` (the template above expanded with examples).


## Related skills

- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`plan-brainstorm`](./skill-plan-brainstorm.md) — `@adk:plan-brainstorm` (a.k.a. `adk-plan-brainstorm`)
- [`plan-design`](./skill-plan-design.md) — `@adk:plan-design` (a.k.a. `adk-plan-design`)
- [`plan-spec`](./skill-plan-spec.md) — `@adk:plan-spec` (a.k.a. `adk-plan-spec`)
