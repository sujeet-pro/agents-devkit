---
title: "communication"
description: "Communication style rules for all DevKit output"
skill_name: communication
category: guideline
workflow_tier: helper
user_invocable: false
---

# communication

Communication style rules applied to every response, deliverable, and summary produced by any DevKit skill. Enforces a concise, conclusion-first writing style with concrete specifics.

## Purpose

- Establish a consistent tone and structure across all DevKit output
- Eliminate preamble, filler, and verbose narration
- Ensure answers lead with conclusions and offer detail on request
- Define concrete before/after examples so skills can calibrate output

## Key Rules

1. **Lead with conclusion, then reasoning** — never bury the answer
2. **Concise by default, elaborate on request** — show the compact result first; offer "Need a detailed breakdown?" instead of dumping full output
3. **Bullet points for multi-part answers**, not paragraphs
4. **Decisions**: state decision, key factor, max 2 supporting points
5. **Show reasoning concisely**: "X because Y, which means Z"
6. **Never repeat what the user said** back to them verbatim
7. **No preamble**: skip "Great question!", "I'd be happy to help!", "Let me think about this..."
8. **No trailing summaries** restating what was just done
9. **Concrete specifics over abstract descriptions**: "the auth middleware in `src/middleware/auth.ts`" not "the relevant code"
10. **Explain for learning**: state the concept, show the concrete example, explain why it matters — in that order
11. **Verbosity follows context**: short for confirmations, standard for work output, detailed only when explicitly requested or `--verbosity detailed` is passed

## What It Provides

### Output Calibration

Skills use these rules to calibrate every piece of output:

- **Status updates**: 2-3 lines with findings count and top issues; offer full list
- **Decision recommendations**: state recommendation, key factor, trade-off — 3 lines total
- **Concept explanations**: concept statement, concrete code example, why-it-matters — in that order
- **Task completions**: summary line with counts, top-priority items expanded, offer to elaborate

### Anti-Patterns to Avoid

| Anti-Pattern | Correct Approach |
|-------------|-----------------|
| Verbose status narration | Concise finding summary with counts |
| Buried recommendations | Lead with the recommendation |
| Abstract descriptions ("the relevant code") | Concrete references (`src/middleware/auth.ts:47`) |
| Preamble phrases ("I'd be happy to help") | Start directly with the answer |
| Trailing summaries of what was done | End with offer to elaborate or next action |
| Repeating user's question back | Acknowledge briefly, then answer |

## Invoked By

All task skills invoke this skill for tone consistency:

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | always |
| `code-review-repo` | always |
| `code-review-fix` | always |
| `audit` | always |
| `dev-build` | always |
| `dev-refactor` | always |
| `dev-migrate` | always |
| `docs-write` | always |
| `docs-review` | always |
| `docs-repo` | always |
| `docs-crud` | always |
| `docs-confluence` | always |
| `design` | always |
| `plan` | always |
| `spec` | always |
| `research` | always |
| `handoff` | always |
| `coding` | always (for tone consistency) |
