# `review-feedback` — comment grouping

How related comments are grouped so a single fix addresses multiple where applicable.

## Why grouping matters

A 30-comment review often groups into 8 logical fixes. Without grouping:

- 30 commits, one per comment — noisy history; reviewers can't see the structure of the fixes.
- 30 separate validations — slow.
- 30 "Done in <sha>" replies — each with a different SHA — reviewer has to context-switch per comment.

With grouping:

- 8 commits (one per logical fix) — readable history.
- 8 validations — fast.
- 30 replies — each pointing to the right SHA, with a per-comment one-liner — reviewer sees the structure.

The reply for each comment in a group cites the same SHA but has a per-comment one-liner so each thread has its own resolution proof.

## Grouping algorithm

```
1. For each apply-* classification, extract the "root cause" (heuristic):
   - Same file:line range (within ±10 lines) -> candidate same-group.
   - Same dimension AND same category-noun (e.g. "missing input validation") -> candidate same-group.
   - Same suggested fix (semantic match: rename / extract / add-test / etc.) -> candidate same-group.

2. Build clusters:
   - For each pair of apply-* comments, compute a similarity score from the heuristics above.
   - Cluster: comments with similarity >= 0.6.

3. For each cluster:
   - Define the "logical fix" — a one-line description that covers all comments in the cluster.
   - Rank comments by their authority (who made the comment first; who's the file's CODEOWNER) for the cluster's "primary" comment.

4. Validate the grouping:
   - If a cluster has comments with different fix shapes (e.g. one says "extract", one says "rename"), DO NOT GROUP — each comment becomes its own logical fix.
   - If a cluster spans dimensions (e.g. one comment is `correctness`, one is `tests`), GROUP ALLOWED — common case is "add validation + add test".

5. Surface the grouping in classification.md (with reasoning per cluster).

6. Under -i: walk each cluster; allow user to split / merge.
```

## Worked grouping examples

### Example A: 4 comments → 1 group

**Comments:**

1. `routes/api.go:42` ("`POST /products` missing input validation")
2. `routes/api.go:78` ("`POST /products/bulk` missing input validation")
3. `routes/api.go:112` ("`POST /products/<id>` missing input validation on update")
4. `routes/api.go:156` ("`POST /orders/<id>` missing input validation")

**Grouping:** all 4 → cluster `g1` (logical fix: "add shared `validateProduct` validator and apply across the 4 POST handlers").

**Reasoning:** same root cause (missing validation), same suggested fix shape (add a validator, apply it), same file.

**Commit:** 1 commit (`xyz1234`) with the validator + 4 handler updates.

**Replies:** 4 separate replies, each citing `xyz1234` with a per-handler one-liner.

### Example B: 3 comments → 2 groups

**Comments:**

1. `db/orders.go:88` ("extract `processOrder` helper")
2. `db/orders.go:117` ("n+1 query")
3. `db/orders.go:200` ("missing test for the n+1 path")

**Grouping:**
- Comments 2 + 3 → cluster `g1` (logical fix: "fix n+1 + add the test"). They're related: the test exercises the n+1 fix.
- Comment 1 → standalone (different root cause: code organization).

**Reasoning:** comments 2 + 3 share root cause + dimension; comment 1 is unrelated (style/refactor).

**Commits:** 2 commits — `g1` is one commit (or two: the fix + the test, with the test commit immediately after); comment 1 is a separate commit.

### Example C: NO grouping (different fix shapes)

**Comments:**

1. `services/order.go:42` ("extract this into a helper")
2. `services/order.go:42` ("rename `process` to `handle`")

**Grouping:** NO. Same line, but different fix shapes (extract vs rename). Each becomes its own logical fix.

**Treatment:** if both `apply-*`, the user picks one (under `-i`) or the skill chooses the more specific one (rename over extract; under `--auto`).

### Example D: cross-dimension grouping

**Comments:**

1. `routes/admin.go:42` ("missing role check") (correctness)
2. `routes/admin_test.go:-` ("no test for the new admin endpoint") (tests)

**Grouping:** allowed. Cluster `g1` (logical fix: "add role check + the test that verifies it").

**Commits:** 2 commits (the fix, then the test) OR 1 squashable commit. The test references the fix.

## Heuristic implementations

### Same-line proximity

```python
def line_proximity(a: Comment, b: Comment) -> float:
    if a.file != b.file:
        return 0.0
    diff = abs(a.line - b.line)
    if diff <= 10:
        return 1.0
    if diff <= 30:
        return 0.5
    return 0.0
```

### Same category-noun

```python
CATEGORY_NOUNS = {
    "missing input validation",
    "n+1 query",
    "auth bypass",
    "missing test",
    "extract helper",
    "rename for clarity",
    "secret in diff",
    "ssrf",
    "csrf",
    "xss",
    "missing null check",
    "off-by-one",
    "race condition",
    "missing error handling",
    "missing pagination",
    # ... etc
}

def extract_category(comment_body: str) -> str | None:
    body_lower = comment_body.lower()
    for noun in CATEGORY_NOUNS:
        if noun in body_lower:
            return noun
    return None

def same_category(a: Comment, b: Comment) -> bool:
    ca = extract_category(a.body)
    cb = extract_category(b.body)
    return ca is not None and ca == cb
```

### Same suggested fix shape

```python
FIX_SHAPES = {
    "rename": ["rename", "rename to", "should be called"],
    "extract": ["extract", "factor out", "pull into a helper"],
    "add-test": ["add a test", "missing test", "needs test coverage"],
    "add-validation": ["add validation", "validate input", "guard against"],
    "fix-typo": ["typo", "spelling"],
    "remove": ["remove", "delete", "drop this"],
    # ... etc
}

def fix_shape(body: str) -> str | None:
    body_lower = body.lower()
    for shape, triggers in FIX_SHAPES.items():
        if any(t in body_lower for t in triggers):
            return shape
    return None

def same_shape(a: Comment, b: Comment) -> bool:
    sa = fix_shape(a.body)
    sb = fix_shape(b.body)
    return sa is not None and sa == sb
```

### Combined similarity

```python
def similarity(a: Comment, b: Comment) -> float:
    return max(
        line_proximity(a, b),
        1.0 if same_category(a, b) else 0.0,
        1.0 if same_shape(a, b) else 0.0,
    )

def cluster(comments: list[Comment]) -> list[list[Comment]]:
    clusters = []
    for c in comments:
        added = False
        for cl in clusters:
            if any(similarity(c, c2) >= 0.6 for c2 in cl):
                cl.append(c)
                added = True
                break
        if not added:
            clusters.append([c])
    return clusters
```

## Anti-patterns

- **Over-grouping.** Grouping comments with different fix shapes loses traceability. When in doubt, leave separate.
- **Under-grouping.** 4 comments on the same root cause = 4 commits is noise. Group when same fix shape + same root cause.
- **Cross-dimension grouping when the fixes are independent.** "Rename + add test" is grouped because the test verifies the rename. "Rename + fix CSS" is NOT grouped — they're independent.
- **Skipping the grouping phase.** The fix queue should be groups, not raw comments.
- **Bundling everything into one squash commit by default.** Default is one-per-logical-fix for traceability; `--squash-fixes` is opt-in.

## Output

The grouping is written to `classification.md` in the `Groups` table (see `references/output-format.md` for the shape).

Under `-i`, the user can edit groupings:

```
[grouping] Cluster g1 covers comments #1, #2, #5 (logical fix: "add shared validateProduct validator").
  - [a]ccept this grouping
  - [s]plit (each becomes its own fix)
  - [m]erge with another cluster
> a
```
