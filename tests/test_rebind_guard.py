"""GRO-4823: unit tests for the tenant-router rebind guard.

Run: /home/ubuntu/work/hd-platform/.venv/bin/python -m pytest \
    tests/test_rebind_guard.py -v

The guard is stdlib-only and duck-typed, so tests exercise the real decision
logic without a database connection — mirroring the existing
test_guest_naming_guard.py pattern (import module by file path).
"""

import importlib.util
import os
import sys
import types

GUARD_PATH = os.path.join(
    os.path.dirname(__file__), "..", "scripts", "hde_rebind_guard.py"
)


def _load_guard():
    if "hde_rebind_guard" in sys.modules:
        return sys.modules["hde_rebind_guard"]
    spec = importlib.util.spec_from_file_location("hde_rebind_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not build spec for {GUARD_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["hde_rebind_guard"] = module
    spec.loader.exec_module(module)
    return module


guard = _load_guard()
evaluate_rebind = guard.evaluate_rebind
is_protected_account = guard.is_protected_account


def _user(user_id, access_status="paid", is_premium=False):
    return types.SimpleNamespace(
        id=user_id,
        access_status=access_status,
        is_premium=is_premium,
    )


# ---- is_protected_account ----

def test_paid_account_is_protected():
    assert is_protected_account(_user(2, "paid", True)) is True


def test_premium_account_is_protected_even_if_access_not_paid():
    # A premium account whose access_status got set to something odd must still
    # be protected — the flag is the stronger signal.
    assert is_protected_account(_user(2, "trial", True)) is True


def test_demo_account_is_not_protected():
    assert is_protected_account(_user(43, "demo", False)) is False


def test_expired_demo_is_not_protected():
    assert is_protected_account(_user(43, "expired_demo", False)) is False


def test_inactive_is_not_protected():
    assert is_protected_account(_user(43, "inactive", False)) is False


def test_none_is_not_protected():
    assert is_protected_account(None) is False


def test_missing_attrs_fail_closed_to_protected():
    # A prior owner with no readable access_status is treated as PROTECTED
    # (fail-closed): an ambiguous/legacy account must never be silently stolen,
    # because users.access_status is NOT NULL DEFAULT 'paid' — the only way it is
    # absent is malformed/legacy data, and blocking a reclaim there is the safe
    # direction (the exact bug we are fixing is a false ALLOW, not a false REFUSE).
    assert is_protected_account(types.SimpleNamespace(id=9)) is True


# ---- evaluate_rebind ----

def test_no_prior_owner_allows_first_bind():
    d = evaluate_rebind(None, _user(2, "paid"))
    assert d.allowed is True


def test_same_user_reclaim_allows():
    d = evaluate_rebind(_user(2, "paid"), _user(2, "paid"))
    assert d.allowed is True
    assert "same user" in d.reason


def test_paid_prior_owner_is_refused():
    # The exact production bug: owner (user 2, paid) bound to the phone,
    # demo (user 43) signs in from the same phone -> must be REFUSED.
    d = evaluate_rebind(_user(2, "paid", True), _user(43, "demo", False))
    assert d.allowed is False
    assert "protected" in d.reason


def test_premium_prior_owner_is_refused():
    d = evaluate_rebind(_user(2, "trial", True), _user(43, "demo", False))
    assert d.allowed is False


def test_demo_prior_owner_is_reclaimed():
    d = evaluate_rebind(_user(43, "demo", False), _user(2, "paid", True))
    assert d.allowed is True
    assert "reclaiming" in d.reason
    assert "non-protected" in d.reason


def test_expired_demo_prior_owner_is_reclaimed():
    d = evaluate_rebind(_user(43, "expired_demo", False), _user(2, "paid"))
    assert d.allowed is True


def test_inactive_prior_owner_is_reclaimed():
    d = evaluate_rebind(_user(43, "inactive", False), _user(2, "paid"))
    assert d.allowed is True


def test_reason_strings_are_log_safe_no_pii():
    prior = _user(2, "paid", True)
    for d in (
        evaluate_rebind(prior, _user(43, "demo", False)),
        evaluate_rebind(_user(43, "demo"), _user(2, "paid")),
        evaluate_rebind(None, _user(2)),
    ):
        r = d.reason.lower()
        assert "gmail" not in r
        assert "8190664947" not in r
        assert "@" not in r
