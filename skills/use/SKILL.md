---
name: use
description: Use when starting a session to pick the right DevKit skill family, understand related skills, and apply the shared child-agent contract before substantial work
---

<CHILD-AGENT-STOP>
If you were launched as a child agent for a focused task, skip this skill.
</CHILD-AGENT-STOP>

# Using DevKit

## Purpose

DevKit is centered on software-development workflows:

- review workflows that leave comments or review artifacts without mutating the source
- write workflows that directly draft or revise professional engineering documents
- research (quick, standard, deep)
- codebase review and security audit
- diagrams and rendering, with Mermaid, Excalidraw, and draw.io preferred over Graphviz
- source-native publishing to GitHub, Bitbucket, Confluence, and Google Docs
- engineering workflows: ADR, dependency audit, migration guides, changelogs, runbooks
- multi-agent and multi-model execution

## First Decision

Before doing substantial work, always check whether a more specific skill should own the task. If one skill obviously delegates to a more specific sibling, use the more specific skill and inherit its preflight and rules.

## Skill Guide

### Reviewing Others' PRs

- `/devkit:review-code` - Entry router for code review requests. Sends PRs to `review-code-pr`, local changes to `review-code-local`, and repo-wide audits to `review-codebase`.
- `/devkit:review-code-pr` - Reviews a GitHub or Bitbucket PR without editing the branch. Auto-detects fresh vs follow-up review and defaults to interactive mode for fresh reviews. Supports `mode=standard`, `mode=interactive`, `mode=followup` overrides.

### Managing My PRs

- `/devkit:pr-describe` - Generates or refreshes a PR description from the actual diff, risks, and tests.
- `/devkit:pr-fix-comments` - Reads PR comments, applies targeted code fixes, and replies back after verification.
- `/devkit:pr-finalize` - Guides merge, PR, cleanup, and follow-through steps at the end of a branch.

### Other Reviews

- `/devkit:review-code-local` - Reviews staged, unstaged, or branch-local changes, including committed files since branch creation. Outputs a reusable review document instead of auto-fixing.
- `/devkit:review-doc` - Reviews markdown, Confluence, or Google Docs without editing the source. Leaves comments where possible, otherwise emits a review artifact.
- `/devkit:review-codebase` - Reviews an entire repository and produces a prioritized engineering improvement document.
- `/devkit:review-ui` - Structured 6-pillar visual and UX audit of frontend code (layout, typography, color, responsiveness, accessibility, interaction states).
- `/devkit:audit-security` - Runs a security-focused review against auth, data handling, dependencies, and attack surfaces.
- `/devkit:audit-performance` - Reviews performance risks such as latency, bundle size, memory growth, and scaling hotspots.

### Write Skills

- `/devkit:write-doc` - Drafts or directly revises a professional engineering document. Use this when the agent should update the content, not leave comments.
- `/devkit:write-project-docs` - Generates or refreshes professional project documentation from the codebase, including diagrams and setup guidance.
- `/devkit:write-article` - Produces or revises deep engineering articles with exhaustive research and strong technical grounding.
- `/devkit:write-blog` - Produces or revises engineering blog posts, release notes, or technical announcements in a polished narrative format.
- `/devkit:write-api-docs` - Builds or refreshes API reference documentation from code or an OpenAPI spec.
- `/devkit:write-adr` - Creates or updates Architecture Decision Records from code, PRs, or discussion notes.
- `/devkit:write-runbook` - Creates or refreshes operational runbooks for services, deployments, and incident response.
- `/devkit:write-changelog` - Creates or updates changelogs from git history with clean categorization and release-ready formatting.
- `/devkit:write-migration-guide` - Creates or refreshes step-by-step migration guides mapped to real repository files.
- `/devkit:write-onboarding` - Produces or updates onboarding guides for new hires, transfers, or contributors.
- `/devkit:write-tech-radar` - Produces or updates technology radar documents with evidence-backed recommendations.
- `/devkit:write-markdown` - Produces markdown-first deliverables while keeping diagrams and assets organized for later publishing.
- `/devkit:publish-confluence` - Publishes prepared markdown docs and assets to Confluence when writing is already complete.

### Research And Diagram Skills

