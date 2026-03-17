# Expressive Code Guidelines

Guidelines for writing code blocks in markdown documents using expressive-code features. These conventions ensure code examples are readable, focused, and well-structured.

---

## 1. Always Include a Language Identifier

Every code block MUST have a language identifier. Never use bare triple-backtick fences.

```markdown
<!-- WRONG -->
```
const x = 1
```

<!-- CORRECT -->
```javascript
const x = 1
```
```

Common identifiers: `javascript`, `typescript`, `python`, `java`, `bash`, `sql`, `json`, `yaml`, `html`, `css`, `go`, `rust`, `ruby`, `php`, `c`, `cpp`, `csharp`, `swift`, `kotlin`, `plaintext`.

---

## 2. File Title with `title=`

Use `title="path/to/file.ext"` to show the file path or name as a header on the code block.

```markdown
```typescript title="src/services/auth.ts"
export class AuthService {
  async login(email: string, password: string): Promise<Token> {
    // ...
  }
}
```
```

**When to use:**
- Code represents a specific file in a project
- Multiple code blocks from different files appear in sequence
- Code should be placed in a specific location by the reader

**When to skip:**
- Short inline examples or REPL-style snippets
- Generic concepts not tied to a specific file

---

## 3. Line Highlighting with `{ranges}`

Highlight specific lines to draw attention to the key parts being discussed.

```markdown
```typescript title="middleware.ts" {3-5}
import { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('session')
  if (!token) return Response.redirect('/login')
  return NextResponse.next()
}
```
```

**Syntax:**
- `{3}` — single line
- `{3-5}` — range
- `{1,4,7-9}` — multiple lines and ranges

**When to use:**
- Text discusses specific lines ("Note lines 3-5 where...")
- Showing a modification within a larger file
- Drawing attention to the important part of a long example

---

## 4. Collapsible Sections with `collapse={ranges}`

Collapse lines that are necessary for completeness but not the focus of discussion (imports, boilerplate, setup, configuration).

```markdown
```typescript title="handler.ts" collapse={1-4,12-15}
import { Request, Response } from 'express'
import { UserService } from './services/user'
import { validate } from './middleware/validation'
import { logger } from './utils/logger'

export async function createUser(req: Request, res: Response) {
  const { email, name } = req.body
  const user = await UserService.create({ email, name })
  res.status(201).json(user)
}

// Helper function for validation
function validateInput(data: unknown): boolean {
  return schema.safeParse(data).success
}
```
```

**Mandatory collapse candidates:**
- Import statements (unless imports ARE the topic)
- Configuration objects and setup
- Helper/utility functions shown for completeness
- Boilerplate (class wrappers, module exports, type definitions not being discussed)
- Error handling when the focus is on happy path (and vice versa)

**Never collapse:**
- The lines being discussed in surrounding text
- Core logic that the reader must understand
- Error handling when that IS the topic

---

## 5. Line Numbers

Line numbers are shown by default. Control them explicitly when needed.

```markdown
<!-- Show line numbers (default) -->
```typescript showLineNumbers
// line 1
// line 2
```

<!-- Hide line numbers -->
```bash showLineNumbers=false
npm install express
```

<!-- Start from a specific line -->
```typescript showLineNumbers startLineNumber=42
// This is line 42 in the original file
export function processQueue() {
```
```

**When to use `showLineNumbers=false`:**
- Short CLI commands (1-3 lines)
- Configuration snippets
- Output/logs

**When to use `startLineNumber=N`:**
- Showing a section from the middle of a large file
- When text references specific line numbers in the original source

---

## 6. Terminal Frame with `frame="terminal"`

Use `frame="terminal"` for command-line examples. Bash code blocks automatically get terminal framing in most configurations.

```markdown
```bash frame="terminal"
npm install @auth/core @auth/express
npm run build
npm test
```
```

**When to use:**
- Installation commands
- CLI tool usage
- Build/deploy commands
- Shell script execution

---

## 7. Diff Marking with `ins={}` and `del={}`

Show inserted and deleted lines for before/after comparisons without using diff syntax.

```markdown
```typescript title="config.ts" del={2} ins={3-4}
export const config = {
  timeout: 5000,
  timeout: 30_000,
  retries: 3,
}
```
```

**Alternative:** Use the `diff` language for traditional diff format:
```markdown
```diff
- timeout: 5000,
+ timeout: 30_000,
+ retries: 3,
```
```

---

## 8. Line Marking with `mark={}`

Mark lines with a neutral background highlight (not green/red like ins/del).

```markdown
```typescript mark={3}
const users = await db.query('SELECT * FROM users')
for (const user of users) {
  await sendEmail(user.email, template) // N+1 problem!
}
```
```

---

## 9. Word Wrapping with `wrap`

Enable word wrapping for long lines (logs, URLs, config values).

```markdown
```json wrap
{"error":"ConnectionTimeoutError","message":"Failed to connect to database at postgresql://prod-db-cluster.internal:5432/myapp after 30000ms","timestamp":"2024-01-15T10:30:00Z"}
```
```

---

## 10. Combining Features

Features can be combined on a single code block:

```markdown
```typescript title="src/api/users.ts" {7-9} collapse={1-3} showLineNumbers
import { Router } from 'express'
import { UserService } from '../services/user'
import { authMiddleware } from '../middleware/auth'

const router = Router()

router.post('/users', authMiddleware, async (req, res) => {
  const user = await UserService.create(req.body)
  res.status(201).json(user)
})

export default router
```
```

---

## 11. Best Practices Summary

| Practice | Rule |
|----------|------|
| Language identifier | Always include |
| File title | Include when code represents a specific file |
| Collapse imports | Always collapse unless imports are the topic |
| Collapse boilerplate | Collapse setup, config, helpers not being discussed |
| Highlight key lines | Use `{ranges}` when text references specific lines |
| Terminal frame | Use for CLI commands |
| Line numbers | Keep default; hide for short CLI snippets |
| Realistic code | Include proper imports, error handling, types |
| Inline comments | Add for non-obvious logic only |
| Block length | Prefer focused blocks (10-30 lines); use collapse for longer |

---

## 12. Anti-Patterns

- **Missing language identifier**: Always specify the language
- **Collapsing important code**: Never hide the lines being discussed
- **Too much highlighted**: If >50% of lines are highlighted, nothing stands out
- **No title on file-specific code**: Reader doesn't know where to put it
- **Pseudocode without marking**: Use `plaintext` or `pseudocode` as language, not bare fences
- **Truncated examples**: Use `collapse` instead of `// ...` comments for omitted code
- **Missing imports**: Include imports (collapsed) so examples are runnable
