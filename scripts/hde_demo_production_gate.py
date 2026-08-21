#!/usr/bin/env python3
"""HDE demo production gate checklist.

This is intentionally a blocker-oriented gate, not a deploy script. It checks
live/human proof artifacts plus machine-checkable lifecycle/reminder/rate-limit
guards for the configured environment.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(os.getenv("HDE_REPO_ROOT", Path(__file__).resolve().parents[1]))
RUNTIME_DIR = Path(os.getenv("HDE_RUNTIME_DIR", REPO_ROOT / ".runtime"))
EVIDENCE_FILE = Path(os.getenv("HDE_DEMO_PRODUCTION_EVIDENCE_FILE", RUNTIME_DIR / "demo_production_evidence.json"))
EDGE_RATE_LIMIT_FILE = Path(os.getenv("HDE_DEMO_EDGE_RATE_LIMIT_FILE", RUNTIME_DIR / "demo_edge_rate_limit.json"))
LIFECYCLE_TIMER = os.getenv("HDE_DEMO_LIFECYCLE_TIMER", "hde_demo_trial_lifecycle.timer")
REMINDER_TIMER = os.getenv("HDE_DEMO_REMINDER_TIMER", "hde_demo_reminders.timer")
LIFECYCLE_TEMPLATE_PREFIX = os.getenv("HDE_DEMO_LIFECYCLE_TEMPLATE_PREFIX", "hde_demo_trial_lifecycle")
REMINDER_TEMPLATE_PREFIX = os.getenv("HDE_DEMO_REMINDER_TEMPLATE_PREFIX", "hde_demo_reminders")
TEMPLATE_DIR = Path(os.getenv("HDE_DEMO_SYSTEMD_TEMPLATE_DIR", REPO_ROOT / "scripts" / "systemd"))

REQUIRED_HUMAN_EVIDENCE = {
    "telegram_clickthrough": "HDE_DEMO_TELEGRAM_E2E_OK",
    "container_provisioning": "HDE_DEMO_CONTAINER_E2E_OK",
    "paid_upgrade_continuity": "HDE_DEMO_PAID_UPGRADE_E2E_OK",
}


def systemctl(*args: str) -> tuple[int, str]:
    proc = subprocess.run(["systemctl", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return proc.returncode, proc.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def truthy_env_or_artifact(name: str, env_name: str, artifacts: dict[str, Any]) -> bool:
    if os.getenv(env_name, "").strip():
        return True
    return bool(artifacts.get(name))


def template_pair_present(prefix: str) -> bool:
    return (TEMPLATE_DIR / f"{prefix}.service").exists() and (TEMPLATE_DIR / f"{prefix}.timer").exists()


def main() -> int:
    artifacts = load_json(EVIDENCE_FILE)
    missing: list[dict[str, str]] = []
    evidence: dict[str, bool] = {}

    for name, env in REQUIRED_HUMAN_EVIDENCE.items():
        value = truthy_env_or_artifact(name, env, artifacts)
        evidence[name] = value
        if not value:
            missing.append({"gate": name, "required_env_or_artifact": env})

    lifecycle_timer_rc, lifecycle_timer_state = systemctl("is-active", LIFECYCLE_TIMER)
    reminder_timer_rc, reminder_timer_state = systemctl("is-active", REMINDER_TIMER)
    lifecycle_templates_present = template_pair_present(LIFECYCLE_TEMPLATE_PREFIX)
    reminder_templates_present = template_pair_present(REMINDER_TEMPLATE_PREFIX)
    reminder_script_present = (REPO_ROOT / "scripts" / "hde_demo_reminders.py").exists()

    reminders_ok = bool(os.getenv("HDE_DEMO_REMINDERS_OK", "").strip()) or (reminder_timer_rc == 0 and reminder_templates_present and reminder_script_present)
    evidence["reminder_messages"] = reminders_ok
    if not reminders_ok:
        missing.append({"gate": "reminder_messages", "required_env_or_artifact": f"HDE_DEMO_REMINDERS_OK or active {REMINDER_TIMER}"})

    edge_artifact = load_json(EDGE_RATE_LIMIT_FILE)
    edge_ok = bool(os.getenv("HDE_DEMO_EDGE_RATE_LIMIT_OK", "").strip()) or bool(edge_artifact.get("rule_id") and edge_artifact.get("host") and edge_artifact.get("path") == "/api/demo/start")
    evidence["edge_waf_rate_limit"] = edge_ok
    if not edge_ok:
        missing.append({"gate": "edge_waf_rate_limit", "required_env_or_artifact": "HDE_DEMO_EDGE_RATE_LIMIT_OK or .runtime/demo_edge_rate_limit.json"})

    result = {
        "status": "PASS" if not missing and lifecycle_timer_rc == 0 and lifecycle_templates_present else "BLOCKED",
        "repo_root": str(REPO_ROOT),
        "lifecycle_timer": LIFECYCLE_TIMER,
        "lifecycle_timer_active": lifecycle_timer_rc == 0,
        "lifecycle_timer_state": lifecycle_timer_state,
        "lifecycle_templates_present": lifecycle_templates_present,
        "reminder_timer": REMINDER_TIMER,
        "reminder_timer_active": reminder_timer_rc == 0,
        "reminder_timer_state": reminder_timer_state,
        "reminder_templates_present": reminder_templates_present,
        "edge_rate_limit_artifact_present": edge_ok,
        "evidence": evidence,
        "missing_before_production": missing,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
