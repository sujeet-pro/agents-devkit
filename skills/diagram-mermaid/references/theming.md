# Mermaid Theming & Dark Mode

## How diagramkit Handles Dark Mode

When rendering with `diagramkit render`, Mermaid diagrams get automatic light/dark mode variants:

1. **Light mode**: Rendered with Mermaid's default theme. Output: `diagram-light.svg`
2. **Dark mode**: Rendered with the `dark` theme, then processed through `postProcessDarkSvg` which:
   - Adjusts the background to a dark surface color
   - Transforms text colors for WCAG-compliant contrast
   - Modifies element fills to maintain visual hierarchy on dark backgrounds
   - Adjusts stroke colors to be visible without being harsh

Output: `diagram-dark.svg`

## Theme Configuration

Mermaid supports inline theme configuration via directives:

```
%%{init: {'theme': 'default'}}%%
flowchart TD
    A --> B
```

Available themes: `default`, `dark`, `forest`, `neutral`, `base`.

**Do not set the theme manually** — diagramkit handles theme selection during rendering. Setting it inline will prevent correct dark mode generation.

## Custom Theming with `classDef`

Use `classDef` to style node groups consistently without hardcoding colors into individual nodes:

```
flowchart TD
    A[API Gateway]:::primary --> B[Auth Service]:::secondary
    A --> C[User Service]:::secondary
    B --> D[(Database)]:::storage
    C --> D

    classDef primary fill:#4C78A8,stroke:#2E5A88,color:#fff
    classDef secondary fill:#72B7B2,stroke:#4A9A95,color:#fff
    classDef storage fill:#E4A847,stroke:#C08C35,color:#fff
```

### Colors That Work in Both Modes

Mid-tone colors survive dark mode transformations best. Avoid very light fills (near white) and very dark fills (near black).

| Purpose | Fill | Stroke | Notes |
|---------|------|--------|-------|
| Primary (blue) | `#4C78A8` | `#2E5A88` | Good contrast both modes |
| Secondary (teal) | `#72B7B2` | `#4A9A95` | Good contrast both modes |
| Accent (coral) | `#E45756` | `#C23B3A` | Stands out in both modes |
| Storage (amber) | `#E4A847` | `#C08C35` | Warm, distinct |
| Success (green) | `#54A24B` | `#3D8B3D` | Earthy green |
| Neutral (gray) | `#9B9B9B` | `#7B7B7B` | Low emphasis |

### Colors to Avoid

- `#ffffff` or near-white fills — become invisible on light backgrounds, look odd when darkened
- `#000000` or near-black fills — invisible on dark backgrounds
- Very saturated neons — may produce harsh contrast after transformation
- Named colors (`red`, `blue`) — Mermaid theme engine only accepts hex

## Subgraph Styling

Subgraphs accept limited styling:

```
flowchart TD
    subgraph api["API Layer"]
        style api fill:#f0f4f8,stroke:#4C78A8,stroke-width:2px
        gateway[Gateway] --> service[Service]
    end
```

For dark mode compatibility, use light translucent fills for subgraph backgrounds rather than solid whites.

## Edge Styling

Edges inherit from the theme. For custom edge styles, use `linkStyle`:

```
flowchart TD
    A --> B
    A -.-> C
    linkStyle 0 stroke:#4C78A8,stroke-width:2px
    linkStyle 1 stroke:#E45756,stroke-width:1px,stroke-dasharray:5
```

Edge style indices are 0-based in order of definition.
