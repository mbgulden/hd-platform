#!/usr/bin/env python3
"""fleet_audit.py — HDE guest-fleet build matrix (HFG-FLEET-MANIFEST).

One command reproduces the full guest matrix as guest_fleet.json:
  per guest: id, status, container state, server build hash + line count,
  last-sync (mtime), .build marker (when present, see HFG-DRIFT-CANARY).

Status model (derived, not hardcoded per guest):
  live           container guest-hermes-<id> is running
  decommissioned no container AND guest is in DECOMMISSIONED (40, 42 per
                 Michael, 2026-08-19: "Leave 40/42 as is")
  down           no container, not known decommissioned -> needs a human
  drift          running but server hash != canonical template hash
                 (reported alongside live/decommissioned in "drift": true)

Exit codes: 0 = ok (drift may be reported), 2 = drift present with --strict.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time

GUEST_ROOT = "/home/ubuntu/users"
TEMPLATE = "/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py"
MANIFEST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "guest_fleet.json")
DECOMMISSIONED = {40, 42}  # Michael decision 2026-08-19
KNOWN_GUESTS = [2, 3, 23, 29, 30, 31, 32, 38, 39, 40, 42, 43]


def md5_of(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: str) -> int:
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def container_states() -> dict:
    """Return {container_name: status} for all guest-hermes containers (incl. stopped)."""
    out = {}
    try:
        r = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=guest-hermes-",
             "--format", "{{.Names}}\t{{.State}}"],
            capture_output=True, text=True, timeout=60,
        )
        for line in r.stdout.splitlines():
            if "\t" in line:
                name, state = line.split("\t", 1)
                out[name.strip()] = state.strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"WARN: could not query docker: {e}", file=sys.stderr)
    return out


def audit_guest(guest_id: int, containers: dict, template_hash: str) -> dict:
    gdir = os.path.join(GUEST_ROOT, f"guest_{guest_id}")
    server = os.path.join(gdir, "guest_agent_server.py")
    rec = {
        "id": guest_id,
        "dir": gdir,
        "server": server,
        "build_hash": None,
        "lines": None,
        "last_sync_utc": None,
        "build_marker": None,
        "marker_stale": False,
        "container": None,
        "container_state": None,
        "drift": False,
    }
    if os.path.isfile(server):
        rec["build_hash"] = md5_of(server)
        rec["lines"] = line_count(server)
        mtime = os.path.getmtime(server)
        rec["last_sync_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(mtime))
        marker = os.path.join(gdir, ".build")
        if os.path.isfile(marker):
            with open(marker) as f:
                rec["build_marker"] = f.read().strip()
            # Canary detector: running build must match the marker fleet_sync
            # wrote. Mismatch = someone edited the file outside the sync path
            # (hand-edit, failed sync, old process). Flagged, never silent.
            if rec["build_marker"].split() and rec["build_marker"].split()[0] != rec["build_hash"]:
                rec["marker_stale"] = True
                print(f"DRIFT-MARKER: guest_{guest_id} running hash "
                      f"{rec['build_hash'][:8]} != marker {rec['build_marker'].split()[0][:8]}",
                      file=sys.stderr)
        rec["drift"] = rec["build_hash"] != template_hash
    else:
        rec["drift"] = True  # missing server == maximal drift
        print(f"ERROR: guest_{guest_id} has no server file", file=sys.stderr)

    cname = f"guest-hermes-{guest_id}"
    rec["container"] = cname if cname in containers else None
    rec["container_state"] = containers.get(cname)

    if rec["container_state"] == "running":
        rec["status"] = "live"
    elif guest_id in DECOMMISSIONED:
        rec["status"] = "decommissioned"
    else:
        rec["status"] = "down"  # unexpected; human decides
    return rec


def main() -> int:
    strict = "--strict" in sys.argv
    template_hash = md5_of(TEMPLATE) if os.path.isfile(TEMPLATE) else None
    if template_hash is None:
        print(f"ERROR: template not found: {TEMPLATE}", file=sys.stderr)
        return 1

    containers = container_states()
    # Real fleet dirs are exactly guest_<int>. Legacy scaffolds (guest_hermes,
    # guest_hermes_1) are NOT fleet members — do not fullmatch them in.
    detected = set()
    for d in os.listdir(GUEST_ROOT):
        m = re.fullmatch(r"guest_(\d+)", d)
        if m:
            detected.add(int(m.group(1)))
    guests = sorted(set(KNOWN_GUESTS) | detected)

    fleet = {
        "schema_version": "1.0.0",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "template": TEMPLATE,
        "template_hash": template_hash,
        "decommissioned": sorted(DECOMMISSIONED),
        "guests": [audit_guest(g, containers, template_hash) for g in guests],
    }

    with open(MANIFEST_PATH, "w") as f:
        json.dump(fleet, f, indent=2)

    print(f"template {template_hash} ({line_count(TEMPLATE)} lines)")
    print(f"{'guest':<8}{'status':<16}{'lines':<7}{'hash':<10}{'container':<18}{'drift'}")
    live_drift = 0
    for g in fleet["guests"]:
        # Drift is operationally meaningful only for the live fleet.
        # Decommissioned workspaces are frozen by owner decision (40/42) —
        # their hash may differ from the template without being a problem.
        flagged = g["drift"] and g["status"] in ("live", "down")
        live_drift += flagged
        print(f"{g['id']:<8}{g['status']:<16}{str(g['lines']):<7}"
              f"{(g['build_hash'] or '-')[:8]:<10}{(g['container'] or '-'):<18}"
              f"{'DRIFT' if flagged else ''}")
    print(f"\nwrote {MANIFEST_PATH} — {len(fleet['guests'])} guests, "
          f"{live_drift} live-drifted")
    return 2 if (strict and live_drift) else 0


if __name__ == "__main__":
    sys.exit(main())