- `/devkit:research` - Standard software engineering research using official docs, source code, and implementation notes.
- `/devkit:research-quick` - Quick research pass when you need a fast answer or shortlist.
- `/devkit:research-deep` - Exhaustive multi-pass research for high-stakes or broad technical questions.
- `/devkit:diagram` - Chooses the best diagram engine and produces editable source plus renders.
- `/devkit:diagram-mermaid` - Best for text-first diagrams that should diff well in Git.
- `/devkit:diagram-excalidraw` - Best for architecture overviews, ownership maps, and exploratory visuals.
- `/devkit:diagram-drawio` - Best for precise infrastructure, enterprise, or process diagrams.
- `/devkit:diagram-graphviz` - Fallback for existing DOT assets or strict layout needs. Prefer Mermaid, Excalidraw, or draw.io for new docs.
- `/devkit:diagram-convert` - Converts rendered assets when the destination needs PNG, JPEG, or another delivery format.
- `/devkit:design-frontend` - Generates intentional frontend or design-system directions with multiple parallel design passes.

### Project Bootstrapping & Specification

- `/devkit:project-init` - Full project initialization with discovery, research, requirements, constitution, and roadmap.
- `/devkit:spec-write` - Writes formal feature specifications that separate intent from implementation with interactive clarification.
- `/devkit:constitution-write` - Creates or updates a versioned project governance document with non-negotiable principles.
- `/devkit:checklist-generate` - Generates "unit tests for English" that validate requirements quality before implementation.
- `/devkit:spec-analyze` - Cross-artifact consistency checker for specs, plans, tasks, and implementation.

### Development Process

- `/devkit:plan-brainstorm` - Turns rough ideas into sharper approaches with optional party mode and structured voting.
- `/devkit:plan-write` - Converts requirements into execution plans with interactive discussion phase and scope categorization.
- `/devkit:plan-execute` - Executes plans with wave-based parallelism, deviation rules, and inter-wave checkpoints.
- `/devkit:quick-task` - Fast execution for simple tasks without full planning overhead.
- `/devkit:dev-tdd` - Enforces RED-GREEN-REFACTOR loops for feature work and bug fixing.
- `/devkit:dev-debug` - Structured root-cause debugging with persistent state, forensics mode, and interactive hypothesis testing.
- `/devkit:dev-verify` - Evidence-based verification with goal-backward 4-level checks (exists, substantive, wired, data-flowing).
- `/devkit:verify-uat` - Interactive user acceptance testing that extracts testable deliverables and diagnoses failures.
- `/devkit:pr-finalize` - Guides merge, PR, cleanup, and follow-through steps at the end of a branch.
- `/devkit:dev-worktree` - Creates isolated workspaces when multiple branches or tasks need to run in parallel.

### Session & Project Management

- `/devkit:session-handoff` - Pause work and resume in a new session with full context reconstruction.
- `/devkit:context-thread` - Persistent named context threads for ongoing work streams across sessions.
- `/devkit:milestone-manage` - Create, track, audit, and archive development milestones and roadmap progress.
- `/devkit:idea-capture` - Capture forward-looking ideas, manage a backlog parking lot, and promote items to specs or plans.

### Utility Skills

- `/devkit:agent-multi` - Runs the same task through multiple providers or models for comparison or consensus.
- `/devkit:agent-team` - Orchestrates larger tasks across multiple agents with explicit roles.
- `/devkit:cross-review` - Multi-model peer review that synthesizes findings with consensus indicators.
- `/devkit:manage-validate` - Checks that the needed MCP servers are configured before a source-backed workflow.
- `/devkit:manage-skill` - Creates or updates DevKit skills while keeping naming, routing, and contracts consistent.
- `/devkit:manage-update` - Updates DevKit from GitHub or a local filesystem source.
- `/devkit:manage-improve` - Audits and improves the DevKit repository itself.

## Core Rule

If the chosen skill does non-trivial work, apply the child-agent rules from `skills/_references/agentic-teams.md`.

## Intermediary Artifacts

Skills that produce plans, drafts, or research notes should store them in `.temp/<skill-name>/` in the current working directory. Plans use checkbox steps (`- [ ]` / `- [x]`) for resume capability.
