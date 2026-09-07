#!/usr/bin/env python3
"""Family-test monitor for HDE staging.

Produces a privacy-aware health + stuck-state dashboard for family/beta testing.
Default mode inspects infrastructure, checkout/onboarding state, container health,
and consent readiness. It does not dump transcript contents. With --include-consented-transcript-summary
it only reports counts/paths for users with active coach/test review consent.
"""
from __future__ import annotations

import argparse
import asyncio
import html
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


load_env(ROOT / ".env")

from shared.database import BotInstance, Invitation, User, async_session_factory  # noqa: E402
from scripts.hde_router_metrics import collect_metrics  # noqa: E402

OUTPUT_JSON = ROOT / "docs" / "hde-family-test-monitor.json"
OUTPUT_HTML = ROOT / "docs" / "hde-family-test-monitor.html"
STUCK_STATUSES = {"error", "provisioning", "waking", "stopped", "suspended"}


@dataclass
class TesterRow:
    user_id: int
    email_label: str
    subscription_status: str
    premium: bool
    coach_review_consent: bool
    consent_active: bool
    latest_invitation_used: bool | None
    latest_invitation_age_hours: float | None
    linked_to_telegram: bool
    guide_name: str | None
    bot_status: str
    container_name: str | None
    container_state: str
    workspace_exists: bool
    waiting_reasons: list[str]
    stuck_reasons: list[str]
    consented_artifacts: dict[str, Any]


def redact_email(email: str | None) -> str:
    if not email:
        return "unknown"
    local, _, domain = email.partition("@")
    if not domain:
        return "[email]"
    shown = local[:2] + "…" if len(local) > 2 else local[:1] + "…"
    return f"{shown}@{domain}"


def run(command: list[str], timeout: int = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)


def docker_statuses() -> dict[str, str]:
    commands = [
        ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"],
        ["sudo", "-n", "docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}"],
    ]
    for command in commands:
        try:
            proc = run(command)
        except Exception:
            continue
        if proc.returncode == 0:
            statuses: dict[str, str] = {}
            for line in proc.stdout.splitlines():
                if "\t" in line:
                    name, status = line.split("\t", 1)
                    statuses[name] = status
            return statuses
    return {}


def consent_is_active(user: User) -> bool:
    if not bool(getattr(user, "coach_review_consent", False)):
        return False
    if getattr(user, "coach_review_consent_revoked_at", None) is not None:
        return False
    if getattr(user, "subscription_status", None) != "active":
        return False
    end = getattr(user, "coaching_container_end", None)
    if end is None:
        return bool(getattr(user, "is_premium", False))
    if getattr(end, "tzinfo", None) is None:
        end = end.replace(tzinfo=timezone.utc)
    return end >= datetime.now(timezone.utc)


def workspace_artifact_summary(path: str | None, include_summary: bool) -> dict[str, Any]:
    if not path:
        return {"enabled": include_summary, "workspace_exists": False}
    root = Path(path)
    payload: dict[str, Any] = {"enabled": include_summary, "workspace_exists": root.exists()}
    if not include_summary or not root.exists():
        return payload
    chart_paths = list((root / "charts").glob("**/chart_data.json")) if (root / "charts").exists() else []
    journal_db = root / "guest_journal.db"
    events = root / "coach_view" / "events.jsonl"
    payload.update(
        {
            "chart_data_files": len(chart_paths),
            "journal_db_present": journal_db.exists(),
            "coach_events_present": events.exists(),
            "latest_chart_paths": [str(p.relative_to(root)) for p in chart_paths[-3:]],
        }
    )
    if events.exists():
        try:
            payload["coach_events_lines"] = sum(1 for _ in events.open("r", encoding="utf-8", errors="ignore"))
        except Exception as exc:
            payload["coach_events_error"] = str(exc)[:120]
    return payload


