---
name: create-skill
description: Create new claude-devkit skills with iterative quality loops, proper agent delegation, and guideline compliance built in
user_invocable: true
arguments:
  - name: name
    description: "Skill name (kebab-case, e.g. 'deploy-preview')"
    required: true
  - name: description
    description: "Brief description of what the skill does"
    required: true
  - name: type
    description: "Skill type: code, document, review, automation, integration (default: automation)"
    required: false
---

# Skill Creator

Create new claude-devkit skills that follow the devkit's architecture patterns: phased workflows, iterative quality loops, agent delegation, and guideline compliance. This skill extends the Anthropic skill-creator pattern with devkit-specific conventions.

## Agent & Skill Delegation

| Task | Delegate To |
|------|-------------|
| Research (existing patterns) | `/research` skill → **research-agent** |
| Diagram (architecture/flow) | `/diagram` skill → **diagram-agent** |

---

## Phase 1: Research & Plan

### 1a. Understand the request

From the `name`, `description`, and `type` arguments, determine:
- What the skill needs to accomplish
- Which existing devkit skills are most similar (for pattern reference)
- What tools and MCP servers the skill will need
- Whether it needs new agents or can reuse existing ones

### 1b. Research existing patterns

Read the following devkit skills for pattern reference based on `type`:

| Type | Reference Skills to Read |
|------|-------------------------|
| `code` | `self-review/SKILL.md`, `pr-review/SKILL.md` |
| `document` | `blog/SKILL.md`, `article/SKILL.md`, `doc-write/SKILL.md` |
| `review` | `doc-review/SKILL.md`, `pr-review/SKILL.md` |
| `automation` | `self-review/SKILL.md`, `pr-describe/SKILL.md` |
| `integration` | `confluence-publish/SKILL.md`, `slack-compose/SKILL.md` |

Read 2-3 reference skills to understand the patterns.

### 1c. Check for similar community skills

Optionally search for existing community skills that do something similar:
- Check `~/.claude/skills/` for already-installed skills
- Use `/research --depth=quick` to search for prior art

### 1d. Present plan

Show the user:

```
## Skill Plan: <name>

**Type**: <type>
**Description**: <description>

### Phases
1. <Phase 1 name> — <what it does>
2. <Phase 2 name> — <what it does>
...
N. Iterative Quality Loop — verify and fix output

### Tools needed
- <tool list>

### Agent delegation
- <which existing agents to reuse>
- <any new agents needed>

### Guidelines
- <which guideline categories apply>

Proceed? (yes / adjust)
```

Wait for user approval.

---

## Phase 2: Generate SKILL.md

Create the skill file at `skills/<name>/SKILL.md` following these mandatory patterns:

### 2a. Frontmatter

```yaml
---
name: <name>
description: <description>
user_invocable: true
arguments:
  - name: <arg1>
    description: "<description>"
    required: <true/false>
  ...
---
```

### 2b. Required sections

Every skill MUST include these sections:

**1. Title and description** — What the skill does and when to use it.

**2. Agent & Skill Delegation table** — Always use devkit agents/skills:

```markdown
## Agent & Skill Delegation

**Always use the devkit's own agents and skills:**

| Task | Delegate To |
|------|-------------|
| Research | `/research` skill → **research-agent** |
| Code blocks | **code-snippet-agent** |
| Diagrams | `/diagram` skill → **diagram-agent** |
```

**3. Phased workflow** — Break the skill into numbered phases. Each phase has a clear purpose and output.

**4. Repo-level guideline discovery** (for document and review types):

```markdown
**Repo-level guideline discovery** (highest priority — overrides devkit guidelines):

| Category | Paths to Check (in priority order) |
|----------|-----------------------------------|
| **Document guidelines** | `docs/guidelines/document/`, `guidelines/document/`, `.github/guidelines/`, `CLAUDE.md` (section: `## Document Guidelines`) |
| **Coding guidelines** | `docs/guidelines/coding/`, `guidelines/coding/`, `coding-guidelines/`, `CLAUDE.md` (section: `## Coding Guidelines`) |
| **Markdown conventions** | `.markdown-guidelines.md`, `MARKDOWN.md`, `docs/markdown-style.md` |

Repo-level guidelines take **higher priority** than devkit guidelines.
```

**5. Iterative Quality Loop** (MANDATORY for all skills):

```markdown
### <Phase N> — Iterative Quality Loop

