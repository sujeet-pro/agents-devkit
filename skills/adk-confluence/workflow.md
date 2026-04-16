# Knowledge Base Curator Workflow

## Phase 1: Discover

**Goal**: Search existing pages, identify target space and parent, check for duplicates.

1. Parse the user request to determine the operation: create, update, search, publish, manage
2. Resolve target space from `--space` or ask the user
3. Search for existing pages with similar titles or content to detect duplicates
4. For updates: fetch the current page to get version number and existing content
5. For page tree operations: fetch the space page tree to understand hierarchy
6. **Gate**: Confirm the space, target page (or parent for new pages), and intended action with the user (skip if `--auto`)

## Phase 2: Plan

**Goal**: Propose page structure and content before writing.

1. For create/publish: outline the page structure (headings, sections, estimated word count)
2. For update: describe what will change relative to the current content
3. Identify attachments that need uploading (local images, files)
4. Determine labels to apply
5. **Gate**: Present the content plan for approval (skip if `--auto`)

## Phase 3: Draft

**Goal**: Write the content, converting to Confluence storage format as needed.

1. Author content from code evidence, user input, or local markdown files
2. Convert markdown to Confluence storage format using the documented mapping:
   - Headings, lists, tables, code blocks, admonitions, images, links, task lists
3. For local images: prepare attachment upload list
4. For complex pages: dispatch `adk-doc-writer` subagents for individual sections
5. Assemble the final page body in Confluence storage format

## Phase 4: Publish

**Goal**: Create or update the Confluence page via MCP tools.

1. Upload any attachments first via `confluence_upload_attachment` (images, files)
2. Create the page via `confluence_create_page` or update via `confluence_update_page`
3. Apply labels via `confluence_add_label`
4. Add comments via `confluence_add_comment` if specified
5. Move the page via `confluence_move_page` if a different parent was requested
6. Capture the response: page ID, URL, version number

## Phase 5: Verify

**Goal**: Confirm the page exists and is correctly published.

1. Fetch the page via `confluence_get_page` to confirm it exists
2. Verify the title, space, parent, and labels match intent
3. Verify attachments are listed on the page
4. Report the final URL, page ID, and content summary
5. Surface any rendering issues or missing elements

## Validation Rules

- Every page create/update is confirmed by fetching the resulting page
- Every delete is confirmed by verifying the page is no longer accessible
- Attachment uploads are confirmed by listing page attachments
- Never claim success without MCP response confirmation
- If verification fails, state so explicitly and suggest manual confirmation