async def tester_rows(include_consented_transcript_summary: bool) -> list[TesterRow]:
    containers = docker_statuses()
    async with async_session_factory() as session:
        result = await session.execute(select(User).options(selectinload(User.invitations), selectinload(User.bot_instance)).order_by(User.id.desc()))
        users = list(result.scalars().unique().all())

    rows: list[TesterRow] = []
    for user in users:
        invitations = sorted(user.invitations or [], key=lambda inv: inv.id or 0, reverse=True)
        latest_invite = invitations[0] if invitations else None
        bot = user.bot_instance
        if not latest_invite and not bot and getattr(user, "subscription_status", None) != "active":
            continue

        bot_status = getattr(bot, "status", None) or "not_onboarded"
        container_name = getattr(bot, "container_name", None)
        workspace_path = getattr(bot, "workspace_path", None)
        container_state = containers.get(container_name or "", "missing" if container_name else "none")
        workspace_exists = bool(workspace_path and Path(workspace_path).exists())
        reasons: list[str] = []
        waiting: list[str] = []
        invite_age_hours: float | None = None
        if latest_invite and getattr(latest_invite, "created_at", None):
            created = latest_invite.created_at
            if getattr(created, "tzinfo", None) is None:
                created = created.replace(tzinfo=timezone.utc)
            invite_age_hours = round((datetime.now(timezone.utc) - created).total_seconds() / 3600, 1)
        if latest_invite and not latest_invite.is_used and getattr(user, "subscription_status", None) == "active":
            waiting.append("paid/active; tester has not opened onboarding link yet")
        if latest_invite and latest_invite.is_used and not bot:
            reasons.append("invite used but no bot instance")
        if bot and not getattr(bot, "telegram_user_id", None):
            reasons.append("bot instance not linked to Telegram")
        if bot_status in STUCK_STATUSES:
            reasons.append(f"bot status is {bot_status}")
        if bot and container_state == "missing" and bot_status == "active":
            reasons.append("active in DB but container missing")
        if bot and container_state != "none" and "unhealthy" in container_state.lower():
            reasons.append("container unhealthy")
        if bot and not workspace_exists:
            reasons.append("workspace missing")
        if bot and not getattr(user, "guide_name", None) and bot_status not in {"not_onboarded"}:
            reasons.append("guide name missing")

        active_consent = consent_is_active(user)
        rows.append(
            TesterRow(
                user_id=int(user.id),
                email_label=redact_email(getattr(user, "email", None)),
                subscription_status=getattr(user, "subscription_status", None) or "inactive",
                premium=bool(getattr(user, "is_premium", False)),
                coach_review_consent=bool(getattr(user, "coach_review_consent", False)),
                consent_active=active_consent,
                latest_invitation_used=None if latest_invite is None else bool(latest_invite.is_used),
                latest_invitation_age_hours=invite_age_hours,
                linked_to_telegram=bool(bot and getattr(bot, "telegram_user_id", None)),
                guide_name=getattr(user, "guide_name", None),
                bot_status=bot_status,
                container_name=container_name,
                container_state=container_state,
                workspace_exists=workspace_exists,
                waiting_reasons=waiting,
                stuck_reasons=reasons,
                consented_artifacts=workspace_artifact_summary(workspace_path, include_consented_transcript_summary and active_consent),
            )
        )
    return rows


def render_html(payload: dict[str, Any]) -> str:
    metrics = payload.get("metrics", {})
    rows = payload.get("testers", [])
    stuck = [r for r in rows if r.get("stuck_reasons")]
    ok_count = len(rows) - len(stuck)

    def pill(status: str) -> str:
        cls = "ok" if status in {"ok", "active", "healthy"} else "warn"
        if status in {"error", "missing", "unhealthy", "warn"}:
            cls = "bad"
        return f'<span class="pill {cls}">{html.escape(str(status))}</span>'

    row_html = []
    for r in rows:
        reasons = r.get("stuck_reasons") or []
        waiting = r.get("waiting_reasons") or []
        status_text = '<br>'.join(html.escape(x) for x in reasons) if reasons else '<span class="muted">clear</span>'
        if waiting:
            status_text += '<br><small>waiting: ' + '<br>'.join(html.escape(x) for x in waiting) + '</small>'
        row_html.append(
            "<tr>"
            f"<td>#{r['user_id']}<br><small>{html.escape(r['email_label'])}</small></td>"
            f"<td>{pill(r['subscription_status'])}<br><small>premium: {r['premium']}</small></td>"
            f"<td>{'yes' if r['latest_invitation_used'] else 'no' if r['latest_invitation_used'] is False else 'none'} / {'yes' if r['linked_to_telegram'] else 'no'}<br><small>invite age: {html.escape(str(r.get('latest_invitation_age_hours') or '—'))}h</small></td>"
            f"<td>{html.escape(str(r.get('guide_name') or '—'))}</td>"
            f"<td>{pill(r['bot_status'])}<br><small>{html.escape(str(r.get('container_state') or ''))}</small></td>"
            f"<td>{'yes' if r['consent_active'] else 'no'}<br><small>raw: {r['coach_review_consent']}</small></td>"
            f"<td>{status_text}</td>"
            "</tr>"
        )
    queue_bits = []
    for lane, q in ((metrics.get("redis") or {}).get("queues") or {}).items():
        queue_bits.append(f"{html.escape(lane)} pending {q.get('pending', 0)} / len {q.get('length', 0)}")
    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>HDE Family Test Monitor</title>
