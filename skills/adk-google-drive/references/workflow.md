# ADK Google Drive Workflow

## Default Flow
1. run preflight to verify MCP server availability and authentication status
2. identify the target: resolve `--target` to a file ID via search, or accept a direct file ID; for create operations, determine the parent folder
3. confirm the action scope, target document, and any destructive implications with the user
4. execute the operation using the appropriate `mcp__google-drive__*` tools
5. validate the result: confirm a URL, file ID, or status was returned
6. report the outcome with direct links, identifiers, and suggested next steps

## Auth Check Flow
1. call `mcp__google-drive__authGetStatus` to verify the OAuth connection is active
2. if authentication fails, report the error and provide re-authentication guidance
3. optionally call `mcp__google-drive__authListScopes` to confirm required scopes are granted
4. optionally call `mcp__google-drive__authTestFileAccess` to verify access to a specific file

## Doc Flow
**Create a new Google Doc:**
1. call `mcp__google-drive__createGoogleDoc` with the title and optional content
2. if initial content is provided, call `mcp__google-drive__insertText` or `mcp__google-drive__updateGoogleDoc` to populate the document
3. apply formatting as needed with `applyTextStyle`, `applyParagraphStyle`, `createParagraphBullets`
4. return the document URL

**Read an existing Google Doc:**
1. resolve the target to a file ID via search or direct ID
2. call `mcp__google-drive__readGoogleDoc` or `mcp__google-drive__getGoogleDocContent` for full content
3. call `mcp__google-drive__getDocumentInfo` for metadata (title, last modified, owner)
4. call `mcp__google-drive__listDocumentTabs` if the document has multiple tabs
5. present the content or summary to the user

**Update a Google Doc:**
1. read the current content to understand the existing structure
2. apply changes using `mcp__google-drive__updateGoogleDoc`, `insertText`, or `findAndReplaceInDoc`
3. apply formatting with `applyTextStyle`, `applyParagraphStyle`, `formatGoogleDocText`, `formatGoogleDocParagraph`
4. insert structured elements as needed: `insertTable`, `editTableCell`, `createFootnote`, `insertSmartChip`
5. manage tabs with `addDocumentTab`, `renameDocumentTab` if needed
6. validate the update by reading the modified section

## Sheet Flow
**Create a new Google Sheet:**
1. call `mcp__google-drive__createGoogleSheet` with the title
2. populate with `mcp__google-drive__updateGoogleSheet` or `appendSpreadsheetRows`
3. apply formatting: `formatGoogleSheetCells`, `formatGoogleSheetText`, `formatGoogleSheetNumbers`, `setGoogleSheetBorders`
4. add structure: `addSheet` for additional tabs, `mergeGoogleSheetCells`, `addNamedRange`
5. add validation: `addDataValidation`, `addGoogleSheetConditionalFormat`, `protectRange`
6. return the spreadsheet URL

**Read an existing Google Sheet:**
1. resolve the target to a file ID
2. call `mcp__google-drive__getGoogleSheetContent` for cell data (specify the range for large sheets)
3. call `mcp__google-drive__getSpreadsheetInfo` for metadata
4. call `mcp__google-drive__listSheets` to discover all tabs
5. present the data or summary to the user

**Update a Google Sheet:**
1. read the current content to understand the existing layout
2. update cells with `mcp__google-drive__updateGoogleSheet`
3. append new rows with `appendSpreadsheetRows`
4. manage tabs: `addSpreadsheetSheet`, `renameSheet`, `deleteSheet`
5. manage ranges: `deleteRange`, `addNamedRange`
6. apply formatting and validation as needed
7. validate the update by reading the modified range

## Slides Flow
**Create a new Google Slides presentation:**
1. call `mcp__google-drive__createGoogleSlides` with the title
2. add content: `createGoogleSlidesTextBox`, `createGoogleSlidesShape`
3. style elements: `styleGoogleSlidesShape`, `setGoogleSlidesBackground`
4. format text: `formatGoogleSlidesText`, `formatGoogleSlidesParagraph`
5. add media: `insertImageFromUrl`, `insertLocalImage`
6. manage slides: `duplicateSlide`, `reorderSlides`, `deleteGoogleSlide`
7. add speaker notes: `updateGoogleSlidesSpeakerNotes`
8. return the presentation URL

**Read an existing Google Slides presentation:**
1. resolve the target to a file ID
2. call `mcp__google-drive__getGoogleSlidesContent` for slide content
3. call `mcp__google-drive__getGoogleSlidesSpeakerNotes` for speaker notes
4. optionally call `mcp__google-drive__exportSlideThumbnail` for visual preview
5. present the content or summary to the user

**Update a Google Slides presentation:**
1. read the current content to understand existing slides and layout
2. update text with `mcp__google-drive__updateGoogleSlides` or `replaceAllTextInSlides`
3. add or modify elements: text boxes, shapes, images
4. update speaker notes with `updateGoogleSlidesSpeakerNotes`
5. manage slide order: `duplicateSlide`, `reorderSlides`, `deleteGoogleSlide`
6. validate by reading the modified slides

## Drive Flow
**Search Drive:**
1. call `mcp__google-drive__search` with the query terms
2. filter results by type if `--type` is specified
3. present results with file names, types, IDs, and last modified dates

**Manage folders:**
1. call `mcp__google-drive__createFolder` to create a new folder
2. call `mcp__google-drive__listFolder` to browse folder contents
3. call `mcp__google-drive__moveItem` to move files between folders
4. call `mcp__google-drive__renameItem` to rename files or folders

**Upload and download:**
1. call `mcp__google-drive__uploadFile` to upload a local file to Drive
2. call `mcp__google-drive__downloadFile` to download a Drive file locally
3. for text files, use `mcp__google-drive__createTextFile` or `updateTextFile`

**Share and permissions:**
1. call `mcp__google-drive__listPermissions` to check current sharing status
2. call `mcp__google-drive__shareFile` or `addPermission` to grant access
3. call `mcp__google-drive__updatePermission` to change access level
4. call `mcp__google-drive__removePermission` to revoke access (confirm first)
5. call `mcp__google-drive__lockFile` or `unlockFile` to manage edit locks

## Validation Rules
- every mutating operation must produce a confirmable artifact: a document URL, file ID, or permission status
- read operations must return non-empty content or an explicit "not found" result
- for destructive operations, always obtain user confirmation before executing
- if an operation fails, report the error clearly and suggest corrective action
- when operating on shared documents, report the current sharing status after changes
