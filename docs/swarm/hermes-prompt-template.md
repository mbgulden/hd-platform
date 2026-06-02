# Hermes Orchestrator Prompt Template (GRO-81)

Use this template when delegating orchestration tasks to Hermes — research coordination,
multi-agent validation, deployment supervision, or any task that requires managing other
agents rather than doing the work directly.

---

## Template

```yaml
# ── Hermes Orchestrator Prompt ──────────────────────────────
# Copy this block, fill in the blanks, and pass to Hermes.

task_type: ""
  # [REQUIRED] The category of orchestration work.
  # Options:
  #   research_coordination  — Delegate to AGY/Jules, synthesize results
  #   deployment_supervision — Watch a deploy, run health checks, rollback if needed
  #   multi_agent_validation  — Run multiple agents against the same problem, compare
  #   code_review_coordination — Delegate review to Codex, aggregate feedback
  #   incident_response       — Triage, delegate fixes, verify resolution

inputs:
  # [REQUIRED] What Hermes has to work with.
  # List files, URLs, issue keys, or raw data.
  # Example:
  #   - "task-intake: docs/swarm/task-intake-template.md"
  #   - "PR URL: https://github.com/nous-research/repo/pull/412"
  #   - "Deploy log: s3://logs/deploy-2026-05-29.json"
  #   - "Incident ticket: INC-47"

expected_outputs:
  # [REQUIRED] What Hermes must produce.
  # Be concrete — file paths, data shapes, or observable outcomes.
  # Example:
  #   - "PR merged to main with all checks green"
  #   - "Deploy complete, health check passing for 10 minutes"
  #   - "Research report at output/research/<slug>.md"
  #   - "Incident postmortem at docs/incidents/INC-47.md"

success_criteria:
  # [REQUIRED] How Hermes knows it's done AND correct.
  # These get fed into the verification checklist.
  # Example:
  #   - "All delegated sub-tasks returned exit code 0"
  #   - "PR CI pipeline is green"
  #   - "Canary traffic shows <0.1% error rate for 5 min"
  #   - "Postmortem reviewed and approved by eng lead"

escalation_path:
  # [REQUIRED] What to do if something goes wrong.
  # Define thresholds and actions.
  # Example:
  #   on_subagent_failure:
  #     retry: 2
  #     then: "escalate to human via Slack #eng-alerts"
  #   on_verification_failure:
  #     retry: 1
  #     then: "rollback and escalate"
  #   on_timeout:
  #     action: "escalate immediately"

subagent_allocations:
  # [OPTIONAL] Explicitly assign sub-tasks to specific agents.
  # If empty, Hermes decides based on task type and agent profiles.
  # Example:
  #   - agent: jules
  #     task: "Implement the contact form fix"
  #     prompt_ref: "docs/swarm/jules-prompt-template.md"
  #   - agent: agy
  #     task: "Research competitor contact form UX patterns"
  #     prompt_ref: "docs/swarm/agy-prompt-template.md"

timeout_minutes: 30
  # [OPTIONAL] Maximum wall-clock time for the entire orchestration.
  # Default: 30. Range: 5–120.
  # Hermes will escalate via escalation_path if this is exceeded.

parallel: false
  # [OPTIONAL] Whether sub-tasks can run in parallel.
  # true  = all subagent_allocations dispatched simultaneously
  # false = sequential (use when tasks depend on each other)
  # Default: false
```

---

## Field Reference

| Field | Required | Purpose |
|-------|----------|---------|
| `task_type` | **Yes** | Determines Hermes's operating mode and agent selection logic |
| `inputs` | **Yes** | All artifacts, URLs, and data Hermes needs to coordinate |
| `expected_outputs` | **Yes** | Concrete deliverables or observable outcomes |
| `success_criteria` | **Yes** | Machine-checkable gates that feed verification |
| `escalation_path` | **Yes** | Failure handling — retry counts, escalation channels |
| `subagent_allocations` | Optional | Pre-assign work to specific agents instead of auto-routing |
| `timeout_minutes` | Optional | Hard wall-clock stop; default 30 |
| `parallel` | Optional | Parallel vs. sequential sub-task dispatch |

---

## Examples

### Deployment Supervision

