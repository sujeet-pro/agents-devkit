# Project Operations

Jira REST API v3 — `${JIRA_URL}/rest/api/3`

## List Projects

```
GET /rest/api/3/project
```

Query parameters:
- `expand` — `lead`, `description`, `url`
- `recent` — number of recent projects to return
- `orderBy` — field to order by

Response: array of project objects with `key`, `name`, `id`, `projectTypeKey`

Script: `bash scripts/projects.sh list`

## Get Project

```
GET /rest/api/3/project/{projectIdOrKey}
```

Query parameters:
- `expand` — `description`, `lead`, `url`, `issueTypes`

Response includes: `id`, `key`, `name`, `description`, `lead`, `projectTypeKey`, `issueTypes`

Script: `bash scripts/projects.sh get --key PROJ`

## List Versions

```
GET /rest/api/3/project/{projectIdOrKey}/versions
```

Response: array of version objects with `id`, `name`, `released`, `releaseDate`, `archived`

Script: `bash scripts/projects.sh versions --key PROJ`

## Create Version

```
POST /rest/api/3/version
```

Body:
```json
{
  "name": "1.0.0",
  "projectId": 10000,
  "released": false,
  "releaseDate": "2024-06-01"
}
```

Returns created version object.

Script: `bash scripts/projects.sh create-version --project-id 10000 --name "1.0.0" [--release-date "2024-06-01"] [--released false]`

## List Components

```
GET /rest/api/3/project/{projectIdOrKey}/components
```

Response: array of component objects with `id`, `name`, `lead`, `assigneeType`

Script: `bash scripts/projects.sh components --key PROJ`

## Create Component

```
POST /rest/api/3/component
```

Body:
```json
{
  "name": "API",
  "project": "PROJ",
  "leadAccountId": "5b10a2844c20165700ede21g"
}
```

Returns created component object.

Script: `bash scripts/projects.sh create-component --project PROJ --name "API" [--lead accountId]`

## Get Statuses

```
GET /rest/api/3/project/{projectIdOrKey}/statuses
```

Response: array of issue types, each with `statuses` array containing `id`, `name`, `statusCategory`

Script: `bash scripts/projects.sh statuses --key PROJ`
