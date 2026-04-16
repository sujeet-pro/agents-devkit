# Document Management Workflow

## Phase 1: Locate

**Goal**: Find or create the target file or folder.

1. Check OAuth authentication status via `authGetStatus`
2. If `--target` is provided: search Drive for the specified file by ID or name
3. If no target: search Drive for files matching the task description to avoid duplicates
4. For folder operations: list folder contents to understand current structure
5. **Gate**: Confirm the target file/folder and intended action with the user (skip if `--auto`)

## Phase 2: Plan

**Goal**: Propose content or organizational changes before execution.

1. For create operations: outline the document structure (title, sections, content summary)
2. For update operations: describe what will change relative to current content
3. For share operations: specify the recipient, access level, and any existing permissions
4. For organize operations: describe the folder structure changes
5. **Gate**: Present the plan for approval; permission changes always require approval regardless of `--auto`

## Phase 3: Execute

**Goal**: Perform the Google Drive operation via MCP.

1. Execute via the appropriate `mcp__google-drive__*` tool
2. For document creation: create the document, then update with content in a second call if needed
3. For sharing: add permissions, then verify the recipient list
4. For uploads: upload the file, then verify it appears in the target folder
5. Capture the response: document URL, file ID, or error

## Phase 4: Verify

**Goal**: Confirm changes via Drive API.

1. Read back the affected document to confirm state matches intent
2. For creation: verify the document exists, has the correct title, and is in the right folder
3. For updates: verify the content matches what was planned
4. For sharing: verify permissions were applied correctly
5. Report the final URL, file ID, sharing status, and any remaining follow-ups

## Validation Rules

- Every mutating operation must produce a confirmable artifact (URL, file ID, permission)
- Read operations must return content or explicit "not found"
- Sharing operations must confirm recipient and access level by reading back permissions
- Never claim success without API confirmation
- If verification fails, state so explicitly and suggest manual confirmation
