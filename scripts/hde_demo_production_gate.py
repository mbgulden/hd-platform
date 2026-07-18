#!/usr/bin/env python3
"""HDE demo production gate checklist.

This is intentionally a blocker-oriented gate, not a deploy script. It collects the
five human/live proofs Michael asked for before production and checks machine
proof that the demo lifecycle is scheduled.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REQUIRED_EVIDENCE = {
    "telegram_clickthrough": "HDE_DEMO_TELEGRAM_E2E_OK",
    "container_provisioning": "HDE_DEMO_CONTAINER_E2E_OK",
    "paid_upgrade_continuity": "HDE_DEMO_PAID_UPGRADE_E2E_OK",
    "edge_waf_rate_limit": "HDE_DEMO_EDGE_RATE_LIMIT_OK",
    "reminder_messages": "HDE_DEMO_REMINDERS_OK",
}


def systemctl(*args: str) -> tuple[int, str]:
    proc = subprocess.run(["systemctl", *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    return proc.returncode, proc.stdout.strip()


def main() -> int:
    missing = []
    evidence = {}
    for name, env in REQUIRED_EVIDENCE.items():
        value = os.getenv(env, "").strip()
        evidence[name] = bool(value)
        if not value:
            missing.append({"gate": name, "required_env_or_artifact": env})

    timer_rc, timer_state = systemctl("is-active", "hde_demo_trial_lifecycle_staging.timer")
    service_template = Path("deploy/systemd/hde_demo_trial_lifecycle_staging.service")
    timer_template = Path("deploy/systemd/hde_demo_trial_lifecycle_staging.timer")
    templates_present = service_template.exists() and timer_template.exists()

    result = {
        "status": "PASS" if not missing and timer_rc == 0 and templates_present else "BLOCKED",
        "timer_active": timer_rc == 0,
        "timer_state": timer_state,
        "tracked_systemd_templates_present": templates_present,
        "evidence": evidence,
        "missing_before_production": missing,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
