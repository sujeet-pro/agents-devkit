# Export to PNG/SVG

Two methods for exporting `.excalidraw` files to rendered images.

---

## Method 1: excalidraw-to-svg (Recommended)

The simplest approach. Works in pure Node.js with no browser needed.

### Prerequisites

```bash
npm install -g excalidraw-to-svg
```

### Usage

```bash
# CLI
npx excalidraw-to-svg ./diagram.excalidraw ./output.svg

# Programmatic
const excalidrawToSvg = require("excalidraw-to-svg");
const fs = require("fs");

const diagram = JSON.parse(fs.readFileSync("diagram.excalidraw", "utf-8"));
const svgElement = await excalidrawToSvg(diagram);
fs.writeFileSync("output.svg", svgElement.outerHTML);
```

### How It Works

- Uses `jsdom` to create an isolated DOM environment
- Loads `@excalidraw/utils` UMD bundle inside JSDOM
- Includes `Path2D` polyfill and `CanvasRenderingContext2D` mock
- Calls `ExcalidrawUtils.exportToSvg()` inside the JSDOM context
- Returns the SVG as a DOM element

### Converting SVG to JPEG

After producing SVG, use the `/image-transform` skill or `sharp` directly:

```javascript
const sharp = require("sharp");

await sharp(Buffer.from(svgString), { density: 300 })
  .flatten({ background: "white" })
  .jpeg({ quality: 90, mozjpeg: true, chromaSubsampling: "4:4:4" })
  .toFile("output.jpg");
```

---

## Method 2: Playwright MCP (Higher Fidelity)

Uses a real browser for pixel-perfect rendering. Requires Playwright MCP tools.

### Prerequisites

- Playwright MCP tools available: `browser_navigate`, `browser_run_code`, `browser_close`
- Python 3 installed (for local HTTP server)

### Procedure

#### 1. Start a Local HTTP Server

A browser origin is required for dynamic ESM imports:

```bash
python3 -m http.server 8765 &
SERVER_PID=$!
```

#### 2. Navigate Playwright to the Server

```
browser_navigate → http://localhost:8765/
```

The 404 page is fine — we only need the HTTP origin for the dynamic import.

#### 3. Read the .excalidraw File

Use the Read tool to get the `.excalidraw` file contents as a JSON string.

#### 4. Export SVG

Use `browser_run_code` with the `.excalidraw` JSON inserted:

```javascript
async (page) => {
  const excalidrawJson = `EXCALIDRAW_JSON_HERE`;

  const svgString = await page.evaluate(async (json) => {
    const utils = await import('https://esm.sh/@excalidraw/utils@0.1.2');
    const { exportToSvg } = utils.default;
    const data = JSON.parse(json);
    const svg = await exportToSvg({
      elements: data.elements,
      appState: { ...data.appState, exportBackground: true },
      files: data.files || {}
    });
    return svg.outerHTML;
  }, excalidrawJson);

  return svgString;
}
```

Write the returned SVG string to `<filename>.svg`.

#### 5. Export PNG

```javascript
async (page) => {
  const excalidrawJson = `EXCALIDRAW_JSON_HERE`;

  const pngBase64 = await page.evaluate(async (json) => {
    const utils = await import('https://esm.sh/@excalidraw/utils@0.1.2');
    const { exportToBlob } = utils.default;
    const data = JSON.parse(json);
    const blob = await exportToBlob({
      elements: data.elements,
      appState: { ...data.appState, exportBackground: true },
      files: data.files || {},
      mimeType: 'image/png'
    });
    const reader = new FileReader();
    return new Promise((resolve) => {
      reader.onloadend = () => resolve(reader.result);
      reader.readAsDataURL(blob);
    });
  }, excalidrawJson);

  return pngBase64;
}
```

Decode and write to file:

```bash
echo "<base64_data_without_prefix>" | base64 -d > <filename>.png
```

Strip the `data:image/png;base64,` prefix before decoding.

#### 6. Clean Up

```
browser_close
```

```bash
kill $SERVER_PID
```

### Key Details

- **Import path**: Export functions are on `utils.default`, not named exports (esm.sh wrapping)
- **Console errors**: `<text> attribute y: Expected length` warnings are cosmetic — exports are valid
- **Background**: `exportBackground: true` includes the white background
- **Visual fidelity**: Both exports produce the same output as excalidraw.com

### Troubleshooting

| Issue | Fix |
|-------|-----|
| Port already in use | Try a different port: `python3 -m http.server 9876 &` |
| Dynamic import fails | Check network connectivity; `esm.sh` CDN must be reachable |
| Playwright tools not available | Use Method 1 (excalidraw-to-svg) instead |
| PNG is blank/corrupted | Verify the base64 prefix was stripped before decoding |
| SVG missing text | Cosmetic only — text renders correctly in a browser |

---

## Method Comparison

| Aspect | excalidraw-to-svg | Playwright MCP |
|--------|-------------------|----------------|
| **Setup** | `npm install -g excalidraw-to-svg` | Playwright MCP configured |
| **Dependencies** | jsdom (pure JS) | Headless browser |
| **Fidelity** | Good | Best (real browser) |
| **Speed** | Fast | Slower (browser startup) |
| **Formats** | SVG only (use sharp for JPEG) | SVG + PNG natively |
| **Offline** | Yes | Needs esm.sh CDN |
| **Complexity** | Low | Medium |

**Recommendation:** Use Method 1 (excalidraw-to-svg) by default. Fall back to Method 2 (Playwright) when higher fidelity is needed or when excalidraw-to-svg is not available but Playwright MCP is.
