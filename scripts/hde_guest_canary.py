#!/usr/bin/env python3
"""Focused HDE guest-runtime canary.

Exercises the private guest /api/message workflow without using Telegram:
- first impression / reset guard
- progressive chart intake with natural date/time
- per-person profile memory and reuse
- single-field profile edit
- workflow navigation: help/what-next/explain/rebuild
- journal shortcut and comparison multi-PDF metadata

This is an ad-hoc behavioral canary. It is not a replacement for a live
Telegram media canary, because bots cannot message themselves through Telegram.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any


def run(cmd: str, timeout: int = 60) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, timeout=timeout)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


class Canary:
    def __init__(self, guest_id: int, keep_artifacts: bool = False):
        self.guest_id = guest_id
        self.container = f"guest-hermes-{guest_id}"
        self.root = Path(f"/home/ubuntu/users/guest_{guest_id}")
        self.keep_artifacts = keep_artifacts
        self.checks: list[dict[str, str]] = []
        self.errors: list[dict[str, str]] = []
        self.ip = ""
        self.backup_index: str | None = None
        self.backup_history: str | None = None
        self.slug = "canary_guest"
        self.friend_slug = "canary_friend"

    def ok(self, condition: bool, label: str, detail: Any = "") -> None:
        entry = {"check": label, "detail": str(detail)}
        (self.checks if condition else self.errors).append(entry)

    def post(self, text: str, timeout: int = 240) -> dict[str, Any]:
        req = urllib.request.Request(
            f"http://{self.ip}:8000/api/message",
            data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())

    def setup(self) -> None:
        rc, out, err = run("python3 -m py_compile /home/ubuntu/guest_hermes_bot/guest_agent_server.py /home/ubuntu/guest_hermes_bot/daily_journal_mcp.py", 90)
        self.ok(rc == 0, "guest template Python files compile", err[:400])

        rc, out, err = run("systemctl is-active hde-reports.service hde_orchestrator_staging.service hde_router.service", 30)
        self.ok(rc == 0 and out.splitlines() == ["active", "active", "active"], "dependent services active", out or err)

        rc, out, err = run(f"sudo docker inspect -f '{{{{.State.Health.Status}}}}' {self.container}", 30)
        self.ok(rc == 0 and out == "healthy", f"{self.container} healthy", out or err)

        rc, out, err = run(f"sudo docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {self.container}", 30)
        self.ip = out.strip()
        self.ok(rc == 0 and bool(self.ip), f"{self.container} IP resolved", self.ip or err)

        index_path = self.root / "people" / "index.json"
        if index_path.exists():
            self.backup_index = index_path.read_text()
        history_path = self.root / "conversation_history.json"
        if history_path.exists():
            self.backup_history = history_path.read_text()

        self.cleanup_test_artifacts(reset_index=False)
        # Run against an isolated people index so an existing live profile does
        # not short-circuit the new-profile intake checks. The original index
        # is restored in the final cleanup.
        run(f"sudo mkdir -p {self.root}/people && sudo rm -f {self.root}/people/index.json", 30)

    def cleanup_test_artifacts(self, reset_index: bool = True) -> None:
        if self.keep_artifacts:
            return
        paths = [
            self.root / "conversation_state.json",
            self.root / "conversation_history.json",
            self.root / "greeting_state.json",
            self.root / "people" / self.slug,
            self.root / "people" / self.friend_slug,
            self.root / "charts" / "personal" / self.slug,
            self.root / "charts" / "friends" / self.slug,
            self.root / "charts" / "friends" / self.friend_slug,
        ]
        for path in paths:
            if path.is_dir():
                run(f"sudo rm -rf {path}", 30)
            else:
                run(f"sudo rm -f {path}", 30)
        # Remove canary journal rows/events so the live guest history is not polluted.
        run(f"python3 - <<'PY'\nimport sqlite3\npath={str(self.root / 'guest_journal.db')!r}\ntry:\n    conn=sqlite3.connect(path)\n    conn.execute(\"DELETE FROM journal_entries WHERE entry_text LIKE '%Canary felt clear but skeptical%' OR entry_text LIKE '%Canary continuity%'\")\n    conn.commit(); conn.close()\nexcept Exception:\n    pass\nPY", 30)
        run(f"sudo rm -rf {self.root}/coach_view", 30)
        if reset_index:
            history_path = self.root / "conversation_history.json"
            if self.backup_history is not None:
                tmp_history = Path(f"/tmp/hde-guest-canary-history-{os.getpid()}.json")
                tmp_history.write_text(self.backup_history)
                run(f"sudo cp {tmp_history} {history_path} && sudo chown 1000:1000 {history_path} && rm -f {tmp_history}", 30)
            else:
                run(f"sudo rm -f {history_path}", 30)
            index_path = self.root / "people" / "index.json"
            if self.backup_index is not None:
                tmp = Path(f"/tmp/hde-guest-canary-index-{os.getpid()}.json")
                tmp.write_text(self.backup_index)
                run(f"sudo mkdir -p {index_path.parent} && sudo cp {tmp} {index_path} && sudo chown 1000:1000 {index_path} && rm -f {tmp}", 30)
            else:
                run(f"sudo rm -f {index_path}", 30)

    def assert_no_bad_prompt(self, text: str, label: str) -> None:
        bad = ["YYYY-MM-DD", "three things", "I'll need three", "1. Birth date", "2. Birth time", "honest"]
        hit = [b for b in bad if b.lower() in text.lower()]
        self.ok(not hit, label, f"bad={hit}; response={text}")

    def exercise_first_impression(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json {self.root}/greeting_state.json", 30)
        r1 = self.post("/new").get("response", "")
        r2 = self.post("Hi Ember").get("response", "")
        self.ok(bool(r1 and r2), "first-impression reaches LLM", f"1={r1!r}; 2={r2!r}")
        self.assert_no_bad_prompt(r1 + "\n" + r2, "greeting has no birth-detail wall")

    def exercise_friction_repair(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("This is painful. Why are you asking again?").get("response", "")
        self.ok("clearing the stuck flow" in r.lower() and "here’s what i know" in r.lower(), "friction interrupt clears stuck flow and summarizes known state", r[:900])

    def exercise_missing_time_exploration(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        transcript = []
        for msg in [
            "build a chart for Canary Guest",
            "06/14/1990",
            "unknown",
            "explore",
            "Boise, Idaho",
            "morning",
            "1",
            "yes",
        ]:
            res = self.post(msg)
            transcript.append((msg, res.get("response", "")))
        unknown_reply = transcript[2][1]
        options_reply = transcript[5][1]
        final = transcript[-1][1]
        self.ok("won’t pretend" in unknown_reply.lower() and "explore" in unknown_reply.lower(), "unknown time offers exploration instead of silently treating noon as better data", unknown_reply[:700])
        self.ok("possible anchors" in options_reply.lower() and "authority" in options_reply.lower(), "time exploration offers chart-pattern anchors", options_reply[:900])
        self.ok("working hypothesis" in final.lower() and "Successfully generated chart" in final, "explored time generates clearly labeled chart", final[:900])
        profile_path = self.root / "people" / self.slug / "profile.json"
        if profile_path.exists():
            profile = json.loads(profile_path.read_text())
            confidence = profile.get("birth_confidence") or {}
            self.ok(confidence.get("birth_time") == "explored", "profile stores explored birth-time confidence", json.dumps(confidence, sort_keys=True))
        else:
            self.ok(False, "profile stores explored birth-time confidence", "profile missing")

    def exercise_name_capture_guard(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("Build a chart for the stinking little chart born 06/14/1990 at 9:30 AM in Boise, Idaho").get("response", "")
        lower = r.lower()
        self.ok("first and last name" in lower and "loose phrase" in lower, "loose phrase after for/under is not captured as a person name", r[:700])
        bad_profile = self.root / "people" / "the_stinking_little_chart" / "profile.json"
        self.ok(not bad_profile.exists(), "invalid phrase did not create fake person profile", bad_profile)

        self.post("I want to compare two charts")
        r2 = self.post("yes please just do it").get("response", "")
        self.ok("first and last name" in r2.lower() and "random phrase" in r2.lower(), "person-name stage rejects non-name phrases", r2[:700])
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)

    def exercise_partial_slot_clipboard(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        first = self.post("Build a chart for Slot Canary born 06/14/1990 at 9:30 AM").get("response", "")
        lower = first.lower()
        self.ok("last piece" in lower and "where" in lower and "birth date" not in lower and "birth time" not in lower, "partial chart request uses stated date/time and asks only missing location", first[:700])
        final = self.post("Boise, Idaho")
        body = final.get("response", "")
        self.ok("Successfully generated chart" in body, "partial slot clipboard continues to chart generation after missing location", body[:900])

    def exercise_personal_chart_memory(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        final = self.post("Put this one under Canary Guest. It should be 14 June 1990 at around sunrise in Boise, Idaho")
        body = final.get("response", "")
        self.ok("Successfully generated chart" in body and "06:03" in body, "one-shot natural correction generates chart and resolves sunrise", body[:700])
        self.ok("A more useful first read" in body and "conditioning pressure" in body.lower(), "chart response includes useful interpretive insight beyond anchor facts", body[:1200])
        self.ok(bool(final.get("pdf_path") or final.get("pdf_paths")), "personal chart returns PDF metadata", json.dumps({"pdf_path": final.get("pdf_path"), "pdf_paths": final.get("pdf_paths")}))

        profile_path = self.root / "people" / self.slug / "profile.json"
        self.ok(profile_path.exists(), "per-person profile written", profile_path)
        if profile_path.exists():
            profile = json.loads(profile_path.read_text())
            birth = profile.get("birth_input") or {}
            confidence = profile.get("birth_confidence") or {}
            self.ok(
                birth.get("birth_date") == "1990-06-14" and birth.get("birth_time") == "06:03" and birth.get("location") == "Boise, Idaho",
                "profile stores resolved birth input",
                json.dumps(birth, sort_keys=True),
            )
            self.ok(confidence.get("birth_time") in {"exact", "natural-clue"}, "profile stores birth-time confidence", json.dumps(confidence, sort_keys=True))

    def exercise_stored_chart_operates_system(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("Rebuild chart for Canary Guest")
        body = r.get("response", "")
        self.ok("Successfully generated chart" in body and "use those details" not in body.lower(), "stored chart request operates system without asking user to confirm known details", body[:900])
        self.ok(bool(r.get("pdf_path") or r.get("pdf_paths")), "stored chart rebuild returns PDF metadata", json.dumps({"pdf_path": r.get("pdf_path"), "pdf_paths": r.get("pdf_paths")}))

    def exercise_single_field_edit_operates_system(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("Update Canary Guest birth time to 7:15 AM")
        body = r.get("response", "")
        lower = body.lower()
        self.ok("updated canary guest" in lower and "rebuilt the chart" in lower and "want me to rebuild" not in lower, "single-field edit rebuilds chart without confirmation tax", body[:900])
        self.ok(bool(r.get("pdf_path") or r.get("pdf_paths")), "single-field edit returns rebuilt PDF metadata", json.dumps({"pdf_path": r.get("pdf_path"), "pdf_paths": r.get("pdf_paths")}))
        r2 = self.post("Canary Guest birth time is 7:45 AM")
        body2 = r2.get("response", "")
        self.ok("rebuilt the chart" in body2.lower() and "what do you want to edit" not in body2.lower(), "natural single-field edit updates default profile without a wizard", body2[:900])
        profile_path = self.root / "people" / self.slug / "profile.json"
        if profile_path.exists():
            birth = json.loads(profile_path.read_text()).get("birth_input") or {}
            self.ok(birth.get("birth_time") == "07:45", "natural single-field edit persists corrected birth time", json.dumps(birth, sort_keys=True))
        else:
            self.ok(False, "natural single-field edit persists corrected birth time", "profile missing")

    def exercise_llm_navigation(self) -> None:
        help_resp = self.post("what can you do?").get("response", "")
        static_bits = ["Pick the thread that fits today", "We have a real starting point", "We can start clean. No menu maze."]
        self.ok(not any(bit in help_resp for bit in static_bits), "help/what-can-you-do falls through to LLM", help_resp[:600])

    def exercise_permission_architecture_contract(self) -> None:
        template = Path("/home/ubuntu/guest_hermes_bot/guest_agent_server.py")
        live = Path(f"/home/ubuntu/users/guest_{self.guest_id}/guest_agent_server.py")
        prompt = template.read_text()
        self.ok(template.exists() and live.exists() and template.read_text() == live.read_text(), "permission architecture template is deployed to live guest runtime", str(live))
        required = [
            "Guide Constitution — never violate",
            "Guide Culture — embody always",
            "Guide Freedoms — use generously",
            "You are allowed to improvise, synthesize, speculate, challenge, reframe, use metaphor, and make intuitive leaps",
            "Take the swing when invited",
            "Use uncertainty etiquette",
            "Practice consentful depth",
            "Graceful Deconditioning + Belief Work — use when patterns repeat",
            "Name the loop without shame, identify the protective belief",
            "Replacement beliefs must be practical, psychologically plausible, and testable",
            "Graduation bias: every useful exchange should move the user toward needing less external interpretation",
            "Belief work response shape: pattern → old belief → why it made sense",
            "pattern_read: synthesize chart mechanics",
            "experiment_builder: create 1–3 real-world experiments",
            "authority_check: distinguish body signal from fear",
            "belief_work: identify inherited/conditioned beliefs",
            "relationship_mirror: compare two people",
            "time_rectification_explorer: when birth time is missing, explore likely windows",
            "thread_memory: summarize the active thread",
            "ritual_or_practice_builder: offer a simple grounding practice",
            "polyvagal_state_check: lightly read sympathetic/dorsal/ventral cues",
        ]
        missing = [needle for needle in required if needle not in prompt]
        self.ok(not missing, "permission architecture prompt contract is present", json.dumps(missing, indent=2))
        self.ok("Hard rules" not in prompt and "As an AI language model" not in prompt, "permission architecture avoids old hard-rule/disclaimer framing", "")
        hardcoded_name_hits = [line for line in prompt.splitlines() if "George" in line or "george" in line]
        self.ok(not hardcoded_name_hits, "runtime prompt does not hardcode George as the guide name", json.dumps(hardcoded_name_hits[:20], indent=2))

    def exercise_permission_architecture(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json {self.root}/conversation_history.json", 30)
        self.post("The pattern is I fall hard for intense people and then six months in it burns out.")
        r = self.post("What am I missing? Tell me the truth about this pattern.").get("response", "")
        lower = r.lower()
        takes_swing = any(phrase in lower for phrase in ("here’s my read", "here's my read", "my read", "my strongest read", "working hypothesis", "the pattern i see", "the thread i see", "before i swing", "here's what i see", "here’s what i see", "here's the truth", "here’s the truth", "i'll name the pattern")) or ("pattern" in lower and ("projector" in lower or "splenic" in lower or "3/5" in lower))
        avoids_wizard = not any(phrase in lower for phrase in ("what is your birth", "birth date", "birth time", "where were you born", "mm/dd/yyyy"))
        self.ok(takes_swing and avoids_wizard, "broad pattern question triggers take-the-swing mode instead of setup wizard", r[:900])

    def exercise_known_relationship_compare_operates_system(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("Compare me and Becca")
        body = r.get("response", "")
        pdfs = r.get("pdf_paths") or []
        lower = body.lower()
        self.ok("say ‘rebuild" not in lower and "send becca" not in lower and "birth details" not in lower, "stored Michael/Becca comparison operates system instead of asking for rebuild/details", body[:900])
        self.ok(("michael" in lower or "becca" in lower or "shared" in lower or "authority" in lower) and len(pdfs) >= 2, "stored Michael/Becca comparison returns relationship read and plural PDFs", json.dumps({"body": body[:700], "pdfs": pdfs}))

    def exercise_journal(self) -> None:
        r = self.post("Journal this: Canary felt clear but skeptical.").get("response", "")
        self.ok("Noted" in r or "journal" in r.lower(), "journal shortcut writes entry", r)
        r = self.post("search my journal for skeptical").get("response", "")
        self.ok("skeptical" in r.lower() or "Canary" in r, "journal search finds entry", r)

    def exercise_continuity_memory_lookup(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        history = [{
            "user": "Yesterday we named the continuity canary blue compass.",
            "assistant": "I marked blue compass as the continuity thread to look up later.",
            "ts": "2026-07-15T00:00:00Z",
        }]
        tmp = Path(f"/tmp/hde-guest-canary-continuity-history-{os.getpid()}.json")
        tmp.write_text(json.dumps(history))
        run(f"sudo cp {tmp} {self.root}/conversation_history.json && sudo chown 1000:1000 {self.root}/conversation_history.json && rm -f {tmp}", 30)
        self.post("Journal this: Canary continuity journal says blue compass belongs to the remembered thread.")
        r = self.post("Do you remember the blue compass from yesterday?").get("response", "")
        lower = r.lower()
        self.ok("i searched the saved journal" in lower and "recent session-history matches" in lower, "remember ask proactively searches journal and session history", r[:900])
        self.ok("blue compass" in lower and "keyword" not in lower, "remember ask answers from retained continuity without demanding a keyword", r[:900])
        self.ok("that is what i can actually find" in lower or "only know what was saved" in lower, "remember ask states retained-memory boundary", r[:900])

    def exercise_comparison(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        responses = []
        for msg in [
            "I want to compare two charts",
            "Canary Guest",
            "yes",
            "Canary Friend",
            "07/04/1992",
            "9:30 AM",
            "Seattle, Washington",
        ]:
            res = self.post(msg)
            responses.append((msg, res))
        final = responses[-1][1]
        body = final.get("response", "")
        pdfs = final.get("pdf_paths") or []
        self.ok("I built both charts" in body or "set them side by side" in body, "comparison returns relationship summary", body[:800])
        self.ok(len(pdfs) >= 2, "comparison returns plural PDF metadata", json.dumps(pdfs))

    def exercise_generic_stored_relationship_compare(self) -> None:
        run(f"sudo rm -f {self.root}/conversation_state.json", 30)
        r = self.post("Compare Canary Guest and Canary Friend")
        body = r.get("response", "")
        pdfs = r.get("pdf_paths") or []
        lower = body.lower()
        self.ok("what name" not in lower and "birth date" not in lower and "person 1" not in lower, "generic stored comparison avoids wizard prompts", body[:900])
        self.ok("canary guest" in lower and "canary friend" in lower and len(pdfs) >= 2, "generic stored comparison returns named relationship read and plural PDFs", json.dumps({"body": body[:700], "pdfs": pdfs}))

    def run_all(self) -> int:
        try:
            self.setup()
            if self.errors:
                return 1
            self.exercise_first_impression()
            self.exercise_friction_repair()
            self.exercise_missing_time_exploration()
            self.exercise_name_capture_guard()
            self.exercise_partial_slot_clipboard()
            self.exercise_personal_chart_memory()
            self.exercise_stored_chart_operates_system()
            self.exercise_single_field_edit_operates_system()
            self.exercise_llm_navigation()
            self.exercise_permission_architecture_contract()
            self.exercise_permission_architecture()
            self.exercise_known_relationship_compare_operates_system()
            self.exercise_journal()
            self.exercise_continuity_memory_lookup()
            self.exercise_comparison()
            self.exercise_generic_stored_relationship_compare()
            return 0 if not self.errors else 1
        except Exception as exc:  # noqa: BLE001 - canary should report any blocker.
            self.ok(False, "canary exception", repr(exc))
            return 1
        finally:
            self.cleanup_test_artifacts(reset_index=True)

    def report(self) -> dict[str, Any]:
        return {
            "status": "pass" if not self.errors else "fail",
            "guest_id": self.guest_id,
            "container": self.container,
            "checks": self.checks,
            "errors": self.errors,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run focused HDE guest workflow canary")
    parser.add_argument("--guest-id", type=int, default=23, help="guest id, e.g. 23 for guest-hermes-23")
    parser.add_argument("--keep-artifacts", action="store_true", help="leave canary people/charts/state in place for inspection")
    parser.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = parser.parse_args()

    canary = Canary(args.guest_id, keep_artifacts=args.keep_artifacts)
    code = canary.run_all()
    print(json.dumps(canary.report(), indent=2 if args.pretty else None))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
