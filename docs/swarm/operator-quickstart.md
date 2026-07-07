# Operator Quickstart — Day-One Guide to the Orchestration Router (GRO-85)

Everything you need to start using the multi-agent orchestration router in 15 minutes.
A checklist-driven guide for task submission, agent selection, output verification,
and escalation.

---

## Prerequisites

Before you start:

- [ ] You have access to the Linear project board (GRO-XX issues)
- [ ] You have access to the target GitHub repos
- [ ] You know which Slack channels to use for escalation (`#eng-alerts`, `#eng-deploys`)
- [ ] You've read the 1-page architecture overview: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)

---

## Step 1: Submit a Task (2 minutes)

Use the **[task intake template](./task-intake-template.md)**. Copy the YAML block, fill it in, and
submit via Linear or directly to Hermes.

### Minimum Viable Task

At minimum, every task needs:

```yaml
goal: >
  Fix the broken contact form — email submissions return 500.

verification_criteria:
  - "POST /api/contact returns 200 with valid payload"
  - "Email arrives in support@ inbox within 30s"

approval_required: false
```

**That's it.** The router auto-classifies everything else.

### Quick Decision: Which Fields to Fill

| If your task is... | Add these fields |
|---|---|
| A simple code fix | `goal`, `files_to_modify`, `verification_criteria` |
| A research question | `goal`, `bounded_scope`, `deliverable_path` |
| A production deploy | `goal`, `side_effects`, `verification_criteria`, `approval_required: true` |
| Multi-agent work | `goal`, `subagent_allocations` (or let Hermes decide) |
| An incident | `goal`, `inputs` (alert link, affected service), set `task_type: incident_response` |

---

## Step 2: Choose an Agent (1 minute)

Use the **[routing decision matrix](./routing-decision-matrix.md)** for the full decision tree.
Here's the quick version:

| You need... | Use... | How to invoke |
|---|---|---|
| **Code written/PR opened** | **Jules** | Label `agent:jules` on Linear, or `preferred_agent: jules` |
| **Research, analysis, docs** | **AGY** | Label `agent:agy` on Linear, or `preferred_agent: agy` |
| **Code reviewed/audited** | **Codex** | Label `agent:chatgpt55` on Linear, or `preferred_agent: codex` |
| **Coordination, deploy, incident** | **Hermes** | Default — no label needed, or `preferred_agent: hermes` |
| **Let the router decide** | **Auto** | Don't set `preferred_agent` (or set to `auto`) |

### Force-Routing

If you're sure which agent should handle it, set `preferred_agent` in the task intake:

```yaml
preferred_agent: jules  # forces Jules regardless of task type
```

The router will use your choice but logs a warning if the task type doesn't match the agent.

---

## Step 3: Verify Output (3 minutes)

Every agent output must pass the **[verification checklist](./verification-checklist.md)**.
Six checks in order:

| # | Check | Auto? | What it means |
|---|---|---|---|
| 1 | `file_exists` | ✅ Auto | Did the agent produce the expected file/PR? |
| 2 | `syntax_valid` | ✅ Auto | Is the output well-formed (valid JSON, YAML, etc.)? |
| 3 | `tests_pass` | ✅ Auto (Jules only) | Did the test suite pass? |
| 4 | `secrets_clean` | ✅ Auto | No API keys, tokens, or passwords in output? |
| 5 | `matches_spec` | 🔶 Manual | Does the output satisfy the success criteria? |
| 6 | `edge_cases_covered` | 🔶 Manual | Are error states and boundary conditions handled? |

### Quick Verification Commands

```bash
# Check a file exists and is non-empty
test -f "output/research/report.md" && test -s "output/research/report.md" && echo "PASS"

# Check a PR is accessible
curl -s -o /dev/null -w "%{http_code}" "https://github.com/owner/repo/pull/N" | grep -q 200 && echo "PASS"

# Check for leaked secrets (quick scan)
grep -qE 'sk-[a-zA-Z0-9]{20,}|-----BEGIN RSA PRIVATE KEY-----|eyJ[a-zA-Z0-9_-]{20,}\.' "file.md" && echo "FAIL: SECRETS FOUND" || echo "PASS"

# Check JSON validity
jq . output.json > /dev/null 2>&1 && echo "PASS" || echo "FAIL: invalid JSON"
```

### What to Do With Results

| Verification Result | Action |
|---|---|
| **All pass** | ✅ Accept the output. Task complete. |
| **`file_exists` fail** | 🔴 Reject — agent didn't produce expected output. Re-run or escalate. |
| **`syntax_valid` fail** | 🔴 Reject — output is malformed. Agent needs to re-generate. |
| **`tests_pass` fail** | 🔴 Reject — code is broken. Jules needs to fix and re-submit. |
| **`secrets_clean` fail** | 🔴 **REJECT + ALERT** — credentials leaked. Rotate immediately. Escalate. |
| **`matches_spec` fail** | 🔴 Reject — output doesn't meet success criteria. Send back with details. |
| **`edge_cases_covered` fail** | 🟡 Warn — accept with notes. Flag gaps for follow-up. |

