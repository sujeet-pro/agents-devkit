---
name: write-changelog
description: Use when you need to draft or directly revise a professional changelog from git history with categorization, release formatting, and clear breaking-change summaries
user_invocable: true
arguments:
  - name: since
    description: "Starting point: a git tag, commit SHA, or date (e.g., 'v1.2.0', 'abc1234', '2024-01-01')"
    required: true
  - name: format
    description: "Output format: markdown, github-release, confluence (default: markdown)"
    required: false
---

# Changelog

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should improve the changelog directly. If you only want a comment-only review, use `/devkit:review-doc`.

## Preflight

Before reading git history or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-changelog`

Verify that the repository is a git repository and that the `since` reference (tag, commit, or date) resolves to a valid git object.

## Required Child Agents

Run at least these child agents in parallel:

- Commit analyzer
- Categorizer
- Writer

## Output

Produce a professional changelog with clear release sections, breaking changes, and user-facing summaries.
