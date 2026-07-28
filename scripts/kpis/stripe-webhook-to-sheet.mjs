#!/usr/bin/env python3
"""
scripts/kpis/stripe-webhook-to-sheet.mjs (Python version)

Run by the existing api/routes/stripe_webhook.py handler on `checkout.session.completed`
and `customer.subscription.deleted` events. Appends a row to Google Sheets ("Raw" tab).

This script is intentionally lightweight: it calls the Sheets API via service-account JSON
read from HDE_GOOGLE_SERVICE_ACCOUNT_JSON.
"""

import json
import os
import sys
import time
from pathlib import Path

# Optional dependency: gspread (preferred). If unavailable, fall back to raw API call.
try:
    import gspread  # type: ignore
    from google.oauth2.service_account import Credentials  # type: ignore
except ImportError:  # pragma: no cover
    gspread = None
    Credentials = None


def append_raw_event(event: dict) -> None:
    sheet_id = os.environ.get("HDE_KPI_SHEET_ID")
    if not sheet_id:
        Path("/tmp/hde-kpi-sheet-raw.log").open("a").write(json.dumps(event) + "\n")
        print("[kpi] no HDE_KPI_SHEET_ID; logged to /tmp/hde-kpi-sheet-raw.log")
        return
    key_file = os.environ.get("HDE_GOOGLE_SERVICE_ACCOUNT_JSON")
    if not key_file or not Path(key_file).exists():
        print("[kpi] no service-account JSON; skipping")
        return

    if gspread is not None:
        creds = Credentials.from_service_account_file(
            key_file, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sheet_id)
        try:
            ws = sh.worksheet("Raw")
        except gspread.WorksheetNotFound:
            ws = sh.add_worksheet("Raw", rows=1000, cols=10)
            ws.append_row([
                "stripe_event_id", "event_type", "created_iso", "amount_usd",
                "customer_email", "metadata_funnel", "metadata_product", "status",
            ])
        obj = event.get("data", {}).get("object", {})
        ws.append_row([
            event.get("id", ""),
            event.get("type", ""),
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(event.get("created", 0))),
            (obj.get("amount_total", 0) or 0) / 100,
            obj.get("customer_details", {}).get("email") or obj.get("customer_email", ""),
            (obj.get("metadata") or {}).get("funnel", ""),
            (obj.get("metadata") or {}).get("product", ""),
            obj.get("payment_status", obj.get("status", "")),
        ])
    else:
        # Very small raw fallback if gspread isn't installed.
        Path("/tmp/hde-kpi-sheet-raw.log").open("a").write(json.dumps(event) + "\n")
        print("[kpi] gspread not installed; logged to /tmp/hde-kpi-sheet-raw.log")


def main():
    raw = sys.stdin.read()
    if not raw:
        print("[kpi] no event on stdin", file=sys.stderr)
        sys.exit(2)
    event = json.loads(raw)
    append_raw_event(event)


if __name__ == "__main__":
    main()
