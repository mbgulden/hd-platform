# GRO-4010 — HDE green North Star progression gate

## North Star

Human Design Engine is only green when it turns a report into a daily work product loop:

1. **Understand the map** — the user can identify the relevant design signal without reading the whole report again.
2. **Choose one aligned action** — the product recommends a concrete next step tied to the user's design and current journey stage.
3. **Practice today** — the action is embodied, nervous-system-aware, and small enough to complete in one day.
4. **Reflect** — the user records what changed, what resisted, and what the next calibration should be.
5. **Continue with community momentum** — the loop invites support/accountability without making community a prerequisite for progress.

Reports are maps. The product is not green until the map produces repeated daily action and measurable life-change.

## Parent-epic gate

`GRO-4010` is the parent epic. It should not be marked green/Done while any child remains incomplete.

Current child dependency order:

1. `GRO-4011` — define the daily nervous-system work product loop.
2. `GRO-4012` — map report outputs to individualized next actions and the Sanctuary journey.
3. `GRO-4013` — design the retention/community invitation funnel.
4. `GRO-4014` — add content/events for daily “live your design” progression.
5. `GRO-4015` — validate with family/test users and close product-fit gaps.

## Verification artifact

Run:

```bash
set -a
source /home/ubuntu/.hermes/profiles/orchestrator/.env 2>/dev/null || source /home/ubuntu/.hermes/profiles/ned/.env.bak
set +a
node scripts/hde-green-status.mjs GRO-4010
```

The verifier queries Linear directly and prints JSON with:

- parent issue state and labels;
- child count;
- completed child count;
- incomplete child identifiers, titles, states, and labels;
- `green: true` only when every child is `Done`.

Exit codes:

- `0` — parent epic is green by dependency state.
- `1` — parent epic is not green because at least one child is still incomplete.
- `2` — missing `LINEAR_API_KEY`.
- `3` — parent issue could not be found.

## Current result from this implementation pass

The verifier is implemented and live-queries Linear. On this pass it reported:

- child count: 5;
- done children: 1;
- incomplete children: `GRO-4012`, `GRO-4013`, `GRO-4014`, `GRO-4015`;
- `green: false`.

That is the correct result. The parent epic should move to review with evidence that the gate exists, but it is not production-green until the remaining children are completed and verified individually.
