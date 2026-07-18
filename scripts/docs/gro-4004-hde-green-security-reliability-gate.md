# GRO-4004 HDE GREEN security/reliability gate

GRO-4004 is the parent epic for Human Design Engine security, performance, and operational reliability. It is intentionally not a single "green" switch: the parent is green only after each child has its own production/staging proof.

## Dependency order

1. `GRO-4005` — Add Cloudflare Pages security headers safely.
2. `GRO-4006` — Fix free-reading CLS/layout stability.
3. `GRO-4007` — Protect public API health/diagnostic routing.
4. `GRO-4008` — Add production smoke cron for checkout/report delivery.
5. `GRO-4009` — Run final PWP + Lighthouse + API proof and publish green report.

## Gate command

Run the parent gate from the repository root:

```bash
node scripts/hde-green-ops-gate.mjs --json
```

With `LINEAR_API_KEY` in the environment, the command reads live Linear state for the child issues. Without credentials, it still prints the static dependency order and required evidence checklist.

Use the strict mode before calling the parent complete:

```bash
node scripts/hde-green-ops-gate.mjs --require-green
```

`--require-green` exits non-zero while any child remains outside a terminal done state. That is expected until all child tasks have independently captured their evidence.

## Parent-finalization rule

Do not mark GRO-4004 done from the parent branch alone. The parent can move forward only after the gate reports all children green and GRO-4009 has published the final PWP/Lighthouse/API proof.
