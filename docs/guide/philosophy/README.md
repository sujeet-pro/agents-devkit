---
title: Philosophy & Design
description: Core principles, output style, and token-efficient lazy loading
order: 2
---

# Philosophy & Design

## Core Principles

- **Human-in-the-loop** — decisions happen interactively, execution happens automatically
- **Plan first, then implement** — every non-trivial task follows a 6-phase workflow with approval gates
- **Concise by default** — output is compact and decision-oriented; show the short version first, then offer to elaborate if the user needs more detail
- **Self-sufficient skills** — every skill works independently with inline fallbacks for shared knowledge; can invoke other skills when available
- **Parallel agentic teams** — non-trivial work uses child agents with distinct roles
- **Principal engineer lens** — do we need this? What's the simplest version? What are the alternatives?
- **Lazy loading** — only the relevant skill, stage, and reference files load per task; ~200-500 lines per invocation out of ~42,000 total
- **Markdown by default** — all outputs are markdown unless the user requests otherwise
- **Auto mode** — pass `--auto` to skip confirmations and execute the full workflow automatically
- **Dual-install support** — works as a Claude plugin (`/adk:skill`), via skills.sh (`/adk-skill`), or Codex (`/adk-skill`)

## Output Style

All ADK output follows **concise by default**:

- **Lead with the conclusion**, then supporting reasoning
- **Short version first** — after completing a task, show the compact result
- **Offer to elaborate** — end with "Need a detailed breakdown?" when the output could be expanded
- **No preamble** — skip "Great question!", "I'd be happy to help", "Let me think about this..."
- **No trailing summaries** — don't restate what was just done
- **Verbosity flag** — pass `--verbosity detailed` to get full output without asking, or `--verbosity short` for one-liners

## Token-Efficient Lazy Loading

ADK never loads all 42,000 lines at once. Each task loads only what it needs:

| What Loads | Lines | When |
|------------|------:|------|
| **Primary skill** | ~100-300 | Always — the SKILL.md for the task at hand |
| **Conditional stages** | ~50-150 | Only the stage matching the detected mode (e.g., `debug` vs `implement` vs `tdd`) |
| **Conditional references** | ~50-200 | Only the guidelines matching the detected stack (e.g., Python backend, not all 16 coding guideline files) |
| **Guideline skills** | ~50-100 each | On demand — skipped if not installed (inline fallback summaries are ~1 line each) |

### Real-World Examples

- A typical PR review loads **~400 lines**
- A Mermaid diagram loads **~250 lines** (1 type reference out of 21)
- A full-stack feature implementation loads **~600 lines** across multiple skills
- The remaining **~41,000 lines stay on disk**

## At a Glance

| What | Count | Details |
|------|------:|---------|
| **Skills** | 49 | 28 task, 16 guideline/helper, 5 routing/orchestrator |
| **Agents** | 15 | Reusable child-agent definitions for parallel work |
| **Reference files** | 251 | Including 16 coding guidelines and 24 doc-writing guidelines |
| **Stage files** | 58 | Conditional stages loaded per mode/context |
| **Scripts** | 67 | Preflight checks, setup, and platform connectors |
| **Total instructions** | ~42,000 lines | But only ~200-500 lines load per task |
