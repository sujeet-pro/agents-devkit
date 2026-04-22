# `validate-browser` — interaction-test script format

A YAML or markdown file. Each step has: action, selector, optional value, optional assertion.

## YAML form

```yaml
target: http://localhost:5173/dashboard
viewport: { width: 1280, height: 800 }
steps:
  - action: navigate
    target: http://localhost:5173/dashboard
  - action: click
    selector: 'button[aria-label="Open menu"]'
    assert:
      visible: '[role="menu"]'
  - action: type
    selector: 'input[name="email"]'
    text: 'alice@example.com'
  - action: click
    selector: 'button[type="submit"]'
    assert:
      text: 'Welcome, Alice'
      url-contains: '/home'
  - action: wait
    ms: 500
  - action: screenshot
    name: 'after-login'
```

## Markdown form (more readable for hand-authored scripts)

```markdown
# interaction-test

target: http://localhost:5173/dashboard
viewport: 1280x800

## steps

1. **navigate** to target
2. **click** `button[aria-label="Open menu"]` — assert `[role="menu"]` visible
3. **type** "alice@example.com" into `input[name="email"]`
4. **click** `button[type="submit"]` — assert text "Welcome, Alice", url contains "/home"
5. **wait** 500ms
6. **screenshot** "after-login"
```

The skill parses both formats. YAML preferred for CI; markdown preferred for hand-writing.
