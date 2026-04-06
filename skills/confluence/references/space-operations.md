# Space Operations

Confluence REST API v2 space operations.

## Endpoints

### List Spaces

```
GET /wiki/api/v2/spaces?limit={limit}
```

Returns all spaces the authenticated user can see. Default limit is 25.

Response shape:
```json
{
  "results": [
    {
      "id": "789",
      "key": "PROJ",
      "name": "Project Space",
      "type": "global",
      "status": "current"
    }
  ]
}
```

### Get Space by ID

```
GET /wiki/api/v2/spaces/{id}
```

### Get Space by Key

```
GET /wiki/api/v2/spaces?keys={key}
```

Returns spaces matching the given key. Space keys are uppercase short identifiers (e.g., `ENG`, `DOCS`).

## Script Actions

```bash
spaces.sh list [--limit 25]
spaces.sh get --id <spaceId>
spaces.sh get --key <spaceKey>
```

## Notes

- Space keys are unique, uppercase identifiers assigned at creation.
- Use space IDs (numeric) when calling page APIs that require `spaceId`.
- To find a space ID from a key, use `spaces.sh get --key <KEY>` and read the `id` field.
