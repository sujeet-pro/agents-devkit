# Sequence Diagram

**Directive:** `sequenceDiagram`

**Syntax:**

```
sequenceDiagram
    participant A as Alice
    participant B as Bob
    actor U as User

    A->>B: Synchronous message
    A-->>B: Dashed (async/response)
    A-xB: Cross (lost message)
    A-)B: Open arrow (async)

    activate B
    B->>A: Response
    deactivate B

    Note over A,B: Shared note
    Note right of B: Side note

    alt Condition
        A->>B: Path 1
    else Other
        A->>B: Path 2
    end

    loop Every minute
        A->>B: Heartbeat
    end

    par Parallel
        A->>B: Task 1
    and
        A->>C: Task 2
    end

    rect rgb(240, 240, 240)
        A->>B: Highlighted section
    end

    autonumber
```

**Example:**

```
%% Diagram: OAuth2 Authorization Code Flow
%% Type: sequence
sequenceDiagram
    autonumber
    actor user as User
    participant app as Client App
    participant auth as Auth Server
    participant api as Resource API

    user->>app: Click "Login"
    app->>auth: Authorization request (client_id, redirect_uri, scope)
    auth->>user: Show login form
    user->>auth: Enter credentials
    auth->>app: Authorization code (via redirect)
    app->>auth: Exchange code for token (code, client_secret)
    auth->>app: Access token + refresh token
    app->>api: API request (Bearer token)
    api->>app: Protected resource
    app->>user: Display data
```
