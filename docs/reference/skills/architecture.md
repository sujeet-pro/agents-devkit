---
title: "architecture"
description: Software architecture patterns, principles, and review criteria
skill_name: architecture
category: guideline
workflow_tier: helper
user_invocable: false
---

# architecture

Provides architecture patterns, principles, anti-pattern detection, and review criteria for review, audit, design, and development skills.

## Purpose

Supplies architecture-level review criteria beyond code-level coding guidelines. Covers structural patterns, dependency management, and system design.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--focus` | `frontend`, `backend`, `fullstack`, `infra` | auto-detect | Architecture focus area |

## Core Principles

- Separation of Concerns (SoC)
- Single Responsibility Principle (SRP)
- Dependency Inversion Principle (DIP)
- Interface Segregation
- Least Privilege
- Fail Fast

## Detection

Auto-detects architecture focus from repo signals (frontend frameworks, API directories, infrastructure config).

## Invoked By

`code-review-pr`, `code-review-repo`, `audit`, `design`, `dev-build`, `dev-refactor`.
