---
name: image-transform
description: Convert SVG images to JPEG using sharp. Standalone utility for image format conversion, used by diagram skills and confluence-publish.
user_invocable: true
arguments:
  - name: input
    description: "Path to input SVG file"
    required: true
  - name: output
    description: "Path to output JPEG file (default: input with .jpg extension)"
    required: false
  - name: quality
    description: "JPEG quality 1-100 (default: 90)"
    required: false
  - name: density
    description: "SVG rasterization DPI (default: 300)"
    required: false
  - name: width
    description: "Output width in pixels (default: auto from SVG)"
    required: false
  - name: background
    description: "Background color for transparent SVGs (default: white)"
    required: false
---

# Image Transform

Convert SVG images to JPEG format using `sharp`. This is a standalone, composable utility used by diagram skills, confluence-publish, and any workflow that needs raster images from vector sources.

## When This Skill Is Used

- **Confluence publishing**: Confluence renders JPEG attachments reliably; SVG support is inconsistent.
- **Google Docs**: Requires raster images for embedding.
- **Email / Slack**: Most messaging platforms need JPEG/PNG, not SVG.
- **Print / PDF**: When SVG rendering varies across PDF generators.
- **Any context where SVG is not supported or renders inconsistently.**

## Prerequisites

`sharp` must be available. It can be used via:
- Project-local: `npm install sharp` in the current project
- Global: `npm install -g sharp` (less common)
- Via npx: Run the conversion script with `npx` (will auto-install sharp temporarily)

If sharp is not available, inform the user:
> `sharp` is required for SVG→JPEG conversion. Install it with `npm install sharp` or use `npx`.

## Conversion Script

Create a temporary Node.js script for the conversion. The script handles SVG quirks (missing dimensions, transparent backgrounds) automatically.

```javascript
#!/usr/bin/env node
// svg-to-jpeg.mjs — Temporary conversion script
import sharp from 'sharp';
import { readFileSync, writeFileSync } from 'fs';

const [inputPath, outputPath, quality = '90', density = '300', bgColor = 'white'] = process.argv.slice(2);

if (!inputPath) {
  console.error('Usage: node svg-to-jpeg.mjs <input.svg> [output.jpg] [quality] [density] [bgColor]');
  process.exit(1);
}

const output = outputPath || inputPath.replace(/\.svg$/i, '.jpg');

let svgBuffer = readFileSync(inputPath);

// Ensure SVG has explicit dimensions for sharp
let svgString = svgBuffer.toString('utf-8');
if (!svgString.match(/\bwidth\s*=\s*["']\d/)) {
  // If SVG has viewBox but no width/height, add default dimensions
  const viewBoxMatch = svgString.match(/viewBox\s*=\s*["'][\d.\s]+\s+[\d.\s]+\s+([\d.]+)\s+([\d.]+)["']/);
  if (viewBoxMatch) {
    const [, vbWidth, vbHeight] = viewBoxMatch;
    svgString = svgString.replace('<svg', `<svg width="${vbWidth}" height="${vbHeight}"`);
    svgBuffer = Buffer.from(svgString);
  }
}

await sharp(svgBuffer, { density: parseInt(density) })
  .flatten({ background: bgColor })
  .jpeg({
    quality: parseInt(quality),
    mozjpeg: true,
    chromaSubsampling: '4:4:4', // Prevent color bleeding on diagrams with sharp text/lines
  })
  .toFile(output);

console.log(`Converted: ${inputPath} → ${output}`);
```

## Workflow

### Step 1: Validate Input

1. Check that the input file exists and has a `.svg` extension.
2. Determine the output path (default: replace `.svg` with `.jpg`).
3. Set quality and density defaults if not provided.

### Step 2: Write Temporary Script

Write the conversion script to a temporary location:

```bash
cat > /tmp/svg-to-jpeg.mjs << 'SCRIPT'
<script content above>
SCRIPT
```

### Step 3: Run Conversion

```bash
node /tmp/svg-to-jpeg.mjs "<input.svg>" "<output.jpg>" <quality> <density> "<background>"
```

If the project has `sharp` installed locally:
```bash
node /tmp/svg-to-jpeg.mjs input.svg output.jpg 90 300 white
```

If not, use npx:
```bash
npx --yes -p sharp node /tmp/svg-to-jpeg.mjs input.svg output.jpg 90 300 white
```

### Step 4: Report

```
Image converted:
  Input:      ./diagrams/architecture.svg
  Output:     ./diagrams/architecture.jpg
  Quality:    90
  Density:    300 DPI
  Background: white
```

### Step 5: Cleanup

Remove the temporary script after conversion.

## Sharp Options Reference

### Quality Settings

| Use Case | Quality | Density | Notes |
|----------|---------|---------|-------|
| Web / markdown | 85 | 150 | Good balance of size and quality |
| Confluence | 90 | 300 | Higher quality for wiki rendering |
| Print / PDF | 95 | 300 | Maximum quality |
| Thumbnails | 70 | 72 | Small file size |

### Background Colors

- `white` — Default, safe for most contexts
- `transparent` — Not supported in JPEG (falls back to black); use PNG instead
- Any CSS color — e.g., `#f8f9fa` for light gray

### chromaSubsampling

Always use `'4:4:4'` for diagrams. The default `'4:2:0'` causes color bleeding at sharp edges (text, lines, boxes), which makes diagram text look blurry.

## Composability

This skill is called by other skills:

- **`/diagram`**: Calls `/image-transform` when `format=jpeg` or `target=confluence`.
- **`/confluence-publish`**: Calls `/image-transform` for all SVG images before uploading.
- **`/doc-write`**: Calls `/image-transform` when `format=confluence` or `format=google-doc`.
- **Standalone**: User invokes directly to convert any SVG to JPEG.

## Batch Conversion

When multiple SVGs need conversion (e.g., a document with several diagrams), process them in parallel:

```bash
# Convert all SVGs in a directory
for svg in ./diagrams/*.svg; do
  node /tmp/svg-to-jpeg.mjs "$svg" &
done
wait
```

Or sequentially if system resources are limited:

```bash
for svg in ./diagrams/*.svg; do
  node /tmp/svg-to-jpeg.mjs "$svg"
done
```
