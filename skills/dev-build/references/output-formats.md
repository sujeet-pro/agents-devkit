# DevKit Output Formats

DevKit skills should support these output targets whenever the source material allows it.

## Documents

- **Markdown**: default source of truth.
- **Google Docs**: publish or update through Google Drive MCP.
- **Confluence**: publish or update through the Confluence MCP.
- **PDF**: export from markdown or HTML with local free tooling when available.

## Diagrams

- **Mermaid**: `.mermaid`, `.mmd`
- **Excalidraw**: `.excalidraw`
- **draw.io**: `.drawio`, `.drawio.xml`

For each generated diagram, keep both:

- the editable source file
- at least one rendered artifact, preferably SVG

Use PNG or JPEG only when the destination does not handle SVG well.

## Review Deliverables

Every review should be able to produce:

- a markdown report
- source comments when supported
- an executive summary section for handoff or reposting
