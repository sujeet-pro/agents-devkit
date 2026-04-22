# `doc-site-setup` — how it works

```mermaid
flowchart TD
    Start["doc-site-setup"] --> Check{"package.json + Node 24+?"}
    Check -- no --> Fail
    Check -- yes --> Install["npm add @pagesmith/docs"]
    Install --> ReadRef["READ node_modules/@pagesmith/docs/REFERENCE.md (mandatory)"]
    ReadRef --> Init["npx pagesmith-docs init --yes --ai"]
    Init --> Verify["pagesmith.config.json5 + docs/ + scripts"]
    Verify --> Smoke1["npm run docs:build"]
    Smoke1 --> Smoke2["npm run docs:dev (curl smoke test)"]
    Smoke2 --> DeployQ{"GitHub Pages?"}
    DeployQ -- yes --> Deploy["Hand off to pagesmith-docs-deploy-gh-pages"]
    DeployQ -- no --> Diag
    Deploy --> Diag{"Diagrams?"}
    Diag -- yes --> DiagSetup["Hand off to @adk:doc-site-diagrams"]
    Diag -- no --> SkillPack
    DiagSetup --> SkillPack["npx pagesmith-core skills (install pagesmith skill pack into consumer)"]
    SkillPack --> Done["Final report"]
```

## Delegation map

```mermaid
flowchart LR
    Setup["doc-site-setup"] --> Add["pagesmith-docs-add-page"]
    Setup --> Nav["pagesmith-docs-configure-nav"]
    Setup --> Theme["pagesmith-docs-customize-theme"]
    Setup --> Search["pagesmith-docs-add-search"]
    Setup --> Deploy["pagesmith-docs-deploy-gh-pages"]
    Setup --> Gen["pagesmith-generate-docs"]
    Setup --> Diagrams["@adk:doc-site-diagrams (wraps diagramkit)"]
```

This skill ONLY bootstraps. All ongoing work (add a page, configure nav, customize theme, add search, deploy, generate from sources, render diagrams) is done by the delegate skills.
