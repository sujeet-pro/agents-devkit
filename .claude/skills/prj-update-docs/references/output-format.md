# Final report format

The skill writes exactly one report file per run at:

```
.temp/prj-update-docs/<YYYY-MM-DD-HHMMSS>/report.md
```

Plus a side-car JSON at the same path with `.json` extension for machine consumption (CI,
follow-up agents).

## Report shape

```markdown
# prj-update-docs report — <YYYY-MM-DD HH:MM:SS>

## TL;DR

- Pages: <created> created, <updated> updated, <unchanged> unchanged, <deleted> deleted
- Diagrams: <rendered> rendered, <validated> validated, <residuals> residual issues
- Build: <PASS / FAIL>
- Drift errors: <count> (see "Drift")
- Choices made: <see "Choices">

## Choices

| # | Question | Selected (auto / user) |
| - | -------- | ---------------------- |

## Pages

### Created

| Artifact kind | Source                          | Doc page                                       |
| ------------- | ------------------------------- | ---------------------------------------------- |

### Updated

| Artifact kind | Source                          | Doc page                                       | Reason                |
| ------------- | ------------------------------- | ---------------------------------------------- | --------------------- |

### Deleted (proposed or applied)

| Source (gone) | Doc page                                       | Action               |
| ------------- | ---------------------------------------------- | -------------------- |

### Unchanged

<count> pages skipped because both source + doc hashes were unchanged.

### Skipped (opt-out)

| Doc page | Reason (`prj_update_docs: skip`) |
| -------- | -------------------------------- |

## Drift

### Errors (must-fix)

| Doc page | File:line in source | Drift                                                 |
| -------- | ------------------- | ----------------------------------------------------- |

### Warnings (should-fix)

| Doc page | File:line in source | Drift                                                 |
| -------- | ------------------- | ----------------------------------------------------- |

### Manual edits preserved

| Doc page | Diff size (lines) |
| -------- | ----------------- |

## Diagrams

### Rendered

<count> diagrams across <count> sources, force-re-rendered. <count> were already up to date.

### Validation

| Severity | Code                     | Count | Files (first 3)              |
| -------- | ------------------------ | ----- | ---------------------------- |

### Residuals (after 8-iteration cap)

| Source file | Final issues | Last attempted fix |
| ----------- | ------------ | ------------------ |

## Build

| Step                          | Status | Notes                                          |
| ----------------------------- | ------ | ---------------------------------------------- |
| `npx pagesmith-docs build`    |        | Exit code, build time, warnings inline below.  |
| `pagesmith-docs dev` smoke    |        | Skipped under `--auto` unless interactive.     |
| Internal link check           |        | Broken links listed below.                     |

### Build warnings

```text
<verbatim warning lines>
```

### Broken internal links

| Page | Link target | Reason                                  |
| ---- | ----------- | --------------------------------------- |

## Follow-ups

- <bullet for each follow-up the user must do manually>

## Run metadata

- ADK version: <git rev>
- Pagesmith version: <package.json `@pagesmith/docs`>
- diagramkit version: <package.json `diagramkit`>
- Node: <node --version>
- OS: <uname -s -r>
- Mode: <auto / review / fix>
- Scope: <all / skills / ...>
- Wall-clock duration: <hh:mm:ss>
```

## Severity labels

| Label    | Meaning                                                                        |
| -------- | ------------------------------------------------------------------------------ |
| critical | Build or render failed; the user MUST act before anything else can ship.       |
| error    | Doc / source drift the run could not auto-fix; surfaces in "Drift → Errors".   |
| warn     | Drift the run did fix or could fix later; surfaces in "Drift → Warnings".      |
| info     | Nice-to-know (e.g. number of unchanged pages).                                 |

## Stdout summary (always)

In addition to the report, print a 6-line summary to stdout, exactly:

```
prj-update-docs: <N> pages created, <N> updated, <N> deleted
prj-update-docs: <N> diagrams rendered, <N> residual issues
prj-update-docs: pagesmith-docs build PASS|FAIL (<seconds>s)
prj-update-docs: <N> drift errors, <N> warnings
prj-update-docs: report at .temp/prj-update-docs/<timestamp>/report.md
prj-update-docs: next: <one-sentence next action for the user>
```

This is the only thing the user reads if the run is successful — it must be 6 lines, no
more, no less.
