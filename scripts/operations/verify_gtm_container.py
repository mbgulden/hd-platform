#!/usr/bin/env python3
"""Verify Human Design Engine GTM/GA4 coverage without exposing secrets.

This verifier is deliberately read-only. It scans committed repository files for
GTM container IDs and the known GA4 measurement ID, samples live production pages,
and probes the public Google endpoints. Admin/container creation still requires a
Google OAuth bearer token with Tag Manager scopes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable

GTM_RE = re.compile(r"GTM-[A-Z0-9]+")
GA4_RE = re.compile(r"G-[A-Z0-9]+")
DEFAULT_GA4_ID = "G-Q6TPL08VM7"
DEFAULT_DOMAIN = "https://humandesignengine.com"
TEXT_SUFFIXES = {".astro", ".html", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".md"}
SKIP_PARTS = {".git", "node_modules", "dist", ".venv", "__pycache__"}
LIVE_PATHS = ["/", "/buy-report/", "/free-human-design-reading-generator/", "/deconditioning/", "/landing-reports.html", "/upsell.html"]


def iter_text_files(repo: Path) -> Iterable[Path]:
    for path in repo.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(errors="ignore")


def http_get(url: str, headers: dict[str, str] | None = None) -> tuple[int | None, str]:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "ned-gtm-verifier/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read(500_000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(50_000).decode("utf-8", "ignore")
    except Exception as exc:  # pragma: no cover - surfaced in JSON output
        return None, f"ERROR: {type(exc).__name__}: {exc}"


def scan_repo(repo: Path, ga4_id: str) -> dict:
    gtm_hits: dict[str, list[str]] = {}
    ga4_hits: dict[str, list[str]] = {}
    for path in iter_text_files(repo):
        text = read_text(path)
        gtms = sorted(set(GTM_RE.findall(text)))
        ga4s = sorted(set(GA4_RE.findall(text)))
        rel = str(path.relative_to(repo))
        if gtms:
            gtm_hits[rel] = gtms
        if ga4_id in ga4s:
            ga4_hits[rel] = [ga4_id]
    return {
        "gtm_file_count": len(gtm_hits),
        "gtm_ids": sorted({gtm for values in gtm_hits.values() for gtm in values}),
        "gtm_hits": gtm_hits,
        "ga4_id": ga4_id,
        "ga4_file_count": len(ga4_hits),
        "ga4_sample_files": sorted(ga4_hits)[:25],
    }


def scan_live(domain: str, ga4_id: str) -> list[dict]:
    rows = []
    for path in LIVE_PATHS:
        url = domain.rstrip("/") + path
        status, body = http_get(url)
        rows.append({
            "url": url,
            "http_status": status,
            "gtm_ids": sorted(set(GTM_RE.findall(body))),
            "ga4_present": ga4_id in body,
        })
    return rows


def probe_google_endpoints(ga4_id: str, oauth_token: str | None = None) -> dict:
    gtag_status, _ = http_get(f"https://www.googletagmanager.com/gtag/js?id={ga4_id}")
    headers = {"User-Agent": "ned-gtm-verifier/1.0"}
    auth_mode = "none"
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
        auth_mode = "oauth_bearer_redacted"
    status, body = http_get("https://tagmanager.googleapis.com/tagmanager/v2/accounts", headers=headers)
    return {
        "public_gtag_js_status": gtag_status,
        "tagmanager_accounts_status": status,
        "tagmanager_auth_mode": auth_mode,
        "tagmanager_response_excerpt": body[:300].replace(oauth_token or "", "[REDACTED]") if body else "",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--ga4-id", default=DEFAULT_GA4_ID)
    parser.add_argument("--oauth-token-env", default="GOOGLE_OAUTH_TOKEN")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    import os
    token = os.environ.get(args.oauth_token_env) or None
    report = {
        "status": "partial",
        "domain": args.domain,
        "repo": str(repo),
        "repo_scan": scan_repo(repo, args.ga4_id),
        "live_sample": scan_live(args.domain, args.ga4_id),
        "google_endpoint_probe": probe_google_endpoints(args.ga4_id, token),
        "green_requirements": [
            "Tag Manager API returns account/container details with OAuth bearer auth",
            "GTM-... container ID is recorded",
            "container contains GA4 config for G-Q6TPL08VM7 and conversion events",
            "published container is live on production pages or intentionally deferred",
        ],
    }
    if report["repo_scan"]["gtm_file_count"] > 0 and report["google_endpoint_probe"]["tagmanager_accounts_status"] == 200:
        report["status"] = "candidate_green_requires_manual_review"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main())