```yaml
task_type: deployment_supervision

inputs:
  - "Deploy artifact: v2.4.1 (Docker image: registry.nous.co/web:v2.4.1)"
  - "Target: k8s/production namespace"
  - "Rollback artifact: v2.4.0 (Docker image: registry.nous.co/web:v2.4.0)"
  - "Runbook: docs/runbooks/deploy-web.md"

expected_outputs:
  - "v2.4.1 running on all production pods"
  - "Deploy log at logs/deploy-2026-05-29-1800.txt"

success_criteria:
  - "All pods report Ready status within 120s of deploy trigger"
  - "Health check /healthz returns 200 on all pods"
  - "P99 latency < 200ms for 10 consecutive minutes"
  - "Error rate < 0.1% for 10 consecutive minutes"
  - "No alerts fired in #eng-alerts related to this deploy"

escalation_path:
  on_health_check_failure:
    retry: 2
    wait_between_retries: "30s"
    then: "rollback to v2.4.0 and escalate to Slack #eng-alerts"
  on_latency_spike:
    retry: 0
    then: "escalate to Slack #eng-alerts with CloudWatch dashboard link"
  on_timeout:
    action: "rollback and escalate"

timeout_minutes: 20
parallel: false
```

### Multi-Agent Research + Implementation

```yaml
task_type: research_coordination

inputs:
  - "Task intake: GRO-77 (competitor pricing analysis + pricing page update)"
  - "Competitor URLs: nexuscloud.com/pricing, dataforge.io/pricing, streamline.dev/pricing"
  - "Our pricing page: src/pages/pricing.astro"
  - "Linear: GRW-87"

expected_outputs:
  - "Research report: output/research/q2-2026-competitor-pricing.md"
  - "PR with pricing page updates (if recommended)"
  - "Orchestration summary at output/summaries/GRW-87-orchestration.md"

success_criteria:
  - "Research report covers all 3 competitors with cited data"
  - "PR (if any) has passing tests and CI green"
  - "All sub-tasks returned exit code 0"

subagent_allocations:
  - agent: agy
    task: "Analyze competitor pricing and produce recommendations"
    prompt_ref: "docs/swarm/agy-prompt-template.md"
  - agent: jules
    task: "Implement pricing page updates based on AGY recommendations"
    prompt_ref: "docs/swarm/jules-prompt-template.md"

escalation_path:
  on_subagent_failure:
    retry: 1
    then: "escalate to human with partial results"
  on_verification_failure:
    retry: 1
    then: "escalate with diff between expected and actual"
  on_timeout:
    action: "escalate with partial results"

timeout_minutes: 45
parallel: false   # Jules depends on AGY output
```

### Incident Response

```yaml
task_type: incident_response

inputs:
  - "Incident: INC-47 — Checkout flow returning 503 for 15% of users"
  - "Alert link: https://datadog.nous.co/monitors/882"
  - "Affected service: checkout-api (k8s/production)"
  - "Recent deploys: v2.4.1 deployed 45 minutes ago (suspected culprit)"

expected_outputs:
  - "Root cause identified and documented"
  - "Fix deployed (or rollback completed)"
  - "Incident postmortem draft at docs/incidents/INC-47.md"

success_criteria:
  - "503 error rate drops to <0.1%"
  - "Checkout flow completes end-to-end with test card"
  - "Postmortem includes timeline, root cause, fix, and prevention steps"

escalation_path:
  on_root_cause_unknown:
    retry: 0
    then: "escalate to on-call engineer via PagerDuty"
  on_fix_attempt_failure:
    retry: 1
    then: "rollback to v2.4.0 and escalate to on-call engineer"
  on_timeout:
    action: "escalate to on-call engineer with current findings"

timeout_minutes: 15
parallel: true    # Investigate and prepare rollback simultaneously
```

---

## Hermes Operating Modes

| task_type | Agent Selection | Parallel OK? | Typical Timeout |
|-----------|----------------|--------------|-----------------|
| `research_coordination` | AGY + optional Jules | After research | 30–60 min |
| `deployment_supervision` | Hermes only (k8s + health checks) | No | 15–20 min |
| `multi_agent_validation` | 2+ agents (same task, compare) | **Yes** | 20–40 min |
| `code_review_coordination` | Codex + optional Jules | Yes | 10–20 min |
| `incident_response` | Hermes + Jules | Yes | 10–15 min |

---

## Integration with Orchestration Router

When the router delegates to Hermes:
1. `task-intake.goal` + `context` → `task_type` is auto-classified.
2. `task-intake.verification_criteria` → `success_criteria`.
3. `task-intake.side_effects` → `escalation_path` thresholds (blast radius determines
   retry count).
4. `task-intake.deadline` → `timeout_minutes` (default 30, capped by deadline).
5. `task-intake.preferred_agent` is ignored (Hermes is the orchestrator).
6. After Hermes completes, the router runs the
   [verification checklist](./verification-checklist.md) against `expected_outputs`.
