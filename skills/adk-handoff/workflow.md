# Session Continuity Workflow

## Phase 1: Capture

**Goal**: Snapshot the current session state comprehensively.

### Create Flow
1. Run `python3 scripts/handoff.py` to capture git state automatically (branch, uncommitted changes, staged files, recent commits)
2. Gather task context from the conversation history or `--task` parameter
3. Identify all modified, created, and deleted files from git status and conversation
4. Extract decisions made during the session with their rationale

### Resume Flow
1. Read the specified handoff document
2. Run `git status` and `git branch` to capture current state
3. Compare current git state against the recorded state
4. Surface any mismatches (different branch, unexpected changes, missing files)

### Status Flow
1. Find existing handoff documents in `.handoff/` or at known paths
2. Read each document's header to extract task, date, and progress

## Phase 2: Structure

**Goal**: Organize captured information using the handoff template at `references/handoff-template.md`.

Read `references/handoff-template.md` and fill every section:

1. **Task**: what is being worked on and the end goal
2. **Current State**: what is done, in progress, and not started
3. **Decisions Made**: each decision with rationale so settled questions stay settled
4. **Remaining Work**: ordered by priority, each item actionable and specific
5. **Blockers and Open Questions**: anything preventing progress or needing clarification
6. **Key Files**: files created, modified, or deleted during the session
7. **Git State**: branch name, uncommitted changes, staged files, recent commits
8. **Environment Notes**: runtime versions, config, or setup steps to reproduce current state
9. **Resumption Checklist**: pre-checks for the next session

## Phase 3: Package

**Goal**: Assemble the handoff document and get user confirmation.

1. Compile all sections into a single markdown document
2. Estimate progress percentage based on completed vs. remaining items
3. Present the document summary to the user for review
4. **Gate**: User confirms completeness or requests additions/corrections
5. Incorporate any feedback from the user

## Phase 4: Deliver

**Goal**: Save the handoff document and summarize.

1. Write the handoff document to the output path (default: `.handoff/handoff-YYYY-MM-DD-HHMM.md`)
2. Create the `.handoff/` directory if it does not exist
3. Report: file path, task summary, progress percentage, blocker count, next action recommendation
4. For resume: present remaining work and suggest the immediate next step

## Validation Rules

- Git state captured matches live `git` output
- All modified files are listed in the document
- Remaining work items are actionable (not vague)
- Blockers are specific enough to act on
- The document can stand alone without the original conversation
- For resume: current state matches recorded state (or mismatches are surfaced)
