# Page Operations

Confluence REST API v2 page operations.

## Endpoints

### Get Page

```
GET /wiki/api/v2/pages/{id}?body-format=storage
```

Returns full page including HTML body in Confluence storage format.

Response shape:
```json
{
  "id": "123456",
  "status": "current",
  "title": "Page Title",
  "spaceId": "789",
  "version": { "number": 5, "message": "Edit summary" },
  "body": { "storage": { "representation": "storage", "value": "<p>HTML content</p>" } }
}
```

### Get Page by Title

```
GET /wiki/api/v2/pages?title={title}&space-id={spaceId}&body-format=storage
```

Returns matching pages. Title match is exact.

### Search Pages

```
GET /wiki/api/v2/pages?title={query}&space-id={spaceId}&limit={limit}
```

For full-text search, use CQL via v1:
```
GET /wiki/rest/api/content/search?cql=type=page AND space="{spaceKey}" AND text~"{query}"
```

### Create Page

```
POST /wiki/api/v2/pages
```

Request body:
```json
{
  "spaceId": "789",
  "status": "current",
  "title": "New Page Title",
  "parentId": "123456",
  "body": {
    "representation": "storage",
    "value": "<p>Page content in Confluence storage format</p>"
  }
}
```

`parentId` is optional — omit to create at the space root.

### Update Page

```
PUT /wiki/api/v2/pages/{id}
```

Request body:
```json
{
  "id": "123456",
  "status": "current",
  "title": "Updated Title",
  "body": {
    "representation": "storage",
    "value": "<p>Updated content</p>"
  },
  "version": {
    "number": 6,
    "message": "What changed"
  }
}
```

**Version number must increment.** Fetch the current page first, read `version.number`, and set the new version to `N+1`.

### Delete Page

```
DELETE /wiki/api/v2/pages/{id}
```

Returns 204 on success.

### Get Children

```
GET /wiki/api/v2/pages/{id}/children
```

Returns direct child pages.

### Get Labels

```
GET /wiki/api/v2/pages/{id}/labels
```

### Add Label

```
POST /wiki/api/v2/pages/{id}/labels
```

Request body (array):
```json
[{ "prefix": "global", "name": "label-name" }]
```

## Script Actions

```bash
pages.sh get --id <pageId>
pages.sh get-by-title --title "Page Title" --space-id <spaceId>
pages.sh search --query "search term" [--space-id <spaceId>] [--limit 25]
pages.sh create --space-id <spaceId> --title "Title" --body "<p>content</p>" [--parent-id <parentId>]
pages.sh update --id <pageId> --title "Title" --body "<p>new content</p>" [--version <N>]
pages.sh delete --id <pageId>
pages.sh children --id <pageId>
pages.sh labels --id <pageId>
pages.sh add-label --id <pageId> --label "label-name"
```

## Notes

- Body content uses Confluence storage format (XHTML-like). Common elements:
  - `<p>`, `<h1>`–`<h6>`, `<ul>`, `<ol>`, `<li>`, `<table>`, `<tr>`, `<th>`, `<td>`
  - `<ac:structured-macro>` for macros
  - `<ri:attachment ri:filename="image.png"/>` for inline images
  - `<ac:image><ri:attachment ri:filename="image.png"/></ac:image>` for displayed images
- When updating, always include the full body content, not just the diff.
