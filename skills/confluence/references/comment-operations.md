# Comment Operations

Confluence REST API v2 comment operations.

## Endpoints

### List Footer Comments

```
GET /wiki/api/v2/pages/{id}/footer-comments
```

Returns all footer (page-level) comments on the page.

### List Inline Comments

```
GET /wiki/api/v2/pages/{id}/inline-comments
```

Returns inline comments anchored to text selections.

### Create Footer Comment

```
POST /wiki/api/v2/footer-comments
```

Request body:
```json
{
  "pageId": "123456",
  "body": {
    "representation": "storage",
    "value": "<p>Comment text</p>"
  }
}
```

### Create Inline Comment

```
POST /wiki/api/v2/inline-comments
```

Request body:
```json
{
  "pageId": "123456",
  "body": {
    "representation": "storage",
    "value": "<p>Comment anchored to selected text</p>"
  },
  "inlineCommentProperties": {
    "textSelection": "the exact text to anchor to",
    "textSelectionMatchCount": 1,
    "textSelectionMatchIndex": 0
  }
}
```

- `textSelection`: the exact text string in the page body to attach the comment to.
- `textSelectionMatchCount`: how many times this text appears (set to actual count).
- `textSelectionMatchIndex`: zero-based index of which occurrence to anchor to.

### Reply to Comment

```
POST /wiki/api/v2/footer-comments
```

Request body:
```json
{
  "pageId": "123456",
  "body": {
    "representation": "storage",
    "value": "<p>Reply text</p>"
  },
  "parentCommentId": "789"
}
```

Replies to inline comments also use the footer-comments endpoint with `parentCommentId`.

### Get Comment

Footer:
```
GET /wiki/api/v2/footer-comments/{id}?body-format=storage
```

Inline:
```
GET /wiki/api/v2/inline-comments/{id}?body-format=storage
```

## Script Actions

```bash
comments.sh list-footer --page-id <pageId>
comments.sh list-inline --page-id <pageId>
comments.sh create-footer --page-id <pageId> --body "<p>comment</p>"
comments.sh create-inline --page-id <pageId> --body "<p>comment</p>" --text-selection "anchored text" [--match-index 0]
comments.sh reply --comment-id <commentId> --body "<p>reply</p>"
comments.sh get --comment-id <commentId> --type footer|inline
```

## Notes

- Comment bodies use the same Confluence storage format as pages.
- Inline comments require the anchored text to exist in the current page body. If the page is updated and the text changes, the inline comment may become orphaned.
- Reply threading: replies appear nested under the parent comment in the Confluence UI regardless of whether the parent is a footer or inline comment.
