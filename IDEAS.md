# Integration Ideas

Ideas for integrating Claude Code into daily development workflow using claude-devkit skills, agents, and MCP servers.

Each idea includes a brief description, the MCP servers or tools involved, and an implementation sketch.

---

## Table of Contents

- [Communication and Collaboration](#communication-and-collaboration)
- [Code Review and Quality](#code-review-and-quality)
- [Documentation](#documentation)
- [Design and Frontend](#design-and-frontend)
- [DevOps and Infrastructure](#devops-and-infrastructure)
- [Research and Learning](#research-and-learning)
- [Workflow Automation](#workflow-automation)

---

## Communication and Collaboration

### Slack Message Composer

**Status**: Removed (was `/slack-compose`, now handled via Slack MCP directly)

Generate well-crafted Slack messages based on a prompt, with channel/thread context awareness, tone adjustment, and draft-first sending.

```
/slack-compose "Let the team know the v2.1 release is going out today" --channel=engineering --tone=announcement
```

**Tools**: Slack MCP (read_channel, read_thread, send_message)

---

### Standup Summary Generator

Generate daily standup updates by analyzing recent activity and posting to Slack.

**How it works**:
1. Read `git log --since="yesterday"` for the current repo
2. Check open/merged PRs on GitHub or Bitbucket from the last 24 hours
3. Optionally read recent Slack messages in the team channel for context
4. Compose a standup update with: what was done, what is in progress, any blockers
5. Post to Slack as a draft for review

**Tools**: Git (Bash), GitHub CLI or Bitbucket MCP, Slack MCP

**Example output**:
```
Yesterday:
- Merged PR #42: Add pagination to user list endpoint
- Reviewed PR #38: Refactor auth middleware

Today:
- Continue work on caching layer for product search
- Address review comments on PR #45

Blockers:
- Waiting on API team for the updated schema for order events
```

---

### Meeting Notes Processor

Take raw, unstructured meeting notes and transform them into structured documents with action items.

**How it works**:
1. Accept raw text (pasted in chat or from a file)
2. Identify: decisions made, action items (with owners and deadlines), key discussion points, open questions
3. Structure into a clean document
4. Post to Confluence as a meeting notes page
5. Optionally post action items to Slack, tagging the responsible people

**Tools**: Confluence MCP (create_page), Slack MCP (send_message), WebSearch (for context on discussed topics)

---

### Email Composer

Generate professional emails based on context and intent, with the ability to save as Gmail drafts.

**How it works**:
1. Accept a prompt describing the email purpose and recipient context
2. Optionally read previous email threads for context
3. Compose the email with appropriate tone and structure
4. Save as a Gmail draft for review before sending

**Tools**: Gmail MCP (search_messages, read_thread, create_draft)

---

### Slack Thread Summarizer

Summarize long Slack threads into key decisions, action items, and open questions.

**How it works**:
1. Read the full thread using the Slack MCP
2. Identify: the original question/topic, key discussion points, decisions reached, action items, unresolved questions
3. Compose a summary and post it as a thread reply
4. Optionally cross-post the summary to a different channel

**Tools**: Slack MCP (read_thread, send_message, search_channels)

---

## Code Review and Quality

### Automated PR Labels

Automatically label PRs based on the files changed (frontend, backend, infrastructure, documentation, tests).

**How it works**:
1. Fetch the PR diff (files changed)
2. Classify files by area:
   - `src/components/`, `app/`, `pages/` -> `frontend`
   - `src/api/`, `src/services/`, `*.java`, `*.py` -> `backend`
   - `terraform/`, `docker-compose.yml`, `.github/workflows/` -> `infrastructure`
   - `docs/`, `*.md`, `CHANGELOG.md` -> `documentation`
   - `*.test.*`, `*.spec.*`, `__tests__/` -> `tests`
3. Apply labels via GitHub CLI or Bitbucket API
4. Add a size label based on lines changed (XS, S, M, L, XL)

**Tools**: GitHub CLI (Bash) or Bitbucket MCP (getPullRequestDiff, updatePullRequest)

---

### PR Summary Generator

Generate detailed PR descriptions from commit history and diff analysis.

**How it works**:
1. Read all commits in the branch
2. Analyze the full diff
3. Generate a structured PR description:
   - Summary of changes (1-3 bullet points)
   - Detailed breakdown by area (frontend, backend, tests, config)
   - Breaking changes (if any)
   - Testing notes
   - Reviewer checklist
4. Update the PR description

**Tools**: GitHub CLI or Bitbucket MCP, Git (Bash)

---

### Dependency Audit

Check for outdated or vulnerable dependencies and generate upgrade recommendations.

**How it works**:
1. Read `package.json`/`requirements.txt`/`pom.xml` and lockfiles
2. Check each dependency for:
   - Known vulnerabilities (via WebSearch or npm audit)
   - Available updates (major, minor, patch)
   - Changelog highlights for available updates
3. Generate a report grouped by severity (critical vulnerabilities, major updates, minor updates)
4. Optionally create a PR with the recommended updates

**Tools**: Bash (npm audit, pip-audit), WebSearch, WebFetch, GitHub CLI or Bitbucket MCP

---

### Code Complexity Reporter

Analyze code complexity trends across the codebase over time.

**How it works**:
1. Run static analysis tools (eslint with complexity rules, radon for Python, etc.)
2. Identify the most complex functions/methods (by cyclomatic complexity, cognitive complexity)
3. Compare against previous snapshots (if available) to show trends
4. Generate a report with:
   - Top 10 most complex functions
   - Newly added complexity (in recent PRs)
   - Recommendations for refactoring
5. Post to Confluence or save as markdown

**Tools**: Bash (eslint, radon, etc.), Confluence MCP or local file system

---

### Test Coverage Analyzer

Identify untested critical paths and generate test suggestions.

**How it works**:
1. Run test coverage tools (jest --coverage, pytest --cov, jacoco)
2. Parse coverage reports to identify uncovered files and functions
3. Cross-reference with git log to find frequently changed but untested files
4. For each untested critical path, generate test scaffolding with:
   - Test file creation
   - Describe/it blocks for key behaviors
   - Mock setup for dependencies
5. Output as a prioritized list with generated test stubs

**Tools**: Bash (test runners), Read (coverage reports), Write (test files)

---

## Documentation

### API Documentation Generator

Generate OpenAPI specs or API documentation from code analysis.

**How it works**:
1. Scan route handlers/controllers for endpoint definitions
2. Analyze request/response types from TypeScript types, Java DTOs, or Python models
3. Generate an OpenAPI 3.0 spec with:
   - Path definitions
   - Request/response schemas
   - Authentication requirements
   - Example payloads
4. Output as YAML/JSON file or publish to Confluence

**Tools**: Glob, Grep, Read (code analysis), Write (spec output), Confluence MCP

---

### Architecture Decision Records

Generate ADRs from PR discussions and code decisions.

**How it works**:
1. Analyze a PR's discussion (comments, review threads, description)
2. Identify architectural decisions: technology choices, pattern selections, trade-off discussions
3. Generate an ADR following the standard template:
   - Title, Status, Context, Decision, Consequences
4. Save to the project's `docs/adr/` directory or post to Confluence

**Tools**: GitHub CLI or Bitbucket MCP (PR comments), Confluence MCP, Write

---

### Runbook Generator

Create operational runbooks from code analysis and incident history.

**How it works**:
1. Analyze the application code for:
   - Entry points and deployment configuration
   - Database connections and migration setup
   - External service dependencies
   - Error handling and logging patterns
   - Health check endpoints
2. Cross-reference with any documented incidents (Confluence, Slack history)
3. Generate a runbook with:
   - Service overview and architecture
   - Deployment steps
   - Health check commands
   - Common failure modes and remediation steps
   - Escalation contacts and procedures
4. Post to Confluence

**Tools**: Read, Grep, Glob (code analysis), Confluence MCP (search, create_page), Slack MCP (search)

---

### Changelog Automation

Generate changelogs from PR titles and conventional commits.

**How it works**:
1. Read all merged PRs and commits since the last release tag
2. Parse conventional commit prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `perf:`, `test:`)
3. Group changes by category
4. Generate a markdown changelog with:
   - Version header with date
   - Categorized list of changes with PR links
   - Breaking changes highlighted at the top
   - Contributors list
5. Prepend to `CHANGELOG.md` or post to Confluence

**Tools**: Git (Bash), GitHub CLI or Bitbucket MCP, Write

---

### Knowledge Base Builder

Extract tribal knowledge from Slack and Confluence into structured documentation.

**How it works**:
1. Search Slack for frequently asked questions (channels with support/help topics)
2. Search Confluence for related but fragmented documentation
3. Identify recurring patterns: the same question asked multiple times, the same person answering
4. Synthesize into a structured FAQ or knowledge base article
5. Publish to Confluence with proper categorization and linking

**Tools**: Slack MCP (search_public, read_thread), Confluence MCP (search, create_page)

---

## Design and Frontend

### Design Token Sync

Synchronize design tokens from Figma through code to documentation.

**How it works**:
1. Read token definitions from the source (Figma API when available, or a tokens JSON file)
2. Generate code output:
   - CSS custom properties file
   - TypeScript constants file
   - Tailwind theme configuration
3. Generate documentation:
   - Token reference table with visual swatches
   - Usage guidelines
4. Verify that all components reference tokens (no hardcoded values)

**Tools**: WebFetch (Figma API), Read/Write (code generation), Confluence MCP (documentation)

---

### Component Documentation

Generate Storybook stories and documentation from component source code.

**How it works**:
1. Read component files and extract: props interface, default values, variants, usage patterns
2. Generate Storybook stories covering:
   - Default state
   - All prop variants
   - Interactive controls
   - Composition examples
3. Generate a documentation page with:
   - Props table
   - Usage examples
   - Accessibility notes
   - Do's and Don'ts

**Tools**: Read, Grep (code analysis), Write (story files)

---

### Visual Regression Reporter

Analyze visual regression test results and generate a human-readable summary.

**How it works**:
1. Read visual regression test output (Chromatic, Percy, BackstopJS, or similar)
2. Identify changed components and classify changes:
   - Intentional (matches PR scope)
   - Unintentional (side effects)
   - Broken (layout shifts, missing elements)
3. Generate a summary report with screenshots and descriptions
4. Post as a PR comment

**Tools**: Read (test output), GitHub CLI or Bitbucket MCP (PR comments)

---

### Accessibility Audit

Run accessibility analysis and generate a remediation plan with code fixes.

**How it works**:
1. Run axe-core or Lighthouse accessibility audit on target pages
2. Parse results and group by severity and WCAG criterion
3. For each issue, analyze the source code to identify the exact element
4. Generate code fixes:
   - Add missing ARIA attributes
   - Fix color contrast values
   - Add keyboard event handlers
   - Fix heading hierarchy
5. Output as a prioritized remediation plan with PR-ready code patches

**Tools**: Bash (Lighthouse CLI, axe-core), Read (source code), Write (fixes)

---

### Performance Budget Monitor

Track bundle sizes and generate optimization suggestions.

**How it works**:
1. Run `next build` or `webpack --profile --json` to get bundle analysis
2. Compare against defined budgets (per-page, per-chunk, total)
3. Identify the largest contributors to bundle size
4. For over-budget chunks, suggest:
   - Code splitting opportunities
   - Lighter dependency alternatives
   - Dynamic import candidates
   - Dead code to remove
5. Post report as a PR comment or Confluence page

**Tools**: Bash (build tools), Read (analysis output), GitHub CLI or Bitbucket MCP

---

## DevOps and Infrastructure

### Pipeline Monitor

Watch CI/CD pipelines and provide root cause analysis on failures.

**How it works**:
1. Check pipeline status (Bitbucket Pipelines, GitHub Actions)
2. On failure, fetch step logs
3. Analyze logs to identify:
   - The failing step
   - The root cause (test failure, build error, timeout, infra issue)
   - Whether this is a flaky failure (same test failed before and passed on retry)
4. Post a summary to Slack with the failure analysis and suggested fix

**Tools**: Bitbucket MCP (getPipelineRun, getPipelineStepLogs) or GitHub CLI, Slack MCP

---

### Infrastructure Cost Analyzer

Review cloud configuration and suggest cost optimizations.

**How it works**:
1. Read infrastructure-as-code files (Terraform, CloudFormation, Docker Compose)
2. Analyze resource configurations:
   - Over-provisioned instances
   - Missing auto-scaling
   - Unused resources
   - Expensive storage configurations
3. Research current pricing with WebSearch
4. Generate a cost optimization report with estimated savings
5. Post to Confluence

**Tools**: Read, Grep (IaC analysis), WebSearch (pricing), Confluence MCP

---

### Deployment Notes Generator

Generate deployment notes from unreleased changes.

**How it works**:
1. Identify all changes since the last deployment tag
2. Classify changes by risk level:
   - Database migrations (high risk)
   - API changes (medium risk)
   - Config changes (medium risk)
   - Feature additions (low risk)
   - Bug fixes (low risk)
3. Generate deployment notes with:
   - Pre-deployment checklist
   - Migration steps
   - Feature flag requirements
   - Rollback plan
   - Verification steps
4. Post to Confluence and Slack

**Tools**: Git (Bash), Read (migration files, config), Confluence MCP, Slack MCP

---

### Feature Flag Manager

Track feature flags, identify stale flags, and suggest cleanup.

**How it works**:
1. Search codebase for feature flag patterns (LaunchDarkly, Unleash, custom implementations)
2. Cross-reference with flag management system (via API)
3. Identify:
   - Flags that have been enabled for all users for > 30 days (candidates for removal)
   - Flags referenced in code but not in the flag system (orphaned references)
   - Flags in the system but not in code (unused flags)
4. Generate cleanup PRs that remove dead flag code paths

**Tools**: Grep, Glob (code search), WebFetch (flag management API), Write (cleanup code)

---

### Log Analyzer

Parse application logs and identify patterns, anomalies, and recurring errors.

**How it works**:
1. Accept log files or log search queries
2. Parse and categorize log entries
3. Identify patterns:
   - Most frequent errors
   - Error rate spikes
   - Slow request patterns
   - Unusual error messages (new errors not seen before)
4. Correlate with recent deployments or code changes
5. Generate an analysis report with recommendations

**Tools**: Read (log files), Bash (log parsing), WebSearch (error messages), Write (report)

---

## Research and Learning

### Tech Radar Generator

Research emerging technologies and generate tech radar updates.

**How it works**:
1. Accept a list of technology areas to evaluate (frontend frameworks, databases, CI/CD tools, etc.)
2. Research each technology:
   - Current adoption trends
   - Community activity (GitHub stars, npm downloads, Stack Overflow questions)
   - Maturity and stability
   - Comparison with alternatives
3. Classify into radar rings: Adopt, Trial, Assess, Hold
4. Generate a tech radar document with rationale for each placement
5. Post to Confluence

**Tools**: WebSearch, WebFetch, Multi MCP (compare perspectives), Confluence MCP

---

### Library Comparison

Compare npm/Python packages for a specific use case with objective analysis.

**How it works**:
1. Accept a use case and candidate libraries
2. Research each library:
   - Bundle size (bundlephobia)
   - Download trends (npm trends)
   - GitHub activity (issues, PRs, releases, contributors)
   - TypeScript support
   - API ergonomics (code examples)
   - Performance benchmarks (if available)
3. Generate a comparison table with a recommendation
4. Optionally use Multi MCP to get multiple model perspectives

**Tools**: WebSearch, WebFetch, Multi MCP (compare), Write (report)

---

### Migration Guide Generator

Generate step-by-step migration guides for framework or library upgrades.

**How it works**:
1. Accept the source and target versions (e.g., React 18 to 19, Next.js 13 to 14)
2. Research:
   - Official migration guide
   - Breaking changes
   - New features and deprecations
   - Community-reported issues
3. Analyze the current codebase for affected patterns
4. Generate a migration guide with:
   - Pre-migration checklist
   - Step-by-step instructions mapped to the codebase
   - Code transformation examples (before/after)
   - Testing checklist
   - Known issues and workarounds
5. Post to Confluence or save as markdown

**Tools**: WebSearch, WebFetch, Grep, Glob (codebase analysis), Confluence MCP or Write

---

### Best Practice Aggregator

Compile best practices from official documentation, conference talks, and expert blog posts.

**How it works**:
1. Accept a topic (e.g., "React Server Components best practices", "PostgreSQL query optimization")
2. Search for:
   - Official documentation and guides
   - Conference talks and workshops (YouTube, conference sites)
   - Expert blog posts (from known authors in the field)
   - GitHub discussions and RFCs
3. Synthesize into a structured document:
   - Core principles
   - Do's and Don'ts with code examples
   - Common anti-patterns
   - References and further reading
4. Post to Confluence or save locally

**Tools**: WebSearch, WebFetch, Research Agent, Confluence MCP or Write

---

## Workflow Automation

### Sprint Planner

Analyze backlog items and suggest sprint compositions based on team capacity and priorities.

**How it works**:
1. Read backlog items (from a project management tool or a structured document)
2. Analyze each item for:
   - Estimated complexity (based on description and historical data)
   - Dependencies on other items
   - Risk factors
3. Given team capacity and sprint duration, suggest:
   - Sprint composition (which items to include)
   - Task ordering (considering dependencies)
   - Risk mitigation for high-risk items
4. Output as a sprint plan document

**Tools**: Confluence MCP (read backlog), WebSearch (context), Write (sprint plan)

---

### Incident Commander

Guide through incident response with automated communication and timeline tracking.

**How it works**:
1. Accept incident description and severity
2. Generate and post initial incident communication to Slack (impacted services, initial assessment, point of contact)
3. Track timeline of events as the user reports them
4. Generate periodic status updates for stakeholders
5. After resolution, compile:
   - Full incident timeline
   - Root cause analysis template
   - Action items
   - Post-mortem document
6. Post to Confluence as a post-mortem

**Tools**: Slack MCP (send_message, schedule_message), Confluence MCP (create_page), Google Calendar MCP (create follow-up meeting)

---

### Release Manager

Orchestrate the full release process from changelog to deployment notification.

**How it works**:
1. Determine the release version (from conventional commits or user input)
2. Generate changelog from merged PRs and commits since last release
3. Bump version in package.json/pom.xml/pyproject.toml
4. Create a release tag and GitHub Release / Bitbucket tag
5. Generate deployment notes
6. Post release announcement to Slack
7. Update Confluence release tracking page

**Tools**: Git (Bash), GitHub CLI or Bitbucket MCP, Slack MCP, Confluence MCP, Write

---

### Onboarding Guide Generator

Generate repository-specific onboarding documentation for new team members.

**How it works**:
1. Analyze the repository:
   - Tech stack (languages, frameworks, tools)
   - Project structure and conventions
   - Build and test commands
   - Environment setup (env vars, databases, external services)
   - Key architectural decisions
   - Common workflows (branching strategy, PR process, deployment)
2. Read existing documentation (README, Confluence, code comments)
3. Generate a comprehensive onboarding guide:
   - Environment setup (step-by-step)
   - Architecture overview with diagrams
   - Key concepts and domain terminology
   - Common tasks and how to do them
   - Who to ask for what (team directory)
   - Links to important resources
4. Post to Confluence or save as markdown in the repo

**Tools**: Read, Grep, Glob (repo analysis), Diagram skill (architecture), Confluence MCP or Write
