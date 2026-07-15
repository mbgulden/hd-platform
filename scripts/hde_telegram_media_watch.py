#!/usr/bin/env python3
"""Watch HDE Telegram media delivery for a live comparison canary.

This script does not send Telegram messages. A real tester still has to talk to
the bot. The watcher verifies the server side:
- router logs show Telegram document uploads succeeding
- Redis media queue has no pending jobs
- router metrics are healthy
- recent guest comparison artifacts exist

No tokens or credentials are printed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REDACT_TOKEN_RE = re.compile(r"\b[0-9]{6,}:[A-Za-z0-9_-]+\b")
DOC_RE = re.compile(r"sendDocument|send_document|document", re.I)
OK_RE = re.compile(r"\b(200|OK|ok=True|success)\b", re.I)
ERR_RE = re.compile(r"\b(traceback|exception|error|failed|timeout|file not found|no such file|401|403|429|500|502|503)\b", re.I)


def run(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def redact(text: str) -> str:
    return REDACT_TOKEN_RE.sub("[REDACTED_TOKEN]", text or "")


def router_logs(since: str) -> list[str]:
    rc, out, err = run(f"journalctl -u hde_router.service --since {sh_quote(since)} --no-pager", 45)
    if rc != 0:
        raise RuntimeError(f"journalctl failed: {redact(err or out)}")
    return [redact(line) for line in out.splitlines()]


def sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def router_metrics() -> dict[str, Any]:
    cmd = "PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts /home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_router_metrics.py --pretty"
    rc, out, err = run(cmd, 60)
    if rc != 0:
        raise RuntimeError(f"router metrics failed: {redact(err or out)}")
    return json.loads(out)


def recent_guest_artifacts(guest_id: int, minutes: int) -> dict[str, Any]:
    root = Path(f"/home/ubuntu/users/guest_{guest_id}")
    cutoff = time.time() - minutes * 60
    pdfs: list[str] = []
    manifests: list[str] = []
    events = 0
    for path in (root / "charts").glob("**/*") if (root / "charts").exists() else []:
        try:
            if path.is_file() and path.stat().st_mtime >= cutoff:
                if path.suffix.lower() == ".pdf":
                    pdfs.append(str(path))
                elif path.name == "coach_manifest.json":
                    manifests.append(str(path))
        except FileNotFoundError:
            pass
    events_path = root / "coach_view" / "events.jsonl"
    if events_path.exists():
        try:
            for line in events_path.read_text(errors="ignore").splitlines():
                if "chart_generated" in line:
                    events += 1
        except Exception:
            events = -1
    return {"recent_pdfs": sorted(pdfs), "recent_manifests": sorted(manifests), "chart_events_total": events}


def evaluate(args: argparse.Namespace) -> tuple[bool, dict[str, Any]]:
    logs = router_logs(args.since)
    doc_lines = [line for line in logs if DOC_RE.search(line)]
    ok_doc_lines = [line for line in doc_lines if OK_RE.search(line)]
    error_lines = [line for line in logs if ERR_RE.search(line) and not ("getUpdates" in line and "timeout" in line.lower())]
    metrics = router_metrics()
    queues = (metrics.get("redis") or {}).get("queues") or {}
    media_pending = int((queues.get("media") or {}).get("pending") or 0)
    chat_pending = int((queues.get("chat") or {}).get("pending") or 0)
    status_ok = metrics.get("status") == "ok"
    artifacts = recent_guest_artifacts(args.guest_id, args.artifact_minutes)

    passed = (
        len(ok_doc_lines) >= args.expect_documents
        and media_pending == 0
        and chat_pending == 0
        and status_ok
        and not error_lines
    )
    report = {
        "status": "pass" if passed else "waiting_or_fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "since": args.since,
        "expected_documents": args.expect_documents,
        "document_log_lines": len(doc_lines),
        "successful_document_log_lines": len(ok_doc_lines),
        "recent_successful_document_lines": ok_doc_lines[-args.show_lines :],
        "router_status": metrics.get("status"),
        "media_pending": media_pending,
        "chat_pending": chat_pending,
        "redis_enabled": (metrics.get("redis") or {}).get("enabled"),
        "guest_containers_healthy": ((metrics.get("docker") or {}).get("guest_containers_healthy")),
        "error_lines": error_lines[-args.show_lines :],
        "artifacts": artifacts,
    }
    return passed, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Watch HDE live Telegram media proof")
    parser.add_argument("--since", default="now", help="journalctl --since value; use a quoted timestamp or '10 minutes ago'")
    parser.add_argument("--expect-documents", type=int, default=2, help="required successful Telegram document uploads")
    parser.add_argument("--watch-seconds", type=int, default=0, help="poll until pass or timeout")
    parser.add_argument("--interval", type=int, default=10, help="poll interval in seconds")
    parser.add_argument("--guest-id", type=int, default=23)
    parser.add_argument("--artifact-minutes", type=int, default=30)
    parser.add_argument("--show-lines", type=int, default=8)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    if args.since == "now":
        args.since = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    deadline = time.time() + max(0, args.watch_seconds)
    last_report: dict[str, Any] = {}
    while True:
        try:
            passed, report = evaluate(args)
        except Exception as exc:  # noqa: BLE001
            passed = False
            report = {"status": "error", "error": redact(repr(exc)), "since": args.since}
        last_report = report
        if passed or args.watch_seconds <= 0 or time.time() >= deadline:
            print(json.dumps(last_report, indent=2 if args.pretty else None))
            return 0 if passed else 1
        time.sleep(max(1, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
