# GitGraph

**Directive:** `gitGraph`

**Syntax:**

```
gitGraph
    commit id: "initial"
    branch develop
    checkout develop
    commit id: "feature-start"
    branch feature/auth
    checkout feature/auth
    commit id: "add-login"
    commit id: "add-signup"
    checkout develop
    merge feature/auth id: "merge-auth"
    checkout main
    merge develop id: "release-1.0" tag: "v1.0"
```

**Example:**

```
%% Diagram: Git Branching Strategy
%% Type: gitgraph
gitGraph
    commit id: "init"
    branch develop
    commit id: "setup-ci"
    branch feature/user-auth
    commit id: "auth-models"
    commit id: "auth-routes"
    commit id: "auth-tests"
    checkout develop
    merge feature/user-auth id: "merge-auth"
    branch feature/dashboard
    commit id: "dashboard-ui"
    commit id: "dashboard-api"
    checkout develop
    merge feature/dashboard id: "merge-dashboard"
    checkout main
    merge develop id: "release" tag: "v1.0.0"
    branch hotfix/security
    commit id: "patch-xss"
    checkout main
    merge hotfix/security id: "hotfix" tag: "v1.0.1"
    checkout develop
    merge hotfix/security id: "sync-hotfix"
```
