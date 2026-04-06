# Attachment Operations

Confluence REST API v1 for attachment operations (v2 does not support file upload).

## Endpoints

### List Attachments

```
GET /wiki/rest/api/content/{id}/child/attachment
```

Response includes attachment metadata with download links:
```json
{
  "results": [
    {
      "id": "att123",
      "title": "image.png",
      "metadata": { "mediaType": "image/png" },
      "_links": { "download": "/wiki/download/attachments/123456/image.png" }
    }
  ]
}
```

### Upload Attachment

```
POST /wiki/rest/api/content/{id}/child/attachment
```

**Must use multipart/form-data.** Requires `X-Atlassian-Token: nocheck` header.

```bash
curl -X POST \
  -u user:token \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@/path/to/image.png" \
  -F "comment=Description of the file" \
  "${CONFLUENCE_URL}/wiki/rest/api/content/${pageId}/child/attachment"
```

If an attachment with the same filename already exists, this creates a new version of it.

### Update Attachment

```
POST /wiki/rest/api/content/{id}/child/attachment/{attachmentId}/data
```

Replaces the file data for an existing attachment.

```bash
curl -X POST \
  -u user:token \
  -H "X-Atlassian-Token: nocheck" \
  -F "file=@/path/to/updated-image.png" \
  "${CONFLUENCE_URL}/wiki/rest/api/content/${pageId}/child/attachment/${attachmentId}/data"
```

### Download Attachment

Construct the full URL from the `_links.download` field returned by list:

```
GET ${CONFLUENCE_URL}{_links.download}
```

Save to a file with curl `-o` flag.

## Script Actions

```bash
attachments.sh list --page-id <pageId>
attachments.sh upload --page-id <pageId> --file /path/to/file.png [--comment "description"]
attachments.sh update --page-id <pageId> --attachment-id <attId> --file /path/to/new-file.png
attachments.sh download --page-id <pageId> --attachment-id <attId> --output /path/to/save.png
```

## Notes

- The `X-Atlassian-Token: nocheck` header is required for all upload/update operations to bypass XSRF protection.
- Maximum attachment size depends on your Confluence instance configuration (default: 100MB for Cloud).
- To embed an uploaded image in a page, update the page body to include:
  ```html
  <ac:image><ri:attachment ri:filename="image.png"/></ac:image>
  ```
- Attachment filenames must be unique per page. Uploading a file with the same name creates a new version, not a duplicate.
