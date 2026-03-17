---
name: review
description: Auto-detect review type (PR or document) and delegate to the appropriate review skill
user_invocable: true
arguments:
  - name: target
    description: "PR number/URL, file path, Confluence URL, or Google Docs URL"
    required: true
  - name: tags
    description: "Comma-separated tags (coding: ds,lib,fe,be,script; document: tdd,hld,lld,prd,erd,tool-eval,blog,article,project,etc.)"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100)"
    required: false
---

# Review Skill

Auto-detect whether the target is a pull request or a document, then delegate to the
appropriate specialized review skill (`/pr-review` or `/doc-review`).

This is the universal entry point for all reviews. Users can invoke `/review 42` for a
PR, `/review path/to/design.md` for a local document, or `/review <URL>` for a remote
document — and the right reviewer runs automatically.

---

## Detection Logic

Examine the `$ARGUMENTS.target` value and apply these rules **in order** — use the
**first** match:

### Rule 1: Bare number → Pull Request

If `$ARGUMENTS.target` is a bare number (matches `^[0-9]+$`):

1. Check if the current directory is inside a git repository:
   ```bash
   git rev-parse --is-inside-work-tree 2>/dev/null
   ```
2. If yes → treat as a PR number. Delegate to `/pr-review --pr=<target>`.
3. If not in a git repo → ask the user to provide a full PR URL or specify the repo.

### Rule 2: GitHub or Bitbucket PR URL → Pull Request

If `$ARGUMENTS.target` URL matches either pattern:
- Contains `github.com` **and** `/pull/` (e.g., `https://github.com/org/repo/pull/42`)
- Contains `bitbucket.org` **and** `/pull-requests/` (e.g., `https://bitbucket.org/ws/repo/pull-requests/42`)

Delegate to `/pr-review --pr=<target>`.

### Rule 3: Confluence URL → Document Review

If `$ARGUMENTS.target` URL contains `atlassian.net/wiki/`:

Delegate to `/doc-review --source=<target>`.

### Rule 4: Google Docs URL → Document Review

If `$ARGUMENTS.target` URL contains `docs.google.com/document/`:

Delegate to `/doc-review --source=<target>`.

### Rule 5: Local file path → Document Review

Check if the target is an existing file:
```bash
test -f "$ARGUMENTS_TARGET"
```

If the file exists → delegate to `/doc-review --source=<target>`.

If the file does not exist, also try resolving relative to the current directory:
```bash
test -f "$(pwd)/$ARGUMENTS_TARGET"
```

### Rule 6: Ambiguous → Ask the user

If none of the above rules match, ask the user to clarify:

> Could not determine review type for: `<target>`
>
> Please provide one of:
> - A PR number (e.g., `42`) — requires being in a git repo
> - A GitHub or Bitbucket PR URL
> - A Confluence page URL
> - A Google Docs URL
> - A local file path

---

## Display Detection Before Delegating

**CRITICAL**: Always show the detection result and give the user a moment to abort
before delegating. This prevents wasted effort if the detection is wrong.

```
Review Detection:
  Input:      42
  Detected:   Pull Request #42
  Platform:   GitHub
  Delegating: /pr-review --pr=42
  Tags:       [fe, be] (from args or auto-detected)

Proceeding... (Ctrl+C to abort and re-run with different args)
```

For document targets:

```
Review Detection:
  Input:      docs/design/auth-system.md
  Detected:   Local document
  Platform:   Local file
  Delegating: /doc-review --source=docs/design/auth-system.md --doc-type=tdd --coding-tags=be
  Tags:       [tdd, be] (split from args)

Proceeding... (Ctrl+C to abort and re-run with different args)
```

---

## Tag Handling

Tags from `$ARGUMENTS.tags` need to be split and routed to the correct delegated skill.

### Known tag categories

**Document type tags** — these map to the `--doc-type` argument of `/doc-review`:
`tdd`, `hld`, `lld`, `prd`, `erd`, `tool-eval`, `community`, `coding-guide`,
`appraisal`, `feedback`, `blog`, `article`, `project`

**Coding tags** — these map to `--tags` for `/pr-review` or `--coding-tags` for `/doc-review`:
`ds`, `lib`, `fe`, `be`, `script`

### Splitting logic

When delegating to `/pr-review`:
- Pass **all** tags as `--tags=<all-tags>`. PR review handles its own tag routing.

When delegating to `/doc-review`:
- Split the tags:
  - Tags matching document type tags → `--doc-type=<first-doc-type-tag>` (only one
    doc-type can be active; if multiple are provided, use the first one and warn)
  - Tags matching coding tags → `--coding-tags=<coding-tags>`
- Example: `--tags=tdd,fe,be` → `--doc-type=tdd --coding-tags=fe,be`

### Confidence pass-through

If `$ARGUMENTS.confidence` is provided, pass it directly to the delegated skill:
- For PR review: `--confidence=<value>`
- For doc review: `--confidence=<value>`

---

## Delegation

After detection and tag splitting, invoke the appropriate skill:

### For Pull Requests

```
/pr-review --pr=<target> --tags=<tags> --confidence=<confidence>
```

Only include `--tags` if tags were provided or detected.
Only include `--confidence` if a value was provided.

### For Documents

```
/doc-review --source=<target> --doc-type=<doc-type> --coding-tags=<coding-tags> --confidence=<confidence>
```

Only include `--doc-type` if a document type tag was resolved.
Only include `--coding-tags` if coding tags were resolved.
Only include `--confidence` if a value was provided.

---

## Important Rules

1. **Always detect before delegating**: Never skip the detection step. Always show the
   user what was detected and where the review is being routed.

2. **Fail fast on ambiguity**: If the target cannot be classified, ask immediately.
   Do not guess and waste time running the wrong review type.

3. **Preserve all arguments**: When delegating, pass through all relevant arguments.
   Do not drop the confidence threshold or tags during delegation.

4. **Single doc-type**: Only one document type tag can be active at a time. If the user
   provides multiple (e.g., `tdd,hld`), use the first one and warn: "Multiple document
   types provided; using 'tdd'. Re-run with a single --doc-type to change."

5. **No double review**: This skill only detects and delegates. It does not perform
   any review itself. All review logic lives in `/pr-review` and `/doc-review`.
