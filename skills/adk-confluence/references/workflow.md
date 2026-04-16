# ADK Confluence Workflow

## Default Flow

1. run preflight to confirm the Atlassian Confluence MCP server is configured
2. confirm the task, target space, target page, and intended action with the user
3. identify the correct MCP tool(s) for the requested operation
4. for destructive or overwrite operations, get explicit user confirmation before proceeding
5. execute the operation via MCP tools
6. validate the result by reading back the affected resource
7. report the outcome with page URL, page ID, and a summary of changes

## Create Flow

Use when creating a new Confluence page.

1. confirm the target space key, page title, and parent page (if any)
2. if content is provided as markdown, convert to Confluence storage format
3. if the markdown references local images, upload them as attachments first
4. call `confluence_create_page` with the space key, title, parent ID, and storage-format body
5. if labels were requested, call `confluence_add_label` for each label
6. fetch the created page with `confluence_get_page` to confirm it exists
7. report the page URL, page ID, title, and any labels applied

## Update Flow

Use when modifying an existing Confluence page.

1. fetch the current page with `confluence_get_page` to get the latest version and content
2. if the page was recently edited by someone else, warn the user and confirm before proceeding
3. apply the requested changes to the page content
4. if new content is markdown, convert to Confluence storage format
5. call `confluence_update_page` with the updated body and incremented version number
6. if labels need adding, call `confluence_add_label`
7. fetch the updated page to confirm the changes took effect
8. report what changed, the new version number, and the page URL

## Publish Flow

Use when publishing a local markdown document to Confluence.

1. read the local markdown file
2. check for YAML frontmatter fields: `confluence_id`, `space`, `title`, `labels`
3. if `confluence_id` exists, treat as an update to the existing page (go to Update Flow step 1)
4. if no `confluence_id`, treat as a new page creation
5. convert the markdown body to Confluence storage format using the format mapping rules
6. identify local image references and upload them as attachments
7. replace local image paths in the storage-format body with `<ri:attachment>` references
8. create or update the page via MCP
9. add labels from frontmatter or `--labels` parameter
10. fetch the resulting page to confirm
11. report the page URL, page ID, conversion notes, and any images uploaded

## Search Flow

Use when finding pages, content, or users in Confluence.

1. confirm the search query, target space (if any), and result expectations
2. call `confluence_search` with the query and any space filters
3. review the result set for relevance
4. present results as a structured list with page title, URL, space, and last modified date
5. if results are too broad, suggest refining the query with space filters or CQL operators
6. if searching for users, use `confluence_search_user` instead

## Delete Flow

Use when removing a Confluence page.

1. fetch the page with `confluence_get_page` to confirm it exists and display its title
2. check for child pages with `confluence_get_page_children`
3. if child pages exist, warn the user about cascading effects
4. get explicit confirmation from the user before proceeding
5. call `confluence_delete_page`
6. attempt to fetch the page again to confirm deletion
7. report the deletion with the former page title and ID

## Move Flow

Use when relocating a page to a different parent or position.

1. fetch the source page to confirm it exists
2. fetch the target parent page to confirm it exists
3. confirm the move with the user, showing source title and destination
4. call `confluence_move_page` with the page ID and new parent ID
5. fetch the moved page to confirm its new location
6. report the move with old and new parent information

## Comment Flow

Use when adding or reading comments on a page.

1. fetch the page to confirm it exists
2. for reading: call `confluence_get_comments` and present the comments with author and timestamp
3. for adding: call `confluence_add_comment` with the comment body
4. for replying: call `confluence_reply_to_comment` with the parent comment ID and reply body
5. confirm the comment was posted by reading comments back

## Attachment Flow

Use when managing page attachments.

1. fetch the page to confirm it exists
2. for uploading: call `confluence_upload_attachment` with the file path and page ID
3. for listing: call `confluence_get_attachments` to show all attachments with file names and sizes
4. for downloading: call `confluence_download_attachment` with the attachment ID and output path
5. for deleting: confirm with the user, then call `confluence_delete_attachment`
6. after any mutation, list attachments again to confirm the change

## History Flow

Use when reviewing page version history or comparing versions.

1. call `confluence_get_page_history` to list versions with dates, authors, and messages
2. if a diff is requested, call `confluence_get_page_diff` with the two version numbers
3. present the history or diff in a readable format
4. highlight significant changes between versions

## Validation Rules

- every page creation returns a page URL and page ID
- every page update returns the new version number
- every attachment upload is confirmed by listing attachments afterward
- every delete is confirmed by attempting to fetch the deleted resource
- search results always include a count and representative items
- if an MCP call fails, report the error clearly and suggest corrective action
- do not claim success without confirming the result through a read-back operation