---

## Step 4: Escalate When Needed (1 minute)

Use the escalation paths defined in the **[Hermes prompt template](./hermes-prompt-template.md)**.

### When to Escalate

| Situation | Escalation Channel | Urgency |
|---|---|---|
| **Secrets leaked in output** | `#eng-alerts` + key rotation | 🔴 Immediate |
| **Agent timed out twice** | `#eng-alerts` with partial results | 🔴 Immediate |
| **Production deploy failed** | `#eng-alerts` + rollback | 🔴 Immediate |
| **Verification keeps failing** | `#eng-deploys` with diff | 🟡 Within 30 min |
| **Agent produced wrong output (non-secrets)** | `#eng-deploys` with details | 🟡 Within 1 hour |
| **Subagent allocation unclear** | Ask Hermes to clarify (no escalation) | 🟢 Next cycle |

### Escalation Template

```
Channel: #eng-alerts
Priority: [CRITICAL | HIGH | MEDIUM]
Task: GRO-XX
Agent: [jules | agy | codex | hermes]
Issue: [1-line description of what went wrong]
Context: [links to task intake, agent output, verification results]
Action needed: [what human should do]
```

---

## Day-One Checklist

Run through these tasks on your first day to get comfortable with the system:

### Morning: Submit One Each

- [ ] **Submit a code task** — Simple bug fix, `preferred_agent: jules`
  - Wait for PR to open (~15 min)
  - Verify with checklist steps 1–4

- [ ] **Submit a research task** — Small analysis, `preferred_agent: agy`
  - Check the deliverable at `output/research/<file>.md`
  - Verify with checklist steps 1, 2, 4, 5

- [ ] **Submit a coordination task** — Let Hermes handle multi-step
  - Use `task_type: research_coordination` with subagent allocations
  - Review the coordination summary

### Afternoon: Review the System

- [ ] **Read the full routing decision matrix** — [routing-decision-matrix](./routing-decision-matrix.md)
- [ ] **Review agent capabilities** — [lane-capabilities](./lane-capabilities.md)
- [ ] **Understand handoff formats** — [handoff-contracts](./handoff-contracts.md)
- [ ] **Check the pilot report** — [router-pilot-report](./router-pilot-report.md) (see what worked)

### End of Day: Verify Everything

- [ ] All tasks that were submitted have completed or escalated
- [ ] No orphaned branches on GitHub
- [ ] Verification results are documented per task
- [ ] Any failed tasks have clear next steps

---

## Common Pitfalls & Solutions

### "My task is stuck — the agent isn't picking it up"

1. Check Linear: is the task in "Todo" or "In Progress" with the right label?
2. Wait 15 minutes (the cron cycle). Check session tracker at `/tmp/jules-session-tracker.json`.
3. If stuck >30 min, escalate to `#eng-alerts`.

### "The agent produced the wrong thing"

1. Check if `goal` was specific enough. "Fix the thing" routes poorly.
2. Re-submit with a clearer goal and `verification_criteria`.
3. If the right agent wasn't chosen, set `preferred_agent`.

### "Verification keeps failing on syntax_valid"

1. Check the file extension — atypical formats may not parse.
2. If the output is prose-only `.txt`, waive syntax check.
3. If the output is valid but the checker disagrees, escalate with a sample.

### "Jules won't open a PR"

1. Check the target repo's CI — `main` must be green.
2. Verify the repo is accessible via `jules remote list --repo`.
3. Check Jules session capacity — at 300/day, new sessions queue.

### "AGY is taking too long"

1. Check if `bounded_scope` had a `stop_after` limit set.
2. Reduce `max_sessions` to 1 (fewer parallel sessions = faster individual completion).
3. If AGY exceeded `stop_after`, check partial results — they may still be useful.

---

## Quick Reference Card

### Templates (copy-paste)

| Template | Purpose | File |
|---|---|---|
| Task submission | Every task starts here | [task-intake-template](./task-intake-template.md) |
| Jules code prompt | Delegate code work | [jules-prompt-template](./jules-prompt-template.md) |
| AGY research prompt | Delegate research | [agy-prompt-template](./agy-prompt-template.md) |
| Hermes coordination prompt | Delegate orchestration | [hermes-prompt-template](./hermes-prompt-template.md) |

### Decision Tools

| Tool | Purpose | File |
|---|---|---|
| Which agent for what? | Routing logic | [routing-decision-matrix](./routing-decision-matrix.md) |
| What can each agent do? | Capability inventory | [lane-capabilities](./lane-capabilities.md) |
| Is the output good? | Verification | [verification-checklist](./verification-checklist.md) |
| What format should output be? | Handoff contracts | [handoff-contracts](./handoff-contracts.md) |

---

## Cross-References

- Full architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
- Pilot results: [router-pilot-report](./router-pilot-report.md)
- Rule refinements: [routing-refinements](./routing-refinements.md)
