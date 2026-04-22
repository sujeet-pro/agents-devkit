# `mode-contract` — validator (used by `bin/adk-validate`)

For each skill in `skills/<name>/`:

## Phase 1
- [ ] If `metadata.modes` is declared, every value is from `{auto, review, fix}`.
- [ ] If frontmatter omits `metadata.modes`, the skill is treated as `auto`-only.

## Phase 2
- [ ] `references/modes.md` exists and documents EACH declared mode for this skill (not just the universal set).

## Phase 3
- [ ] If `[review]` is declared, the skill must NOT write to source files in that mode (best-effort static analysis; manual confirmation otherwise).
- [ ] If `[fix]` is declared, the skill must end its `fix`-mode workflow by either re-running `review` or producing a `validation/d1.md` proving no residual findings.
