# Guide Deconditioning Runtime Workflow

**Status:** Current staging operating reference
**Last verified:** 2026-07-15
**Canonical methodology note:** `/home/ubuntu/work/belief-deprogrammer/okf/research/hde-guide-deconditioning-runtime-workflow-2026-07-15.md`

## Purpose

This document records the Human Design Engine guide runtime workflow used for the deconditioning bot inside the `humandesignengine.com` platform.

The key correction: **George is not the architecture**. George is only one possible guide name. The platform must support any user-selected guide/persona name through runtime configuration.

## Architecture summary

```text
Telegram head bot
  ↓
HDE tenant router / onboarding
  ↓
Private guest runtime per user
  ↓
LLM-first Sanctuary conversation
  + deterministic rails for state mutations/artifacts
  + reusable canary contract checks
```

## Canonical files

| Concern | Path |
|---|---|
| Guest runtime template | `/home/ubuntu/guest_hermes_bot/guest_agent_server.py` |
| Live guest 23 runtime | `/home/ubuntu/users/guest_23/guest_agent_server.py` |
| Reusable guest canary | [`scripts/hde_guest_canary.py`](../../scripts/hde_guest_canary.py) |
| Head-bot scaling runbook | [`docs/hde-head-bot-scaling-runbook.md`](../hde-head-bot-scaling-runbook.md) |
| Router | [`scripts/hde_tenant_router.py`](../../scripts/hde_tenant_router.py) |
| Somatic cue library | [`scripts/somatic_cues.json`](../../scripts/somatic_cues.json) |
| Deconditioning OKF source | `/home/ubuntu/work/belief-deprogrammer/okf/research/hde-guide-deconditioning-runtime-workflow-2026-07-15.md` |

## Guide-neutral identity

Runtime prompt identity must be configurable:

```python
guide_name = (
    os.getenv("GUEST_GUIDE_NAME")
    or os.getenv("HDE_GUIDE_NAME")
    or "the user's Human Design guide"
).strip()
```

The prompt should say:

```text
You are {guide_name} inside Human Design Engine Sanctuary.
Reply as {guide_name} in plain text.
```

Do **not** hardcode `George` in the guest runtime. The canary should fail if `George` appears in the runtime prompt/template.

## Runtime contract

The runtime prompt is organized as:

1. **Guide Constitution** — safety and truth constraints.
2. **Guide Culture** — Sanctuary voice and pacing.
3. **Guide Freedoms** — permission to be useful, take the swing, and improvise when grounded.
4. **Graceful Deconditioning + Belief Work** — named belief-work protocol.
5. **Tool/action policy** — server owns mutations/artifacts; guide narrates.
6. **Creative tools** — internal reasoning handles like `pattern_read`, `belief_work`, and `experiment_builder`.
7. **Polyvagal integration** — optional micro-practices as working reads, never diagnosis.
8. **Deterministic tools** — create/update profile, chart generation, comparisons, journal, PDFs, search.

## Graceful Deconditioning + Belief Work

The guide should identify limiting beliefs and survival patterns as old protection, not personal failure.

Required sequence:

1. Name the loop without shame.
2. Identify the protective belief.
3. Respect why it formed.
4. Show the cost of keeping it.
5. Map to Human Design mechanics when useful.
6. Separate truth from strategy.
7. Offer a replacement working belief as a hypothesis.
8. Give one small real-world experiment.
9. Ask what reality showed, not what fear predicted.
10. Close toward self-trust and needing the guide less.

Replacement belief shape:

```text
Old belief: “If I don’t ___, then ___.”
Updated belief: “I can ___ and still ___.”
Experiment: “This week, test it by ___.”
```

Never turn this into cheesy affirmations, forced positivity, diagnosis, spiritualized trauma, or guide-dependence.

## Deterministic rails

Use deterministic code for operations that must be reliable:

- first-impression greeting/reset guard,
- friction interrupt,
- chart/profile creation,
- single-field birth detail edits,
- immediate chart rebuild when a profile is complete,
- stored profile chart generation,
- stored profile relationship comparison,
- plural PDF/media path return,
- journal write/search/list,
- external factual search injection,
- workflow navigation such as help, what next, explain my chart, rebuild, compare, edit details.

Do **not** put a rigid static menu or wizard in front of the LLM for ordinary conversation.

## Guest canary command

Run server-side guest-runtime proof with:

```bash
cd /home/ubuntu/work/hd-platform-staging
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

This is focused guest-runtime verification, not live Telegram proof.

The canary should cover:

- Python compile,
- required services active,
- `guest-hermes-23` healthy,
- first-impression guard,
- non-George greeting such as `Hi Ember`,
- friction interrupt,
- progressive chart intake,
- natural date/time parsing,
- stored profile chart operation,
- single-field edit with immediate rebuild,
- workflow navigation,
- journal write/search,
- comparison with plural media metadata,
- permission architecture contract,
- graceful belief-work protocol markers,
- guide-name neutrality.

## Deployment workflow

1. Lock files before editing.
2. Edit `/home/ubuntu/guest_hermes_bot/guest_agent_server.py`.
3. Update docs and canary in the same work unit.
4. Copy runtime template into guest 23:

```bash
sudo cp /home/ubuntu/guest_hermes_bot/guest_agent_server.py \
  /home/ubuntu/users/guest_23/guest_agent_server.py
```

5. Restart and wait for health:

```bash
sudo docker restart guest-hermes-23
sudo docker inspect -f '{{.State.Health.Status}}' guest-hermes-23
```

6. Run canary:

```bash
cd /home/ubuntu/work/hd-platform-staging
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
```

7. Run frontend build when HDE repo files changed:

```bash
npm run build
```

8. For doc/runtime changes, create a fresh OS-safe `/tmp/hermes-verify-*` script using `tempfile.mkstemp`, run it, remove it, and report it as **focused ad-hoc verification**, not suite green.

## Live Telegram proof caveat

Bots cannot send themselves Telegram updates through the Bot API. Server-side guest canaries are necessary but not sufficient for live Telegram media proof.

Live Telegram proof still requires a real tester/user to message the bot while a watcher checks Telegram delivery, invitation linkage, and media uploads.

## Future-agent rules

- Do not hardcode George.
- Do not replace guide freedom with a larger prompt cage.
- Do not turn belief work into affirmation/manifestation copy.
- Do not claim one conversation permanently replaced a belief.
- Do not make the guide the user’s outsourced authority.
- Do not update the live guest runtime without updating the template, canary, and docs.
- Do not claim Telegram proof from server-side checks alone.
