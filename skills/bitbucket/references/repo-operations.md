# Repository Operations

All operations use script `scripts/repo.sh`.

## get

Get repository metadata.

```bash
bash scripts/repo.sh get <workspace> <repo>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}`

**Response fields**: `full_name`, `description`, `is_private`, `language`, `mainbranch.name`, `size`, `created_on`, `updated_on`

## file

Get file contents at a specific ref.

```bash
bash scripts/repo.sh file <workspace> <repo> --path src/main.py [--ref main]
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/src/{ref}/{path}`

Default ref: `main`. Returns raw file contents (not JSON).

## branches

List branches.

```bash
bash scripts/repo.sh branches <workspace> <repo>
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/refs/branches`

**Response fields per branch**: `name`, `target.hash`, `target.date`, `target.message`

## commits

List commits, optionally filtered by branch.

```bash
bash scripts/repo.sh commits <workspace> <repo> [--branch main]
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/commits[/{branch}]`

**Response fields per commit**: `hash`, `message`, `author.raw`, `date`, `parents[].hash`

## diff

Compare two refs (branches or commits).

```bash
bash scripts/repo.sh diff <workspace> <repo> --spec main..feature-branch
```

**Endpoint**: `GET /2.0/repositories/{workspace}/{repo}/diff/{spec}`

Returns raw unified diff text (not JSON).
