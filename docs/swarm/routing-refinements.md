# Routing Refinements — Post-Pilot Adjustments (GRO-86)

Changes made to routing rules, agent selection, and verification after real-world use
of the orchestration router. Captures lessons from the pilot and edge cases encountered.

---

## Refinements from the Pilot

Based on the [router pilot report](./router-pilot-report.md) (49 tasks, 3 agents, 1 day),
these routing rules were refined:

---

## Refinement 1: AGY Scope Adherence Verification

**Before (pilot):** AGY's `bounded_scope` was advisory only. No post-task check for
scope breaches.

**Problem encountered:** 3 of 13 AGY tasks expanded slightly beyond `out_of_scope`.
All were benign (useful content), but one task added implementation details that weren't
requested.

**New rule:**
- AGY handoff now includes `scope_adherence` field (see [handoff-contracts](./handoff-contracts.md))
- `out_of_scope_breaches: <number>` is reported in every AGY handoff
- Breaches > 2 triggers a `warn` flag in verification
- Single benign breach is auto-accepted
- Breaches that add implementation details are flagged for Hermes review

**Implementation:**
```yaml
# Added to AGY handoff contract
scope_adherence:
  in_scope_covered: "full | partial | minimal"
  out_of_scope_breaches: <number>
  breach_details:
    - "description of what was breached and why"
```

---

## Refinement 2: Orchestrator Compression Threshold

**Before (pilot):** Compression threshold was 0.65 (650K tokens on DeepSeek 1M).

**Problem encountered:** During Hermes's 9-task documentation sequence, context grew to
~350K by task 7. At 0.65, compression wouldn't fire until 650K — leaving ~300K headroom
that could have been used for cost savings.

**New rule:** Compression threshold lowered to 0.50 (500K tokens). This was already
planned in [context-window-pruning](./context-window-pruning.md) (GRO-58) and the pilot
confirmed it's the right threshold.

**Cost savings:** Estimated ~$0.21/API call at typical usage. For 30 daily sessions,
~$2,300/year.

---

## Refinement 3: Context Pre-Loading Priority

**Before (pilot):** AGY received `context_links` but had to discover its own approach.

**Problem encountered:** AGY tasks with populated `context_links` finished ~40% faster.
Tasks without pre-loaded context spent the first 15-20 minutes discovering what was
already known.

**New rule:** The router now **requires** `context_links` for AGY research tasks when:
- The task builds on prior research in the same topic area
- Drive documents or existing reports exist
- Linear issues with relevant context are linked

If `context_links` is empty and the router detects prior work exists, it auto-populates
from recent AGY handoffs in the same topic area.

**Implementation:** Router searches `docs/` and recent AGY handoffs for related work.
Adds links to `context_links` before dispatching.

---

## Refinement 4: Parallel Research Default

**Before (pilot):** AGY's `max_sessions` defaulted to 1.

**Problem encountered:** AGY's 3-session parallel research (competitor analysis) was
highly effective. Independent research tasks benefit significantly from parallelism.

**New rule:** Router auto-sets `max_sessions: 2` when:
- The research task is independent (no sub-task dependencies)
- The task has no `stop_after` under 30 minutes
- AGY capacity is available (<5 active sessions)

If sub-tasks have dependencies, `max_sessions: 1` (sequential) is used.

**Capacity guard:** The router checks current AGY load before increasing parallelism.
If AGY is near capacity, parallelism stays at 1.

---

## Refinement 5: Jules Pre-Flight Checks

**Before (pilot):** Jules was not tested (docs-only pilot).

**Problem encountered:** While not encountered in the pilot, analysis of the Jules
workflow identified that Jules can silently fail on repos with broken CI or missing
dependencies.

**New rule:** Router runs three pre-flight checks before dispatching to Jules:
1. **CI check:** `main` branch CI is green (via GitHub API)
2. **Repo check:** Repo is accessible via `jules remote list --repo`
3. **Dependency check:** Package manager lockfile exists and is recent (<24h old)

If any pre-flight fails, the router reports the failure and doesn't dispatch to Jules.

