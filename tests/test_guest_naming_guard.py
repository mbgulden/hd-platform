"""HFG-TEST-GUARD-02: unit tests for the guest naming guard.

Run: /home/ubuntu/work/hd-platform/.venv/bin/python -m pytest \
    hd-platform-staging/tests/test_guest_naming_guard.py -v

Imports the guest server module directly from the canonical template path
(the fleet's source of truth), so the test proves what actually ships.
"""

import importlib.util
import os
import sys

TEMPLATE = "/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py"


def _load_guest_server():
    if "guest_agent_server" in sys.modules:
        return sys.modules["guest_agent_server"]
    spec = importlib.util.spec_from_file_location("guest_agent_server", TEMPLATE)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build spec for {TEMPLATE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["guest_agent_server"] = module
    spec.loader.exec_module(module)
    return module


gs = _load_guest_server()


# --- flag cases: dev/test names must be blocked ---

def test_blocks_michael_gulden():
    assert gs.is_blocked_person_name("Michael Gulden") is True


def test_blocks_michael_alone():
    assert gs.is_blocked_person_name("Michael") is True


def test_blocks_becca():
    assert gs.is_blocked_person_name("Becca") is True


def test_blocks_becca_gulden():
    assert gs.is_blocked_person_name("Becca Gulden") is True


def test_blocks_test_and_variants():
    for n in ("Test", "tester", "Test Guest", "Guest Test"):
        assert gs.is_blocked_person_name(n) is True, n


def test_blocks_is_case_and_punct_insensitive():
    assert gs.is_blocked_person_name("michael GULDEN") is True
    assert gs.is_blocked_person_name("Michael.") is True


# --- pass-through cases: real client names must file normally ---

def test_passes_normal_two_token_name():
    assert gs.is_blocked_person_name("Jordan Smith") is False


def test_passes_another_real_name():
    assert gs.is_blocked_person_name("Keoni Nakamura") is False


def test_passes_single_real_token():
    assert gs.is_blocked_person_name("Keoni") is False


def test_blocked_set_shape():
    s = gs.BLOCKED_PERSON_NAMES
    assert "michael gulden" in s
    assert "becca" in s
    # env extension path exists (empty env -> built-ins only)
    assert all(isinstance(x, str) for x in s)
