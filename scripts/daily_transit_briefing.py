#!/usr/bin/env python3
"""
Daily Transit Briefing — GRO-99
================================
Computes today's transits, formats a Telegram-friendly briefing, and posts it.
Designed to run as a cron job at 6 AM Mountain time (13:00 UTC).

Usage:
    python3 daily_transit_briefing.py          # compute + print
    python3 daily_transit_briefing.py --send   # compute + send to Telegram

Environment:
    TELEGRAM_BOT_TOKEN   — from BotFather
    TELEGRAM_CHAT_ID     — target channel/chat
    ENGINE_PATH          — path to OpenHumanDesignMCP/src (default below)
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# ── Engine import ──────────────────────────────────────────────────────
ENGINE_PATH = os.environ.get(
    "ENGINE_PATH",
    "/home/ubuntu/work/OpenHumanDesignMCP/hd-mcp-server/src"
)
sys.path.insert(0, ENGINE_PATH)

from ephemeris_engine import init_ephemeris
from transit_engine import calculate_transit_positions
from cosmic_calculator import GATE_NAMES

init_ephemeris()

# ── Telegram ────────────────────────────────────────────────────────────
def send_telegram(message: str) -> bool:
    """Send a message to Telegram. Returns True if successful."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    if not bot_token or not chat_id:
        print("[warn] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set — skipping send")
        return False
    
    import urllib.request
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    body = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
        return result.get("ok", False)
    except Exception as e:
        print(f"[error] Telegram send failed: {e}")
        return False


# ── Transit computation ─────────────────────────────────────────────────
def compute_daily_transits():
    """Calculate today's transit positions and return a dict."""
    positions = calculate_transit_positions()
    
    # Build a human-readable summary
    transit_gates = []
    planet_icons = {
        "Sun": "☀️", "Moon": "🌙", "Mercury": "☿", "Venus": "♀",
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
        "Uranus": "♅", "Neptune": "♆", "Pluto": "♇",
        "North Node": "☊", "South Node": "☋",
    }
    
    for planet, data in sorted(positions.items()):
        gate = data.get("gate", "?")
        gate_name = GATE_NAMES.get(gate, f"Gate {gate}")
        retro = " ℞" if data.get("retrograde") else ""
        icon = planet_icons.get(planet, "•")
        transit_gates.append({
            "planet": planet,
            "icon": icon,
            "gate": gate,
            "name": gate_name,
            "retrograde": data.get("retrograde", False),
        })
    
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "transits": transit_gates,
    }


# ── Formatting ──────────────────────────────────────────────────────────
def format_briefing(data: dict) -> str:
    """Format transit data as a Telegram-friendly HTML message."""
    date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
    
    lines = [
        f"🌌 <b>Daily Transit Briefing</b>",
        f"📅 {date_str}",
        "",
        "<b>Today's Gates:</b>",
        ""
    ]
    
    for t in data["transits"]:
        retro = " <i>(retrograde)</i>" if t["retrograde"] else ""
        lines.append(f"{t['icon']} <b>{t['planet']}</b> — Gate {t['gate']}: {t['name']}{retro}")
    
    # Group by unique gates
    unique_gates = sorted(set(t["gate"] for t in data["transits"]), key=int)
    
    lines.append("")
    lines.append(f"<b>Active Gates Today:</b> {', '.join(str(g) for g in unique_gates)}")
    lines.append("")
    lines.append("<i>Get your full transit report → humandesignengine.com/reports</i>")
    
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Daily Transit Briefing")
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()
    
    data = compute_daily_transits()
    
    if args.json:
        print(json.dumps(data, indent=2))
        return
    
    message = format_briefing(data)
    print(message)
    
    if args.send:
        ok = send_telegram(message)
        print(f"\n[{'✓' if ok else '✗'}] Telegram {'sent' if ok else 'failed'}")
    else:
        print("\n[info] Use --send to post to Telegram (needs TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)")


if __name__ == "__main__":
    main()
