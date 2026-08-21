#!/usr/bin/env python3
"""fleet_sync.py — HDE guest-fleet one-command sync (HFG-FLEET-SYNC).

Syncs the canonical template guest_agent_server.py to all LIVE guests:
  1. read the fleet manifest (fleet_audit.py) to learn who is live
  2. for each live guest whose build_hash != template:
       - write .bak-<UTC stamp> rollback of the current file
       - copy template, restore 1000:1000 ownership (container user)
       - md5-verify the copy
       - write .build marker (hash + lines) for the drift canary
  3. docker restart each changed container
  4. poll in-container /docs until 200 (health gate before Done)

Safety:
  - only guests with status 'live' are touched; decommissioned/down are skipped
  - nothing is ever deleted (backups are additive)
  - --dry-run reports what would happen without writing/restarting
  - idempotent: if every live guest already matches, prints 'all current'
    and touches nothing (no copies, no restarts)

Exit codes: 0 ok, 1 hard failure (verify/health), 2 partial (some guests failed).
"""

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = "/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py"
MANIFEST = os.path.join(HERE, "guest_fleet.json")
HEALTH_TIMEOUT_S = 90
HEALTH_POLL_S = 5
CONTAINER_USER = "1000:1000"


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: str) -> int:
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def run(cmd, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def load_manifest():
    if not os.path.isfile(MANIFEST):
        print("manifest missing — running fleet_audit.py first")
        r = run([sys.executable, os.path.join(HERE, "fleet_audit.py")])
        if r.returncode not in (0, 2):
            print(r.stdout, file=sys.stderr)
            raise SystemExit(1)
    with open(MANIFEST) as f:
        return json.load(f)


def sync_guest(guest: dict, template_hash: str, dry_run: bool) -> dict:
    gid = guest["id"]
    server = guest["server"]
    result = {"id": gid, "changed": False, "backup": None, "hash_ok": None,
              "marker": None, "restarted": False, "healthy": None, "error": None}
    if guest["status"] != "live":
        result["error"] = f"skipped (status={guest['status']})"
        return result
    if guest["build_hash"] == template_hash:
        result["error"] = "already current"
        return result

    result["changed"] = True
    if dry_run:
        result["error"] = "would sync (dry-run)"
        return result

    # 1. rollback backup
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup = f"{server}.bak-{stamp}"
    subprocess.run(["cp", server, backup], check=True)
    result["backup"] = backup

    # 2. copy + ownership
    subprocess.run(["cp", TEMPLATE, server], check=True)
    run(["chown", CONTAINER_USER, server])

    # 3. hash verify
    result["hash_ok"] = md5_of(server) == template_hash
    if not result["hash_ok"]:
        result["error"] = "HASH MISMATCH after copy — restore backup"
        subprocess.run(["cp", backup, server], check=True)
        return result

    # 4. .build marker (drift canary input)
    marker = os.path.join(os.path.dirname(server), ".build")
    with open(marker, "w") as f:
        f.write(f"{template_hash} {line_count(server)}\n")
    result["marker"] = "written"

    # 5. restart container
    cname = f"guest-hermes-{gid}"
    r = run(["docker", "restart", cname], timeout=120)
    if r.returncode != 0:
        result["error"] = f"restart failed: {r.stderr.strip()[:200]}"
        return result
    result["restarted"] = True

    # 6. health gate: poll in-container /docs
    deadline = time.time() + HEALTH_TIMEOUT_S
    while time.time() < deadline:
        h = run(["docker", "exec", cname, "python3", "-c",
                 "import urllib.request;urllib.request.urlopen('http://localhost:8000/docs')"],
                timeout=20)
        if h.returncode == 0:
            result["healthy"] = True
            return result
        time.sleep(HEALTH_POLL_S)
    result["healthy"] = False
    result["error"] = "health check timed out — see docker logs"
    return result


def main():
    dry = "--dry-run" in sys.argv
    if not os.path.isfile(TEMPLATE):
        print(f"ERROR: template missing: {TEMPLATE}", file=sys.stderr)
        return 1
    template_hash = md5_of(TEMPLATE)
    manifest = load_manifest()

    live = [g for g in manifest["guests"] if g["status"] == "live"]
    stale = [g for g in live if g["build_hash"] != template_hash]

    print(f"template {template_hash} ({line_count(TEMPLATE)} lines) | "
          f"live={len(live)} stale={len(stale)} dry_run={dry}")

    if not stale:
        print("all current — nothing to do (no copies, no restarts)")
        return 0

    failures = 0
    for g in stale:
        r = sync_guest(g, template_hash, dry)
        benign = ("skipped", "already current", "would sync (dry-run)")
        if r.get("error") and not any(r["error"].startswith(b) for b in benign):
            failures += 1
        print(f"guest {g['id']:<3} changed={r['changed']!s:<6} "
              f"backup={os.path.basename(r['backup']) if r['backup'] else '-':<26} "
              f"hash_ok={r['hash_ok']} restarted={r['restarted']} "
              f"healthy={r['healthy']} {r['error'] or ''}")
    print(f"\n{'DRY-RUN ' if dry else ''}done: {len(stale)} target, {failures} failed")
    if failures:
        return 2 if failures < len(stale) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
