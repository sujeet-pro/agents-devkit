#!/usr/bin/env python3
"""triage.py — accept / reject / edit findings before posting.

The parent agent drives the interactive UX. This script owns the state file
and the finalize logic. It never speaks to the user directly; the harness's
parent agent does (via AskUserQuestion in Claude Code; equivalent in other
harnesses).

Lifecycle
---------
  1. After findings.json is written, the orchestrator (or parent agent) runs:
       triage.py --init --default-state {pending|accept}
     pending = interactive (user triages every finding)
     accept  = auto (post everything)

  2. In interactive mode, the parent agent walks the pending list, asking the
     user accept / reject / edit for each. For 'edit', the parent agent runs
     an iterative loop (show current body → ask for prompt → rewrite via its
     own LLM → show new → confirm/iterate → accept or reject). After each
     rewrite, the parent agent calls:
       triage.py --rewrite f-NNN --fields-json '{"body":"…","suggestion":"…"}'
     The rewrite stays in 'edit' state until the user confirms with --mark accept.

  3. When every finding is accept or reject, the orchestrator runs:
       triage.py --finalize
     which emits findings-final.json (only accepted findings, with edits
     applied). post_comments.py reads this file when it exists.

State file: <task-dir>/triage-state.json
  {
    "mode": "auto" | "interactive",
    "findings": {"f-001": {"state": "...", "edits": N}, ...},
    "edited":   {"f-001": {"title":"…", "body":"…", …}, ...}
  }
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import die, get_logger, read_json, write_json, pr_review_file  # noqa: E402


VALID_STATES = ("accept", "reject", "edit", "pending")
EDITABLE_FIELDS = ("title", "body", "suggestion", "impact_if_unfixed")


def _state_path(task_dir: Path) -> Path:
    return pr_review_file(task_dir, "triage-state.json")


def _findings_path(task_dir: Path) -> Path:
    """Path to the post-validation finding set (Phase 3 output)."""
    return pr_review_file(task_dir, "initial-findings.json")


def _final_path(task_dir: Path) -> Path:
    return pr_review_file(task_dir, "findings-final.json")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_init(task_dir: Path, default_state: str, log) -> dict:
    if default_state not in ("accept", "pending"):
        die("--default-state must be 'accept' (auto) or 'pending' (interactive)")
    findings_blob = read_json(_findings_path(task_dir))
    findings = findings_blob.get("findings", [])
    mode = "auto" if default_state == "accept" else "interactive"
    # Appreciations always start in `accept` — they never enter the
    # interactive walk. They post as PR-level general comments later, with
    # no resolve state to manage. The user wants ALL appreciations to land.
    n_auto_appreciations = 0
    findings_state: dict[str, dict] = {}
    for f in findings:
        sev = f.get("severity")
        if sev == "appreciation":
            findings_state[f["id"]] = {"state": "accept", "edits": 0,
                                        "auto_accepted": True, "kind": "appreciation"}
            n_auto_appreciations += 1
        else:
            findings_state[f["id"]] = {"state": default_state, "edits": 0}
    state = {
        "task_dir": str(task_dir),
        "mode": mode,
        "ts": _now(),
        "findings": findings_state,
        "edited": {},
    }
    write_json(_state_path(task_dir), state)
    log.info("init: mode=%s findings=%d default=%s (auto-accepted %d appreciation(s))",
             mode, len(findings), default_state, n_auto_appreciations)
    return {
        "mode": mode,
        "n_findings": len(findings),
        "n_auto_accepted_appreciations": n_auto_appreciations,
        "default_state": default_state,
        "state_path": str(_state_path(task_dir)),
    }


def cmd_mark(task_dir: Path, finding_id: str, new_state: str, log) -> dict:
    if new_state not in VALID_STATES:
        die(f"--state must be one of {VALID_STATES}")
    state = read_json(_state_path(task_dir))
    if finding_id not in state["findings"]:
        die(f"unknown finding_id: {finding_id}")
    prev = state["findings"][finding_id]["state"]
    state["findings"][finding_id]["state"] = new_state
    write_json(_state_path(task_dir), state)
    log.info("mark %s: %s → %s", finding_id, prev, new_state)
    return {"finding_id": finding_id, "previous_state": prev, "new_state": new_state}


def cmd_rewrite(task_dir: Path, finding_id: str, fields: dict, log) -> dict:
    state = read_json(_state_path(task_dir))
    if finding_id not in state["findings"]:
        die(f"unknown finding_id: {finding_id}")
    # Validate fields
    unknown = [k for k in fields if k not in EDITABLE_FIELDS]
    if unknown:
        die(f"only these fields may be rewritten: {EDITABLE_FIELDS}; got {unknown}")
    cur = state["edited"].get(finding_id, {})
    cur.update(fields)
    state["edited"][finding_id] = cur
    state["findings"][finding_id]["edits"] += 1
    # Stay in 'edit' state until --mark accept lands.
    state["findings"][finding_id]["state"] = "edit"
    write_json(_state_path(task_dir), state)
    log.info("rewrite %s: fields=%s (edit #%d)", finding_id, list(fields.keys()),
             state["findings"][finding_id]["edits"])
    return {
        "finding_id": finding_id,
        "edits": state["findings"][finding_id]["edits"],
        "state": "edit",
        "fields_updated": list(fields.keys()),
    }


def _merge_finding(f: dict, edited: dict) -> dict:
    out = dict(f)
    for k, v in edited.items():
        out[k] = v
    return out


def cmd_list(task_dir: Path, filter_state: str | None, include_content: bool, log) -> dict:
    state = read_json(_state_path(task_dir))
    findings_blob = read_json(_findings_path(task_dir))
    findings_by_id = {f["id"]: f for f in findings_blob.get("findings", [])}
    out = []
    for fid, st in state["findings"].items():
        if filter_state and st["state"] != filter_state:
            continue
        f = findings_by_id.get(fid)
        if not f:
            continue
        edited = state.get("edited", {}).get(fid, {})
        merged = _merge_finding(f, edited)
        row = {
            "id": fid,
            "state": st["state"],
            "edits": st.get("edits", 0),
            "severity": merged.get("severity"),
            "title": merged.get("title"),
            "file": merged.get("file"),
            "line_start": merged.get("line_start"),
        }
        if include_content:
            row["body"] = merged.get("body")
            row["suggestion"] = merged.get("suggestion")
            row["impact_if_unfixed"] = merged.get("impact_if_unfixed")
        out.append(row)
    return {"mode": state.get("mode"), "filter": filter_state, "findings": out}


def cmd_show(task_dir: Path, finding_id: str, log) -> dict:
    state = read_json(_state_path(task_dir))
    findings_blob = read_json(_findings_path(task_dir))
    findings_by_id = {f["id"]: f for f in findings_blob.get("findings", [])}
    if finding_id not in findings_by_id:
        die(f"unknown finding_id: {finding_id}")
    f = findings_by_id[finding_id]
    edited = state.get("edited", {}).get(finding_id, {})
    merged = _merge_finding(f, edited)
    return {
        "id": finding_id,
        "state": state["findings"][finding_id]["state"],
        "edits": state["findings"][finding_id].get("edits", 0),
        "has_edits": bool(edited),
        "current": {k: merged.get(k) for k in (
            "severity", "dimension", "confidence", "file", "line_start", "line_end",
            "title", "body", "suggestion", "impact_if_unfixed",
        )},
        "original": {k: f.get(k) for k in EDITABLE_FIELDS} if edited else None,
    }


def cmd_render(task_dir: Path, finding_id: str, log) -> dict:
    """Return a rich markdown rendering of one finding — what the agent
    shows the user during the interactive triage walk.

    Includes:
      - the location + severity + dimension header
      - the code snippet with context lines around the anchored range
      - "What's happening" / "Why this matters" / "Suggested fix"
      - a preview of EXACTLY what would post to the PR
      - the current triage state (so the agent can offer the right options)
    """
    state = read_json(_state_path(task_dir))
    findings_blob = read_json(_findings_path(task_dir))
    findings_by_id = {f["id"]: f for f in findings_blob.get("findings", [])}
    if finding_id not in findings_by_id:
        die(f"unknown finding_id: {finding_id}")
    f = findings_by_id[finding_id]
    edited = state.get("edited", {}).get(finding_id, {})
    merged = _merge_finding(f, edited)

    # Lazy imports — report.render_finding_block + post_comments.format_comment_body.
    # We use report's rich block but switch the "preview" to the post template.
    try:
        from report import render_finding_block  # noqa: WPS433
        from post_comments import format_comment_body  # noqa: WPS433
    except Exception as e:
        die(f"could not import rendering helpers: {e}")

    rendered = render_finding_block(
        merged, task_dir=task_dir, format_comment_body=format_comment_body,
    )
    return {
        "id": finding_id,
        "state": state["findings"][finding_id]["state"],
        "edits": state["findings"][finding_id].get("edits", 0),
        "rendered_md": rendered,
        "post_preview": format_comment_body(merged),
    }


def cmd_finalize(task_dir: Path, log) -> dict:
    state = read_json(_state_path(task_dir))
    findings_blob = read_json(_findings_path(task_dir))
    pending = [fid for fid, st in state["findings"].items()
               if st["state"] in ("pending", "edit")]
    if pending:
        die("cannot finalize — {} finding(s) still {} state: {}".format(
            len(pending),
            "pending/edit",
            ", ".join(pending),
        ))
    accepted = [f for f in findings_blob.get("findings", [])
                if state["findings"].get(f["id"], {}).get("state") == "accept"]
    edited_lookup = state.get("edited", {})
    finalized = [_merge_finding(f, edited_lookup.get(f["id"], {})) for f in accepted]
    out = {
        "findings": finalized,
        "existing_comment_actions": findings_blob.get("existing_comment_actions", []),
        "recommendation": findings_blob.get("recommendation"),
        "summary": findings_blob.get("summary"),
        "finding_set_hash": findings_blob.get("finding_set_hash"),
        "triage": {
            "mode": state.get("mode"),
            "accepted": len(finalized),
            "rejected": sum(1 for st in state["findings"].values() if st["state"] == "reject"),
            "edited": sum(1 for fid in edited_lookup if state["findings"].get(fid, {}).get("state") == "accept"),
        },
    }
    write_json(_final_path(task_dir), out)
    log.info("finalize: accepted=%d rejected=%d edited=%d",
             out["triage"]["accepted"], out["triage"]["rejected"], out["triage"]["edited"])
    return {"final_path": str(_final_path(task_dir)), **out["triage"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    sub = ap.add_mutually_exclusive_group(required=True)
    sub.add_argument("--init", action="store_true")
    sub.add_argument("--mark", help="finding_id to mark")
    sub.add_argument("--rewrite", help="finding_id to rewrite")
    sub.add_argument("--list", action="store_true")
    sub.add_argument("--show", help="finding_id to inspect")
    sub.add_argument("--render", help="finding_id to render as rich markdown (code snippet + what/why/impact + post preview) for the interactive walk")
    sub.add_argument("--finalize", action="store_true")

    ap.add_argument("--default-state", choices=("accept", "pending"), default="pending",
                    help="for --init")
    ap.add_argument("--state", choices=VALID_STATES, help="for --mark")
    ap.add_argument("--fields-json", help="for --rewrite, JSON object of editable fields")
    ap.add_argument("--filter-state", choices=VALID_STATES, help="for --list")
    ap.add_argument("--include-content", action="store_true", help="for --list")
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    log = get_logger("triage", task_dir if task_dir.exists() else None)

    if args.init:
        result = cmd_init(task_dir, args.default_state, log)
    elif args.mark:
        if not args.state:
            die("--mark requires --state")
        result = cmd_mark(task_dir, args.mark, args.state, log)
    elif args.rewrite:
        if not args.fields_json:
            die("--rewrite requires --fields-json '{\"body\": \"...\"}'")
        try:
            fields = json.loads(args.fields_json)
        except json.JSONDecodeError as e:
            die(f"invalid --fields-json: {e}")
        if not isinstance(fields, dict):
            die("--fields-json must be a JSON object")
        result = cmd_rewrite(task_dir, args.rewrite, fields, log)
    elif args.list:
        result = cmd_list(task_dir, args.filter_state, args.include_content, log)
    elif args.show:
        result = cmd_show(task_dir, args.show, log)
    elif args.render:
        result = cmd_render(task_dir, args.render, log)
    elif args.finalize:
        result = cmd_finalize(task_dir, log)
    else:
        die("no sub-command")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
