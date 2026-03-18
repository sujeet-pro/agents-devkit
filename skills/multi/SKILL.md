---
name: multi
description: "Multi-model mode: run any task through multiple AI CLIs in parallel and merge results via Opus consensus"
user_invocable: true
arguments:
  - name: task
    description: "The task description or skill command to run multi-model (e.g., '/pr-review 42', 'research kubernetes networking')"
    required: true
  - name: models
    description: "Comma-separated model names to use (default: all detected). Use 'list' to show available models."
    required: false
  - name: strategy
    description: "Consensus strategy: merge (default), vote, best-of"
    required: false
  - name: timeout
    description: "Timeout per model in seconds (default: auto based on task type)"
    required: false
---

# Multi-Model Skill

Run any task through multiple AI models in parallel, then use Claude Opus as the consensus engine to synthesize the best result. Works as a standalone skill or as a `--multi` flag on any other skill.

## Activation Patterns

This skill activates when:
- User invokes `/multi <task>`
- User adds `--multi` flag to any skill: `/pr-review 42 --multi`
- User says "multi-model", "use multiple models", "get a second opinion", "compare model outputs"

## Agent & Skill Delegation

| Task | Delegate To |
|------|-------------|
| Consensus synthesis | **consensus-agent** (Opus) |
| Model detection | `scripts/detect-models.zsh` |
| Context assembly | `scripts/assemble-context.zsh` |
| Parallel execution | `scripts/run-models.zsh` |

---

## Phase 1: Detection & Planning

### 1a. Detect available models

Run the detection script:

```bash
zsh ~/.claude/scripts/detect-models.zsh
```

Parse the JSON output. If `multi_model_available` is `false` (fewer than 2 models):

> Multi-model mode requires at least 2 AI CLI tools installed.
> Currently available: [list installed CLIs]
>
> Install additional CLI tools:
> - `codex` — OpenAI Codex CLI
> - `gemini` — Google Gemini CLI
> - `cursor-cli` — Cursor CLI (supports GPT and Gemini models)

If `$ARGUMENTS.models` is `list`, display the available models table and **stop**.

### 1b. Select models

If `$ARGUMENTS.models` is specified (e.g., `claude,codex`), filter the detected models to only those requested. Warn if a requested model is not installed.

Otherwise, use ALL available models.

### 1c. Parse the task

Determine what the user wants to run:

| Pattern | Interpretation |
|---------|---------------|
| Starts with `/` (e.g., `/pr-review 42`) | Skill invocation — extract skill name and args |
| Freeform text | General task prompt |
| Contains `--multi` in another skill's args | Strip `--multi` flag, use remaining as task |

### 1d. Determine timeout

| Task / Skill | Timeout |
|------|---------|
| `/research --depth=exhaustive` | 15 min (900s) |
| `/research --depth=standard` | 10 min (600s) |
| `/article` | 10 min (600s) |
| `/project-docs --depth=comprehensive` | 10 min (600s) |
| All other tasks | 5 min (300s) |

Override with `$ARGUMENTS.timeout` if specified.

### 1e. Present execution plan

Show the user:

```
Multi-Model Execution Plan

Task: [task description]
Models: [list of models]
Strategy: [merge/vote/best-of]
Timeout: [N] seconds per model
Output: .temp/multi/<run-id>/

Proceed?
```

Wait for user confirmation.

---

## Phase 2: Context Assembly

### 2a. Gather context

**For skill invocations** (`/pr-review`, `/research`, etc.):
1. Read the skill's `SKILL.md` from `~/.claude/skills/<name>/SKILL.md`
2. Detect applicable guidelines (general + repo-type-specific from `~/.claude/guidelines/`)
3. Read the project's `CLAUDE.md` if present in the current directory
4. Read any files referenced in the task arguments

**For freeform tasks**:
1. Read the project's `CLAUDE.md` if present
2. Include any files or context referenced in the task

### 2b. Assemble the prompt

```bash
WORK_DIR="$PWD/.temp/multi/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$WORK_DIR"

zsh ~/.claude/scripts/assemble-context.zsh \
  --task "$TASK" \
  --skill "$SKILL_NAME" \
  --guideline "$GUIDELINE_PATH_1" \
  --guideline "$GUIDELINE_PATH_2" \
  --claude-md "$PWD/CLAUDE.md" \
  > "$WORK_DIR/prompt.md"
```

The prompt must be **fully self-contained** — external CLIs cannot access the devkit's agent system, tool use, or file reading. All context must be in the prompt itself.

### 2c. Verify prompt size

Check the assembled prompt size. If it exceeds 100KB:
1. Truncate guidelines (keep general, drop type-specific)
2. Summarize CLAUDE.md instead of including full text
3. Warn the user about truncated context

---

## Phase 3: Parallel Execution

### 3a. Run all models

