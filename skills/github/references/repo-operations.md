# Repository Operations

## Get File Contents

```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '.content' | base64 -d
```

At a specific branch or ref:

```bash
gh api "repos/{owner}/{repo}/contents/{path}?ref={branch}" --jq '.content' | base64 -d
```

Get file metadata (size, sha, download URL):

```bash
gh api repos/{owner}/{repo}/contents/{path} --jq '{sha: .sha, size: .size, download_url: .download_url}'
```

List directory contents:

```bash
gh api repos/{owner}/{repo}/contents/{directory_path} --jq '.[].name'
```

## List Branches

```bash
gh api repos/{owner}/{repo}/branches --paginate --jq '.[].name'
```

With protection status:

```bash
gh api repos/{owner}/{repo}/branches --paginate --jq '.[] | {name: .name, protected: .protected}'
```

## Get Branch

```bash
gh api repos/{owner}/{repo}/branches/{branch} --jq '{name: .name, sha: .commit.sha, protected: .protected}'
```

## Search Code

```bash
gh search code "query" --repo {owner}/{repo}
```

With language filter:

```bash
gh search code "query" --repo {owner}/{repo} --language typescript
```

With path filter:

```bash
gh search code "query" --repo {owner}/{repo} --filename "*.ts"
```

JSON output:

```bash
gh search code "query" --repo {owner}/{repo} --json path,repository,textMatches
```

## List Commits

```bash
gh api repos/{owner}/{repo}/commits --jq '.[] | {sha: .sha, message: .commit.message, date: .commit.author.date}'
```

On a specific branch:

```bash
gh api "repos/{owner}/{repo}/commits?sha={branch}" --jq '.[] | {sha: .sha, message: .commit.message}'
```

With pagination:

```bash
gh api "repos/{owner}/{repo}/commits?sha={branch}&per_page=50" --paginate --jq '.[].sha'
```

## Get Commit

```bash
gh api repos/{owner}/{repo}/commits/{sha} --jq '{sha: .sha, message: .commit.message, author: .commit.author.name, files: [.files[].filename]}'
```

With diff stats:

```bash
gh api repos/{owner}/{repo}/commits/{sha} --jq '{sha: .sha, stats: .stats, files: [.files[] | {name: .filename, status: .status, additions: .additions, deletions: .deletions}]}'
```

## Compare Branches

```bash
gh api repos/{owner}/{repo}/compare/{base}...{head}
```

Files changed:

```bash
gh api repos/{owner}/{repo}/compare/{base}...{head} --jq '.files[] | {filename: .filename, status: .status, additions: .additions, deletions: .deletions}'
```

Commits between branches:

```bash
gh api repos/{owner}/{repo}/compare/{base}...{head} --jq '.commits[] | {sha: .sha, message: .commit.message}'
```

Summary:

```bash
gh api repos/{owner}/{repo}/compare/{base}...{head} --jq '{ahead_by: .ahead_by, behind_by: .behind_by, total_commits: .total_commits}'
```

## Get Repo Info

```bash
gh repo view --json name,owner,description,defaultBranchRef,url,isPrivate,languages
```

With specific fields:

```bash
gh repo view --json name,defaultBranchRef --jq '{name: .name, default_branch: .defaultBranchRef.name}'
```
