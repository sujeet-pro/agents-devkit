# User Journey

**Directive:** `journey`

**Syntax:**

```
journey
    title Journey Title
    section Phase
        Task: score: actor1, actor2
```

Score: 1 (worst) to 5 (best).

**Example:**

```
%% Diagram: User Onboarding Journey
%% Type: journey
journey
    title New User Onboarding
    section Discovery
        Visit landing page: 5: User
        Read pricing: 3: User
        Compare plans: 3: User
    section Signup
        Create account: 4: User
        Verify email: 2: User
        Complete profile: 3: User
    section First Use
        View dashboard: 4: User
        Create first project: 3: User, System
        Invite team member: 4: User
    section Activation
        Complete tutorial: 5: User, System
        First successful build: 5: User
```