**Implementation:** Pre-flight script at `ops/jules-preflight.sh`:
```bash
#!/usr/bin/env bash
# ops/jules-preflight.sh — Run before dispatching to Jules
REPO="$1"
# 1. CI green?
gh api "/repos/$REPO/commits/main/check-runs" --jq '.check_runs[] | select(.conclusion != "success")' | read && exit 1
# 2. Repo accessible?
jules remote list --repo "$REPO" > /dev/null 2>&1 || exit 1
# 3. Lockfile recent?
find . -maxdepth 2 -name 'package-lock.json' -mtime -1 | read || exit 1
echo "Pre-flight: PASS"
```

---

## Refinement 6: Codex Review Scheduling

**Before (pilot):** No Codex usage in pilot.

**Problem encountered:** Codex has a 3-hour token refresh cycle. Reviews dispatched
near the end of the cycle may be incomplete.

**New rule:** Router tracks Codex token refresh windows:
- Deep reviews (full audit) are scheduled within the **first 60 minutes** of the refresh cycle
- Shallow reviews (quick scan) can run anytime
- If Codex is in fallback mode (deepseek-v4-flash), reviews are flagged as "fallback quality"

**Implementation:** Router checks Codex token status before dispatching. If near exhaustion
(<30 min remaining), it delays the review or runs a shallow scan.

---

## Refinement 7: Escalation Trigger Refinements

**Before (pilot):** Escalation was defined per-template but not enforced by the router.

**Problem encountered:** The pilot had no failures, so escalation wasn't tested. But
the templates defined escalation paths that the router couldn't enforce.

**New rule:** Router now enforces these automatic escalations:

| Trigger | Action |
|---|---|
| Subagent timeout (exceeded `timeout_minutes`) | Auto-escalate to Hermes for triage |
| Subagent timeout × 2 (retry exhausted) | Auto-escalate to human (Slack `#eng-alerts`) |
| `secrets_clean` fail | **Immediate** escalation + key rotation alert |
| Jules CI failure (PR checks red) | Flag PR, do not auto-merge, notify via Linear comment |
| AGY `out_of_scope_breaches > 3` | Flag for human review before acceptance |
| Codex `verdict: blocked` | Auto-escalate to Hermes for investigation |

---

## New Patterns Discovered

### Pattern 1: Research → Implement → Review Pipeline

Discovered during documentation (not yet tested end-to-end):

```
Task Intake → Router classifies as multi-agent
  ↓
Phase 1: AGY → research/analysis → handoff with key_findings
  ↓
Phase 2: Jules → implement based on key_findings → PR opened
  ↓
Phase 3: Codex → review PR → verdict + recommendations
  ↓
Phase 4: Hermes → verify all handoffs → merge or escalate
```

**Status:** Partially validated (Phase 1 from pilot, Phases 2-4 documented but not tested).

### Pattern 2: Doc-First Development

Hermes wrote documentation templates first, then built the router around them. This
created a coherent system where every doc cross-references every other doc.

**Recommendation:** For any new subsystem, write the documentation templates first.
Implement against the docs, not the other way around.

### Pattern 3: Idempotent Branch Discipline

Branch discipline script (`ops/branch-discipline.py`) proved idempotent and safe to
call before every write. Zero branch conflicts in 49 tasks.

**Recommendation:** Call branch discipline before every file write, regardless of agent.
The script is a no-op if already on a feature branch — no performance cost.

---

## Edge Cases Handled

### Edge Case 1: Empty Goal

**Situation:** Task submitted with `goal: ""` or missing goal.

**Handling:** Router rejects immediately with message: "`goal` is required. Re-submit with
a one-sentence task objective."

### Edge Case 2: Preferred Agent Unavailable

**Situation:** `preferred_agent: jules` but Jules is at 300/300 session cap.

**Handling:** Router waits 15 minutes (one cron cycle) and retries. If still unavailable,
escalates to Hermes with a recommendation to either wait or manually implement.

### Edge Case 3: Verification Criteria Empty + Approval Required