<style>
:root {{ --sage:#2f3a33; --moss:#63745f; --cream:#faf7f0; --paper:#fffdf8; --line:#ddd4c5; --bad:#9d2f2f; --warn:#8a6d2e; --ok:#2f6b45; }}
body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; background:var(--cream); color:var(--sage); }}
.wrap {{ max-width:1180px; margin:0 auto; padding:36px 24px 60px; }}
h1 {{ font-family: Georgia, serif; font-size:38px; margin:0 0 8px; }}
.card {{ background:var(--paper); border:1px solid var(--line); border-radius:24px; padding:22px; box-shadow:0 10px 30px rgba(47,58,51,.08); margin:18px 0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; }}
.metric {{ border:1px solid var(--line); border-radius:18px; padding:16px; background:#fff; }}
.metric b {{ display:block; font-size:28px; }}
.pill {{ display:inline-block; border-radius:999px; padding:4px 10px; font-weight:700; font-size:12px; background:#eee; }}
.pill.ok {{ color:var(--ok); background:#e6f2ea; }} .pill.warn {{ color:var(--warn); background:#fbf2d4; }} .pill.bad {{ color:var(--bad); background:#f7dddd; }}
table {{ width:100%; border-collapse:collapse; background:#fff; border-radius:18px; overflow:hidden; }}
th,td {{ border-bottom:1px solid var(--line); padding:12px; text-align:left; vertical-align:top; }} th {{ background:#f3eee5; font-size:12px; text-transform:uppercase; letter-spacing:.06em; }}
small,.muted {{ color:#7b766e; }} .note {{ line-height:1.6; }}
</style></head><body><main class='wrap'>
<p class='pill ok'>Human Design Engine · family test monitor</p>
<h1>Health + stuck-state dashboard</h1>
<p class='muted'>Generated {html.escape(payload['generated_at'])}. Transcript contents are not shown; consented transcript mode reports only artifact presence/counts.</p>
<section class='grid'>
<div class='metric'><span>Overall</span><b>{html.escape(payload['status'])}</b></div>
<div class='metric'><span>Testers</span><b>{len(rows)}</b><small>{ok_count} clear / {len(stuck)} stuck</small></div>
<div class='metric'><span>DB</span><b>{html.escape((metrics.get('database') or {}).get('backend','?'))}</b><small>{(metrics.get('database') or {}).get('users',0)} users</small></div>
<div class='metric'><span>Queues</span><b>{'ok' if not any((q.get('pending',0) or 0)>0 for q in ((metrics.get('redis') or {}).get('queues') or {}).values()) else 'pending'}</b><small>{html.escape(' · '.join(queue_bits) or 'no redis data')}</small></div>
<div class='metric'><span>Docker</span><b>{html.escape(str((metrics.get('docker') or {}).get('guest_containers_healthy','?')))}</b><small>healthy guests</small></div>
</section>
<section class='card note'><h2>Privacy posture</h2><p>This dashboard is safe for operations: it shows status, stuck reasons, and consent flags. Conversation/transcript contents are a separate second step and should only be reviewed for testers who explicitly consent.</p></section>
<section class='card'><h2>Tester stuck-state table</h2><table><thead><tr><th>User</th><th>Subscription</th><th>Invite / Telegram</th><th>Guide</th><th>Bot / container</th><th>Consent</th><th>Stuck reasons</th></tr></thead><tbody>{''.join(row_html)}</tbody></table></section>
</main></body></html>"""


async def build_payload(include_consented_transcript_summary: bool) -> dict[str, Any]:
    metrics = await collect_metrics()
    rows = await tester_rows(include_consented_transcript_summary)
    status = "ok"
    if metrics.get("status") != "ok" or any(r.stuck_reasons for r in rows):
        status = "warn"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "mode": {
            "health_and_stuck_state": True,
            "consented_transcript_summary": include_consented_transcript_summary,
            "raw_transcript_content_included": False,
        },
        "metrics": metrics,
        "testers": [asdict(r) for r in rows],
    }
    return payload


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate HDE family-test monitor artifacts")
    p.add_argument("--json", type=Path, default=OUTPUT_JSON)
    p.add_argument("--html", type=Path, default=OUTPUT_HTML)
    p.add_argument("--include-consented-transcript-summary", action="store_true", help="Report transcript/artifact counts only for actively consented testers; never dumps raw transcript content.")
    p.add_argument("--stdout", action="store_true")
    return p


def main() -> None:
    args = parser().parse_args()
    payload = asyncio.run(build_payload(args.include_consented_transcript_summary))
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.html.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    args.html.write_text(render_html(payload), encoding="utf-8")
    if args.stdout:
        print(json.dumps({"status": payload["status"], "json": str(args.json), "html": str(args.html), "testers": len(payload["testers"]), "stuck": sum(1 for r in payload["testers"] if r["stuck_reasons"])}, indent=2))


if __name__ == "__main__":
    main()
