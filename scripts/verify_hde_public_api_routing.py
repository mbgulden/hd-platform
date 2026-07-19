#!/usr/bin/env python3
"""Verify HD Engine public/protected API routing decisions.

This intentionally uses static source assertions so it can run in the Hermes VM
without live Stripe, SQLAlchemy, Redis, or engine credentials. It guards the edge
contract: revenue checkout/report delivery remains public, diagnostic inventory is
protected, and health has a public uptime-safe endpoint.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def require(needle: str, haystack: str, label: str) -> None:
    if needle not in haystack:
        raise AssertionError(f"missing {label}: {needle}")


def main() -> int:
    policy = read("api/routes/access_policy.py")
    api_main = read("api/main.py")
    payment = read("payment/server.py")
    reports = read("reports/server.py")

    for route in (
        '"GET /api/health"',
        '"POST /api/checkout/create-session"',
        '"GET /api/checkout/session"',
        '"POST /api/public/compute-chart"',
        '"GET /api/reports/download/{filename}"',
    ):
        require(route, policy, "public route policy")

    for marker in (
        '"GET /api/diagnostics/routes"',
        '"GET /api/reports"',
        "HTTP_503_SERVICE_UNAVAILABLE",
        "HTTP_403_FORBIDDEN",
        "CF-Access-Client-Id",
        "CF-Access-Client-Secret",
        "HDE_DIAGNOSTIC_TOKEN",
    ):
        require(marker, policy, "protected diagnostic policy")

    require("app.include_router(access_policy_router)", api_main, "FastAPI policy router mount")
    require("'/api/checkout/create-session'", payment, "payment checkout alias")
    require("'/api/checkout/session'", payment, "payment session alias")
    require("elif path.startswith('/api/reports/download/'):", reports, "public report download route")
    require("elif path == '/api/public/compute-chart':", reports, "public chart route")
    require("elif path == '/api/public/capture-lead':", reports, "public lead route")

    print("OK: HD Engine public checkout/report routes remain open; diagnostics are protected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
