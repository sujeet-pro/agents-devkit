# Anti-patterns: adk-doc-site-setup

- Skipping the confirm-intent gate on a non-trivial setup that overwrites existing config or scaffolds on top of existing docs.
- Producing output without running `pagesmith-docs build` and `diagramkit validate` for evidence.
- Letting scope creep replace the user's actual ask (e.g. designing custom layouts when they only asked to scaffold).
- Inventing config keys not present in `node_modules/@pagesmith/docs/schemas/*` or `node_modules/diagramkit/schemas/*`.
- Skipping the install of `prj-doc-site-*` skills because the user "didn't ask for them" — they are the durable handoff.
- Installing `sharp` when only SVG output is needed (raster output is opt-in).
- Running `diagramkit warmup` on a Graphviz-only repo (Graphviz is WASM, no browser).
- Promoting working artifacts (plan, draft scaffold, scratch markdown) out of `.temp/` before they are the deliverable.
- Hand-editing rendered SVGs in `.diagramkit/` instead of editing the source and re-rendering.
- Hardcoding `%%{init: {theme: ...}}%%` in Mermaid sources — diagramkit controls theme injection.
- Setting `pagesmith.config.json5` `origin` to `http://localhost`. Use the real production origin even for local builds.
- Using absolute paths in `contentDir`. Always relative to the config file.
- Mixing two skill-install mechanisms (this skill's `prj-*` install AND `npx skills add sujeet-pro/diagramkit`) in the same repo.
- Treating the inline references in this skill as authoritative. They are fallbacks; `node_modules/<pkg>/REFERENCE.md` wins on conflict.