**Situation:** `approval_required: true` but `verification_criteria` is empty.

**Handling:** Router rejects: "Approval-required tasks must have verification criteria.
Add at least one machine-checkable criterion."

### Edge Case 4: Mixed File Types (Code + Docs)

**Situation:** `files_to_modify` includes both `.ts` and `.md` files.

**Handling:** Router classifies as CODE (dominant type). If the `.md` is a README or
doc, Jules handles it alongside code. If the `.md` is a research deliverable, the task
is split: AGY handles the `.md`, Jules handles the `.ts`.

### Edge Case 5: Deploy With No Rollback Defined

**Situation:** `task_type: deployment_supervision` but no `rollback` artifact in inputs.

**Handling:** Router flags with a warning: "No rollback artifact provided. Deployment will
proceed, but auto-rollback is disabled." Adds a note to the Hermes orchestration prompt.

### Edge Case 6: AGY Partial Results on Timeout

**Situation:** AGY exceeds `stop_after` but has partial results.

**Handling:** Router accepts partial results. AGY handoff shows `status: partial` with
`time_stats.exceeded_stop_after: true`. Hermes reviews partial results and either accepts
as-is or dispatches a follow-up.

---

## Future Improvements

### Short-Term (Next Pilot)

1. **Automated router dispatch:** Replace manual Hermes coordination with GitHub Action that
   reads Linear labels and auto-dispatches.

2. **Jules integration test:** Exercise the full AGY → Jules → Codex → Hermes pipeline with
   real code changes.

3. **Verification as post-agent hook:** Run verification checklist automatically on agent
   completion instead of manually.

4. **Dashboard/metrics:** Track throughput, success rate, and verification results per agent.

### Medium-Term (Next Month)

5. **Agent capacity forecasting:** Predict when Jules will hit 300/day cap and pre-route
   to Hermes to avoid queue buildup.

6. **Smart retry with context enrichment:** When an agent fails, automatically enrich the
   prompt with failure details and re-submit.

7. **Cross-agent learning:** AGY research results automatically populate Jules's context
   for related implementation tasks.

8. **Escalation auto-routing:** Escalations automatically create Linear issues with full
   context, linked to the original task.

### Long-Term (Next Quarter)

9. **Agent performance scoring:** Track per-agent accuracy (verification pass rate) and
   speed (wall-clock per task type) to optimize routing over time.

10. **Dynamic parallelism:** Router learns which research tasks benefit from parallelism
    and auto-tunes `max_sessions`.

11. **Predictive routing:** Based on task intake fields, predict the best agent with a
    confidence score before dispatching.

12. **Human-in-the-loop dashboard:** Web UI for approving gated tasks, reviewing verification
    results, and manually re-routing.

---

## Summary of Rule Changes

| # | Rule Change | Reason | Impact |
|---|---|---|---|
| 1 | AGY scope adherence verified in handoff | Scope creep detected in 3/13 tasks | Better output quality; fewer surprises |
| 2 | Compression threshold 0.65 → 0.50 | Context grows faster than expected | ~$2,300/year cost savings |
| 3 | Auto-populate AGY context_links | Pre-loaded context saves ~40% time | Faster research completion |
| 4 | Default max_sessions: 2 for independent research | 3-session parallel was highly effective | ~2× research throughput |
| 5 | Jules pre-flight checks before dispatch | Prevent silent failures on broken repos | Higher Jules success rate |
| 6 | Codex review scheduling by token window | Avoid incomplete reviews | Better review quality |
| 7 | Router-enforced escalation triggers | Escalation was template-only, not enforced | Faster incident response |

---

## Cross-References

- Pilot results that drove these changes: [router-pilot-report](./router-pilot-report.md)
- Current routing rules: [routing-decision-matrix](./routing-decision-matrix.md)
- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
- How to use the system: [operator-quickstart](./operator-quickstart.md)
- Handoff contracts: [handoff-contracts](./handoff-contracts.md)
- Verification: [verification-checklist](./verification-checklist.md)
