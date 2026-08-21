"""GRO-4823 — Rebind guard for the tenant router's chat→user claim path.

Background
----------
``bot_instances.telegram_user_id`` binds a Telegram chat to exactly one HDE
account. The claim path in ``hde_tenant_router.process_start_token`` used to
*silently steal* the binding when a different account signed in from the same
phone: it set the prior row's ``telegram_user_id = NULL`` and rebound the chat
to the new user with no check on who the prior owner was. In production that
left the owner's phone bound to a 14-day demo account, so every message was
answered with the demo's seeded chart instead of the owner's (GRO-4823).

This module centralises the rebind decision so it is unit-testable without a
database connection:

* a **protected** account (real, non-demo — ``access_status == "paid"``, or
  ``is_premium == true``) can never be silently stripped of its chat binding;
* a non-protected (demo / expired-demo / deactivated) prior binding may be
  reclaimed, but every such rebind is logged at WARNING so it is visible in
  the fleet logs;
* refusals are logged at ERROR with the full before/after identity.

The schema layer already enforces at-most-one *live* binding per chat via the
unique index ``ix_bot_instances_telegram_user_id`` (Postgres treats NULLs as
distinct, so unbound rows never collide). The guard covers the one case that
constraint cannot catch: an *intentional* NULL-then-rebind sequence.

Stdlib-only on purpose — the router imports this, and the tests must load it
without a DB session.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Access statuses that mark a *real* (non-demo) account. Everything else
# (demo, expired_demo, inactive, trial) is reclaimable by another sign-in.
PROTECTED_ACCESS_STATUSES = frozenset({"paid"})


@dataclass(frozen=True)
class RebindDecision:
    """Outcome of a chat-binding rebind evaluation.

    ``reason`` is operator-facing: it must be safe to log verbatim (no
    secrets, no phone numbers — chat identity is supplied by the caller).
    """

    allowed: bool
    reason: str


def is_protected_account(user: Optional[object]) -> bool:
    """Return True if ``user`` is a real (non-demo) account whose chat
    binding must not be silently stripped.

    Duck-typed on purpose so tests can pass a plain namespace object with
    ``access_status`` / ``is_premium`` attributes.
    """
    if user is None:
        return False
    access = (getattr(user, "access_status", None) or "paid").lower()
    if access in PROTECTED_ACCESS_STATUSES:
        return True
    return bool(getattr(user, "is_premium", False))


def _access_label(user: Optional[object]) -> str:
    return repr(getattr(user, "access_status", None))


def evaluate_rebind(prior_user: Optional[object], new_user: object) -> RebindDecision:
    """Decide whether a chat binding may move from ``prior_user`` to ``new_user``.

    Rules:
    * ``prior_user is None``            -> allow (chat was unbound; normal first bind).
    * same user id                      -> allow (self re-claim, e.g. invite re-use).
    * prior owner protected (paid)      -> REFUSE (the silent-steal bug).
    * prior owner non-protected (demo,
      expired demo, deactivated)        -> allow, caller must log a REBIND ALERT.

    ``prior_user`` / ``new_user`` are duck-typed (``id``, ``access_status``,
    ``is_premium``) so this is testable without SQLAlchemy models.
    """
    if prior_user is None:
        return RebindDecision(allowed=True, reason="chat was unbound")

    prior_id = getattr(prior_user, "id", None)
    new_id = getattr(new_user, "id", None)
    if new_id is not None and prior_id is not None and prior_id == new_id:
        return RebindDecision(allowed=True, reason="same user re-claiming own chat")

    if is_protected_account(prior_user):
        return RebindDecision(
            allowed=False,
            reason=(
                "prior owner is a protected (real/paid) account "
                f"(user_id={prior_id}, access_status={_access_label(prior_user)})"
            ),
        )

    return RebindDecision(
        allowed=True,
        reason=(
            "prior owner is a non-protected account "
            f"(user_id={prior_id}, access_status={_access_label(prior_user)}) — reclaiming"
        ),
    )
