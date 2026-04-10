# Review Comment Template

Canonical format for all review findings. Used by all stages that produce or post review comments.

---

## Priority Labels

| Priority | Icon | Meaning |
|----------|------|---------|
| **Blocker** | :no_entry: | Blocks merge -- correctness, data loss, security vulnerability |
| **Critical** | :rotating_light: | Serious issue -- bugs, regressions, significant design flaws |
| **Should Have** | :large_orange_diamond: | Improvement opportunity -- better patterns, readability, maintainability |
| **May Have** | :small_blue_diamond: | Minor improvement -- optional enhancement, alternative approach |
| **Nitpick** | :pushpin: | Style or convention issue -- naming, formatting, trivial cleanup |
| **Question** | :grey_question: | Clarification needed -- unclear intent, missing context, design rationale |
| **Praise** | :star2: | Well-crafted code worth calling out |

---

## Comment Structure

Every review finding uses this structure:

```md
<icon> **[<PRIORITY>][<aspects>]** <Short, specific title>

| | |
|---|---|
| **Location** | `<file-path>:<line-range>` |
| **Confidence** | <score>/100 |
| **Concern** | <Correctness\|Design\|Reliability\|Performance\|DevEx> |
| **Depth** | <Surface\|Logic\|Integration\|Architecture\|Hardening> |
| **Dimension** | <syntax\|correctness\|security\|performance\|design\|reliability\|testing\|documentation\|ui-ux\|spec-compliance> |
| **Guideline** | <which standard or best practice is violated> |

#### Issue
<1-2 sentence description of the problem>

#### Where it fails
<specific cases, inputs, or conditions that trigger the issue>

#### Why it matters
<impact on correctness, security, performance, maintainability, or user experience>

#### Suggested fix
<recommendation with code snippet when applicable>

<details>
<summary>Suggested tests</summary>

<test cases that would catch this issue>
</details>
```

---

## Lightweight Format (Nitpick / Question)

For low-severity findings where the full structure is unnecessary:

```md
<icon> **[<PRIORITY>][<aspects>]** <Short, specific title>
*`<file-path>:<line>` | Confidence: <score>/100 | Dimension: <dimension>*
> <1-2 sentence explanation or question>
```

---

## Praise Format

```md
:star2: **[Praise][<aspects>]** <Short, specific title>

> <1-3 sentences explaining what's well done and why it matters.>
```

---

## Example: Blocker

```md
:no_entry: **[Blocker][bug, security]** SQL injection in user search endpoint

| | |
|---|---|
| **Location** | `src/api/users.ts:47-52` |
| **Confidence** | 95/100 |
| **Concern** | Correctness |
| **Depth** | Logic |
| **Dimension** | security |
| **Guideline** | OWASP A03:2021 Injection |

#### Issue
User input is interpolated directly into a SQL query string without parameterization.

#### Where it fails
Any request to `/api/users?search='; DROP TABLE users;--` executes arbitrary SQL.

#### Why it matters
Full database compromise. An attacker can read, modify, or delete any data.

#### Suggested fix
Use parameterized queries:
` `` `ts
const results = await db.query('SELECT * FROM users WHERE name LIKE $1', [`%${search}%`]);
` `` `

<details>
<summary>Suggested tests</summary>

- Test that special SQL characters in search input do not alter the query structure.
- Test that search returns correct results for inputs containing quotes, semicolons, and dashes.
</details>
```

## Example: Should Have

```md
:large_orange_diamond: **[Should Have][error-handling]** Missing error boundary around async file read

| | |
|---|---|
| **Location** | `src/utils/config.ts:23` |
| **Confidence** | 88/100 |
| **Concern** | Reliability |
| **Depth** | Logic |
| **Dimension** | reliability |
| **Guideline** | Defensive error handling for I/O operations |

#### Issue
`fs.readFile` is called without a try/catch. If the file is missing or unreadable, the process crashes with an unhandled rejection.

#### Where it fails
When the config file does not exist on first run, or when file permissions are restricted.

#### Why it matters
Unhandled rejection crashes the service. Users see no actionable error message.

#### Suggested fix
` `` `ts
try {
  const data = await fs.readFile(configPath, 'utf-8');
  return JSON.parse(data);
} catch (err) {
  if (err.code === 'ENOENT') return defaultConfig;
  throw new ConfigError(`Failed to read config: ${err.message}`);
}
` `` `
```

## Example: Nitpick

```md
:pushpin: **[Nitpick][naming]** Ambiguous variable name `data`
*`src/handlers/export.ts:15` | Confidence: 75/100 | Dimension: syntax*
> `data` is used for both the raw response and the parsed result. Consider `rawResponse` and `parsedExport` for clarity.
```

## Example: Praise

```md
:star2: **[Praise][design]** Clean separation of validation and execution

> The validator-then-executor pattern in the pipeline keeps each stage testable in isolation. The shared `ValidationResult` type makes it easy to add new validators without touching the executor.
```