Run an iterative review-fix cycle. **Max <2-3> iterations.**

\```
iteration = 0
max_iterations = <2-3>

while iteration < max_iterations:
    iteration += 1
    issues = verify_output()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break  # stuck — stop
\```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| <check 1> | CRITICAL | <action> |
| <check 2> | WARNING | <action> |
...

**Convergence rules:**

| Condition | Action |
|-----------|--------|
| No CRITICAL or WARNING issues remain | **Done** |
| `iteration >= max_iterations` | **Max reached** — report remaining |
| No fixes applied this iteration | **Stuck** — needs human decision |
| Same issue reappears after fix | **Stuck** — stop and report |
```

**6. CLI tool preferences** (for skills that use Bash):

```markdown
## CLI Tool Preferences

- `fd` instead of `find` for file searching
- `rg` (ripgrep) instead of `grep` for text searching
- `bat` instead of `cat` for file viewing
- `jq` for JSON processing
- `gh` for GitHub operations
```

### 2c. Type-specific patterns

**For `code` type skills:**
- Include validation command detection (same pattern as `/self-review` Phase 1b)
- Include lint/test/build loop
- Support `fix` mode (prompt/auto/dry-run)

**For `document` type skills:**
- Include mode support (write/review/update)
- Include diagram requirements with minimum counts
- Include research delegation

**For `review` type skills:**
- Include finding quality verification loop
- Include confidence threshold
- Include interactive approval (post/skip/pick/edit/done/abort)

**For `automation` type skills:**
- Include VCS platform detection (GitHub/Bitbucket)
- Include idempotency (safe to run multiple times)

**For `integration` type skills:**
- Include MCP server connectivity check
- Include fallback behavior if MCP server is unavailable

---

## Phase 3: Generate Supporting Files (if needed)

If the skill needs a new agent:

1. Create `agents/<agent-name>.md` with:
   - Frontmatter: name, description, `model: opus`, tools list
   - System instructions
   - CLI tool preferences
   - Output format specification

2. Update `CLAUDE.md` project structure to include the new agent.

---

## Phase 4: Iterative Quality Loop

Verify the generated skill against devkit conventions. **Max 3 iterations.**

```
iteration = 0
max_iterations = 3

while iteration < max_iterations:
    iteration += 1
    issues = verify_skill()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break
```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| Frontmatter has name, description, user_invocable, arguments | CRITICAL | Add missing fields |
| Agent & Skill Delegation table is present | CRITICAL | Add delegation table |
| Iterative Quality Loop section is present | CRITICAL | Add loop section |
| Convergence rules are defined | CRITICAL | Add convergence rules |
| Phases are numbered and sequential | WARNING | Fix numbering |
| CLI tool preferences use modern tools (fd, rg, bat) | WARNING | Replace legacy tools |
| Guideline discovery section exists (for doc/review types) | WARNING | Add discovery section |
| All referenced agents exist in `agents/` | WARNING | Create missing agents |
| Diagram requirements specified (for doc types) | WARNING | Add diagram section |
| Skill follows the same structure as reference skills | INFO | Restructure |

**Convergence rules:** Same as other skills — max 3 iterations, stuck detection.

---

## Phase 5: Update Devkit

After the skill is created:

1. Add the skill to `CLAUDE.md` project structure
2. Add the skill to `README.md` skills table with command and description
3. Add examples to the README examples section
4. If a new agent was created, add it to the agents table in README

---

## Phase 6: Test Plan

Present a test plan to the user:

```
## Test Plan for /<name>

1. Install: `zsh install.zsh`
2. Open a test project and invoke: `/<name> <example args>`
3. Verify:
   - [ ] Skill triggers correctly
   - [ ] All phases execute in order
   - [ ] Quality loop runs and catches issues
   - [ ] Agent delegation works
   - [ ] Output format is correct
   - [ ] Guideline loading works
```

---

## Rules

1. **Follow devkit conventions exactly.** Match the structure, naming, and patterns of existing skills.
2. **Every skill gets a quality loop.** No exceptions. The loop ensures output quality.
3. **Delegate to existing agents.** Don't create new agents when existing ones suffice.
4. **Use modern CLI tools.** Never use `find`, `grep`, or `cat` when `fd`, `rg`, and `bat` are available.
5. **Include convergence detection.** Every loop must have max iterations and stuck detection.
6. **Support repo-level guidelines.** Document and review skills must discover and prioritize repo guidelines.
