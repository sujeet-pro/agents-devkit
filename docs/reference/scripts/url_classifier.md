---
title: 'url_classifier.py'
description: 'url_classifier.py — classify URLs / paths / freeform in a prompt.'
script: 'url_classifier.py'
source: 'scripts/url_classifier.py'
group: 'scripts'
order: 4011
---
# url_classifier.py

url_classifier.py — classify URLs / paths / freeform in a prompt.

## Source

`scripts/url_classifier.py`

## Contents

```python
#!/usr/bin/env python3
"""url_classifier.py — classify URLs / paths / freeform in a prompt.

Usage:
  python3 scripts/url_classifier.py <text...>

Stdin also accepted:
  echo "<prompt>" | python3 scripts/url_classifier.py

Output: JSON to stdout.

Classification is purely structural — pattern matching on URL hostnames + paths.
No network calls.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

# (compiled_pattern, classifier_label)
URL_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"https?://[a-z0-9-]+\.atlassian\.net/(jira/[^/]+/)?browse/[A-Z][A-Z0-9]+-\d+", re.I), "jira-url"),
    (re.compile(r"https?://[a-z0-9-]+\.atlassian\.net/wiki/spaces/[^/]+/pages/\d+(?:/[^?\s]*)?", re.I), "confluence-url"),
    (re.compile(r"https?://github\.com/[^/]+/[^/]+/pull/\d+", re.I), "github-pr"),
    (re.compile(r"https?://github\.com/[^/]+/[^/]+/issues/\d+", re.I), "github-issue"),
    (re.compile(r"https?://github\.com/[^/]+/[^/]+/blob/[^/]+/\S+", re.I), "github-file"),
    (re.compile(r"https?://[a-z0-9-]+\.slack\.com/archives/[A-Z0-9]+/p\d+(?:\?[^\s]*)?", re.I), "slack-permalink"),
    (re.compile(r"https?://app\.datadoghq\.(?:com|eu|us3\.com|us5\.com|ap1\.com|ap2\.com)/incident/\d+", re.I), "datadog-incident"),
    (re.compile(r"https?://app\.datadoghq\.(?:com|eu|us3\.com|us5\.com|ap1\.com|ap2\.com)/monitors/\d+", re.I), "datadog-monitor"),
    (re.compile(r"https?://app\.datadoghq\.(?:com|eu|us3\.com|us5\.com|ap1\.com|ap2\.com)/dashboard/[a-z0-9-]+", re.I), "datadog-dashboard"),
    (re.compile(r"https?://app\.datadoghq\.(?:com|eu|us3\.com|us5\.com|ap1\.com|ap2\.com)/logs\?[^\s]+", re.I), "datadog-logs"),
    (re.compile(r"https?://app\.datadoghq\.(?:com|eu|us3\.com|us5\.com|ap1\.com|ap2\.com)/apm/(?:services/[^/?\s]+|trace/[a-f0-9]+)", re.I), "datadog-apm"),
    (re.compile(r"https?://console\.statsig\.com/[^/]+/(?:gates|experiments|metrics)/[^/?\s]+", re.I), "statsig"),
    (re.compile(r"https?://console\.statsig\.com/[^/]+/audit-log[^\s]*", re.I), "statsig-audit"),
    (re.compile(r"https?://[a-z0-9-]+\.cloud\.looker\.com/dashboards?/\d+", re.I), "looker-dashboard"),
    (re.compile(r"https?://[a-z0-9-]+\.app\.mixpanel\.com/project/\d+/(?:view|report|funnels|insights)/\d+", re.I), "mixpanel-report"),
    # generic URL last
    (re.compile(r"https?://\S+"), "url-other"),
]

# Path patterns
PATH_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^[~/]?[\w./-]+/$"), "directory"),
    (re.compile(r"^[~/]?[\w./-]+\.\w{1,8}$"), "file"),
    (re.compile(r"^\.$"), "cwd"),
    (re.compile(r"^[~/]?[\w./-]+\*\*?/?[\w./-]*$"), "glob"),
]

# Jira ticket key shorthand (not full URL): SF-1234, ABC-99
JIRA_KEY_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]+)-(\d+)\b")
# GH issue shorthand: #123 (require word boundary)
ISSUE_SHORTHAND = re.compile(r"(?<!\w)#(\d+)\b")


def classify_text(text: str) -> dict[str, Any]:
    urls: list[dict[str, str]] = []
    consumed: list[tuple[int, int]] = []

    for pattern, label in URL_PATTERNS:
        for m in pattern.finditer(text):
            span = (m.start(), m.end())
            if any(s <= span[0] < e for s, e in consumed):
                continue
            urls.append({"url": m.group(0), "type": label})
            consumed.append(span)
    consumed.sort()

    # Look for jira keys not inside a URL we already captured
    jira_keys: list[str] = []
    for m in JIRA_KEY_PATTERN.finditer(text):
        span = (m.start(), m.end())
        if any(s <= span[0] < e for s, e in consumed):
            continue
        jira_keys.append(m.group(0))

    # Issue shorthand
    issue_shorthands: list[str] = []
    for m in ISSUE_SHORTHAND.finditer(text):
        span = (m.start(), m.end())
        if any(s <= span[0] < e for s, e in consumed):
            continue
        issue_shorthands.append(m.group(0))

    # Local paths — anything that looks like a path, with cwd resolution
    local_paths: list[dict[str, str]] = []
    for tok in re.split(r"\s+", text):
        tok = tok.strip(".,;:!?\"'`()[]{}")
        if not tok or tok.startswith(("http://", "https://")):
            continue
        for pattern, label in PATH_PATTERNS:
            if pattern.match(tok):
                resolved = os.path.abspath(os.path.expanduser(tok)) if tok != "." else os.getcwd()
                local_paths.append({"raw": tok, "type": label, "resolved": resolved})
                break

    # Strip captured spans + tokens to get freeform residue
    masked = list(text)
    for s, e in consumed:
        for i in range(s, e):
            masked[i] = " "
    freeform = " ".join(filter(None, "".join(masked).split()))
    # Don't strip freeform further; downstream uses it as plain English

    return {
        "urls": urls,
        "jira_keys": jira_keys,
        "issue_shorthands": issue_shorthands,
        "local_paths": local_paths,
        "freeform": freeform,
    }


def main() -> int:
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    if not text.strip():
        print(json.dumps({"error": "empty input"}))
        return 1
    print(json.dumps(classify_text(text), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
