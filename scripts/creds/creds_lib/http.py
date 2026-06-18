"""Tiny stdlib HTTP helper — no third-party deps.

``request`` never raises on a non-2xx status; it returns
``(status, headers, body_text)`` so callers can branch on the code. A
network/SSL failure surfaces as status ``0`` with the reason in the body.
"""

from __future__ import annotations

import base64
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: dict[str, Any] | bytes | None = None,
    json_body: Any = None,
    timeout: float = 20.0,
) -> tuple[int, dict[str, str], str]:
    hdrs = dict(headers or {})
    if params:
        sep = "&" if "?" in url else "?"
        url = url + sep + urllib.parse.urlencode(params)

    body: bytes | None = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    elif isinstance(data, dict):
        body = urllib.parse.urlencode(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/x-www-form-urlencoded")
    elif isinstance(data, (bytes, bytearray)):
        body = bytes(data)

    req = urllib.request.Request(url, data=body, method=method.upper(), headers=hdrs)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, dict(e.headers or {}), raw
    except urllib.error.URLError as e:
        return 0, {}, f"URLError: {e.reason}"
    except Exception as e:  # noqa: BLE001 — surface anything as a soft failure
        return 0, {}, f"{type(e).__name__}: {e}"


def json_or_text(body: str) -> Any:
    try:
        return json.loads(body)
    except Exception:  # noqa: BLE001
        return body


def basic_auth(user: str, token: str) -> str:
    raw = f"{user}:{token}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")