```bash
MODELS_JSON='[...filtered model array from Phase 1...]'

zsh ~/.claude/scripts/run-models.zsh \
  --prompt-file "$WORK_DIR/prompt.md" \
  --output-dir "$WORK_DIR" \
  --models "$MODELS_JSON" \
  --timeout "$TIMEOUT"
```

### 3b. Report progress

After execution completes, display results:

```
Execution Results

| Model | Status | Duration |
|-------|--------|----------|
| claude-opus | Success | 45s |
| codex | Success | 62s |
| cursor-gpt | Timeout | 300s |
```

If fewer than 2 models succeeded, offer to:
- Proceed with available outputs
- Retry failed models
- Cancel and fall back to Claude-only

### 3c. Read all outputs

For each successful model, read the output file from `$WORK_DIR/<model-name>.md`.

---

## Phase 4: Consensus (Opus as Merge Engine)

Spawn the **consensus-agent** with all model outputs and the original task.

The consensus strategy depends on `$ARGUMENTS.strategy` (default: `merge`):

### Strategy: merge (default)

The consensus-agent reads all outputs and creates a unified result:

1. **Agreement** (high confidence) — points where all models agree
2. **Synthesized** (medium confidence) — best version from partial agreement
3. **Divergent views** — genuine disagreements with analysis
4. **Unique insights** — single-source findings flagged for verification

The merged output includes provenance annotations:

```markdown
## [Section]

[Content agreed by all models]

> **Note**: codex disagreed, arguing [alternative]. Consensus favored
> [chosen view] because [reasoning].

> **Single-source** (claude only): [content]. Verify independently.
```

### Strategy: vote

For discrete decisions (yes/no, option A vs B):
1. Collect each model's answer
2. Present tally
3. Go with majority, noting dissent

### Strategy: best-of

Opus evaluates all outputs and picks the single best one:

```
| Model | Strengths | Weaknesses | Score |
|-------|-----------|------------|-------|
| claude-opus | ... | ... | 8/10 |
| codex | ... | ... | 7/10 |

Selected: claude-opus — [reasoning]
```

---

## Phase 5: Output & Cleanup

### 5a. Present the consensus result

Display the merged/selected output in the conversation.

### 5b. Save consensus

Write the consensus result to `$WORK_DIR/consensus.md`.

### 5c. Offer follow-up actions

> Multi-model consensus complete. Options:
> - **View individual outputs** from each model
> - **Drill deeper** on a specific section
> - **Re-run** with different models or strategy
> - **Save** consensus to a file
> - **Post** results (if this was a PR review, post comments)

---

## Phase 6: Iterative Quality Loop

**Max 2 iterations.**

```
iteration = 0
max_iterations = 2

while iteration < max_iterations:
    iteration += 1
    issues = verify_consensus()
    if no CRITICAL or WARNING issues: break
    fix(issues)
    if no fixes applied this iteration: break
```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| All successful model outputs were read | CRITICAL | Re-read missing outputs |
| Consensus addresses the original task completely | CRITICAL | Fill gaps from individual outputs |
| Provenance annotations present for disagreements | WARNING | Add source attribution |
| Single-source findings flagged | WARNING | Add single-source labels |
| Output format matches expected format | WARNING | Reformat to match task type |

**Convergence rules:**

| Condition | Action |
|-----------|--------|
| No CRITICAL or WARNING issues remain | **Done** |
| `iteration >= max_iterations` | **Max reached** — report remaining |
| No fixes applied this iteration | **Stuck** — needs human decision |

---

## Edge Cases

1. **Only 1 CLI available**: Inform user. Offer to run single-model instead.
2. **CLI hangs/timeouts**: `timeout` command kills hung processes. Proceed with successful outputs.
3. **Empty output**: Treat as failed model. Exclude from consensus.
4. **All external models fail**: Fall back to Claude-only and inform user.
5. **Prompt too large** (>100KB): Truncate guidelines, warn user.
6. **Different output formats**: Consensus agent normalizes during merge.

## Temporary File Management

All temp files go to `$PWD/.temp/multi/<run-id>/`:
- `prompt.md` — assembled prompt
- `<model-name>.md` — individual model outputs
- `<model-name>.status` — execution status JSON
- `consensus.md` — final merged result
- `manifest.json` — model manifest

The `.temp/` directory is cleaned when `/clear` is run.

## CLI Tool Preferences

- `fd` instead of `find`
- `rg` instead of `grep`
- `jq` for JSON processing
- `mktemp` / `mkdir -p` for temp directories

## Rules

1. **Opus is always the consensus engine.** External models provide input; Opus decides.
2. **Always detect at runtime.** Never assume which CLIs are installed.
3. **Respect timeouts.** Never let a hung CLI block the workflow.
4. **Attribute sources.** Always note which model contributed which finding.
5. **Fail gracefully.** If multi-model fails, fall back to single-model.
6. **Self-contained prompts.** External CLIs can't use devkit tools — embed all context.
7. **Temp files in .temp/.** Never use system temp dirs. Clean on `/clear`.
