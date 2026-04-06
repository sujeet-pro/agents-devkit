# Quadrant Chart

**Directive:** `quadrantChart`

**Syntax:**

```
quadrantChart
    title Chart Title
    x-axis Low --> High
    y-axis Low --> High
    quadrant-1 Label (top-right)
    quadrant-2 Label (top-left)
    quadrant-3 Label (bottom-left)
    quadrant-4 Label (bottom-right)
    Item A: [0.8, 0.9]
    Item B: [0.3, 0.7]
```

**Example:**

```
%% Diagram: Technical Debt Prioritization
%% Type: quadrant
quadrantChart
    title Technical Debt Priority Matrix
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    quadrant-1 Do First
    quadrant-2 Plan Carefully
    quadrant-3 Deprioritize
    quadrant-4 Quick Wins
    Upgrade Node.js: [0.3, 0.9]
    Fix N+1 queries: [0.4, 0.8]
    Migrate to TypeScript: [0.9, 0.7]
    Update lint rules: [0.2, 0.3]
    Refactor auth module: [0.7, 0.85]
    Add API versioning: [0.6, 0.5]
    Remove dead code: [0.15, 0.4]
```
