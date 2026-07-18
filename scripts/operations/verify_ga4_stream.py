#!/usr/bin/env python3
"""Verify the known Human Design Engine GA4 web stream evidence.

This script intentionally does not print secrets. It can verify public/live tag
installation and detect whether an OAuth bearer token is available for Google
Analytics Admin API proof. GA Admin API mutation/lookup requires OAuth; API keys
alone are expected to fail with UNAUTHENTICATED.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

MEASUREMENT_RE = re.compile(r"G-[A-Z0-9]{6,}")
DEFAULT_MEASUREMENT_ID = "G-Q6TPL08VM7"
DEFAULT_LIVE_URLS = [
    "https://humandesignengine.com/",
    "https://humandesignengine.com/landing-reports.html",
    "https://humandesignengine.com/buy-report.html",
    "https://humandesignengine.com/widget-demo.html",
    "https://humandesignengine.com/bodygraph.html",
]
EXCLUDED_PARTS = {
    ".git",
    "node_modules",
    "dist",
    ".astro",
    "__pycache__",
}
TEXT_SUFFIXES = {".html", ".astro", ".js", ".ts", ".md", ".json"}


def fetch(url: str, headers: dict[str, str] | None = None) -> tuple[int, str]:
    request = urllib.request.Request(url, headers=headers or {"User-Agent": "hde-ga4-verifier/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def scan_repo(repo: Path, measurement_id: str) -> dict[str, object]:
    files_with_measurement: list[str] = []
    all_measurements: set[str] = set()
    scanned = 0
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(repo)
        if any(part in EXCLUDED_PARTS for part in rel.parts):
            continue
        scanned += 1
        text = path.read_text(errors="ignore")
        ids = set(MEASUREMENT_RE.findall(text))
        all_measurements.update(ids)
        if measurement_id in text:
            files_with_measurement.append(str(rel))
    return {
        "scanned_text_files": scanned,
        "measurement_ids_seen": sorted(all_measurements),
        "files_with_expected_measurement": sorted(files_with_measurement),
        "expected_measurement_file_count": len(files_with_measurement),
    }


def verify_live(urls: list[str], measurement_id: str) -> dict[str, object]:
    results = []
    for url in urls:
        status, body = fetch(url)
        ids = sorted(set(MEASUREMENT_RE.findall(body)))
        results.append(
            {
                "url": url,
                "http_status": status,
                "measurement_ids": ids,
                "expected_measurement_present": measurement_id in ids,
                "gtag_loader_present": f"https://www.googletagmanager.com/gtag/js?id={measurement_id}" in body,
            }
        )
    status, body = fetch(f"https://www.googletagmanager.com/gtag/js?id={measurement_id}")
    return {
        "pages": results,
        "gtag_js": {"http_status": status, "bytes": len(body.encode("utf-8"))},
    }


def verify_admin_api() -> dict[str, object]:
    token = os.environ.get("GOOGLE_OAUTH_TOKEN", "")
    token_is_placeholder = token.startswith("__SET_IN_HOST_ENV_") or token in {"", "***"}
    if token_is_placeholder:
        # Prove the Admin API class needs OAuth rather than silently pretending we checked it.
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        url = "https://analyticsadmin.googleapis.com/v1beta/accountSummaries"
        if api_key and not api_key.startswith("__SET_IN_HOST_ENV_"):
            url += "?key=" + api_key
        status, body = fetch(url)
        try:
            parsed = json.loads(body)
            message = parsed.get("error", {}).get("message", body[:300])
            api_status = parsed.get("error", {}).get("status")
        except json.JSONDecodeError:
            message = body[:300]
            api_status = None
        return {
            "admin_api_verified": False,
            "reason": "GOOGLE_OAUTH_TOKEN missing or placeholder; Analytics Admin requires OAuth bearer credentials.",
            "unauthenticated_probe_http_status": status,
            "unauthenticated_probe_status": api_status,
            "unauthenticated_probe_message": message,
        }

    status, body = fetch(
        "https://analyticsadmin.googleapis.com/v1beta/accountSummaries",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "hde-ga4-verifier/1.0"},
    )
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = {"raw": body[:500]}
    return {"admin_api_verified": status == 200, "http_status": status, "response_keys": sorted(parsed.keys())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--measurement-id", default=DEFAULT_MEASUREMENT_ID)
    parser.add_argument("--live-url", action="append", dest="live_urls")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    live_urls = args.live_urls or DEFAULT_LIVE_URLS
    result = {
        "status": "warning" ,
        "domain": "humandesignengine.com",
        "expected_measurement_id": args.measurement_id,
        "repo": scan_repo(repo, args.measurement_id),
        "live": verify_live(live_urls, args.measurement_id),
        "analytics_admin_api": verify_admin_api(),
    }
    pages = result["live"]["pages"]
    if all(page["expected_measurement_present"] for page in pages) and result["analytics_admin_api"].get("admin_api_verified"):
        result["status"] = "pass"
    elif any(page["expected_measurement_present"] for page in pages):
        result["status"] = "partial"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in {"pass", "partial"} else 2


if __name__ == "__main__":
    sys.exit(main())
