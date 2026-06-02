# Handoff Contracts — Agent Output Formats (GRO-84)

Exact output format each agent lane must return when completing a task. The orchestrator
uses these contracts to parse, verify, and chain agent outputs.

---

## Jules — Code Implementation Handoff

When Jules completes a code task, it must return this exact structure:

```yaml
# Jules Handoff Contract
# REQUIRED: All fields must be present.
# The orchestrator parses this to verify and chain.

agent: jules
status: completed | failed | partial
task_id: "<GRO-XX or Linear issue key>"
timestamp: "<ISO-8601>"

deliverables:
  pr_url: "<https://github.com/owner/repo/pull/N>"
  branch_name: "<type/description or gro-XX/description>"
  base_branch: "<main | staging | release/...>"
  commit_sha: "<full 40-char SHA>"

test_results:
  passed: true | false
  total: <number>
  failed: <number>
  skipped: <number>
  coverage_pct: <number>  # if available

files_changed:
  created:
    - "<path/relative/to/repo>"
  modified:
    - "<path/relative/to/repo>"
  deleted:
    - "<path/relative/to/repo>"

notes: >
  # Optional — any context the orchestrator needs.
  # Examples: known limitations, follow-up tasks, dependencies.
```

### Example (Success)

```yaml
agent: jules
status: completed
task_id: "GRO-100"
timestamp: "2026-05-29T18:30:00Z"

deliverables:
  pr_url: "https://github.com/mbgulden/hd-platform/pull/42"
  branch_name: "feat/weekly-podcast-automation"
  base_branch: "main"
  commit_sha: "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"

test_results:
  passed: true
  total: 15
  failed: 0
  skipped: 0
  coverage_pct: 87

files_changed:
  created:
    - "scripts/generate-podcast.sh"
    - "scripts/__tests__/generate-podcast.test.sh"
    - "hd-content/podcasts/2026-05-29-episode.md"
  modified: []
  deleted: []

notes: >
  Script tested on Ubuntu 24.04. Requires `ffmpeg` and `jq` installed.
  Follow-up: GRO-101 (add RSS feed generation).
```

### Example (Failed)

```yaml
agent: jules
status: failed
task_id: "GRO-102"
timestamp: "2026-05-29T19:00:00Z"

deliverables:
  pr_url: ""  # No PR opened
  branch_name: "fix/broken-payment-flow"
  base_branch: "main"
  commit_sha: ""

test_results:
  passed: false
  total: 8
  failed: 3
  skipped: 0
  coverage_pct: 0

files_changed:
  created: []
  modified:
    - "src/api/payment.ts"
  deleted: []

notes: >
  3 tests failing in payment flow. Stack traces attached.
  Issue: Stripe webhook signature verification fails in test env.
  Needs human: configure Stripe test webhook secret in CI.
```

---

## AGY — Research Handoff

When AGY completes a research task, it must return this exact structure:

```yaml
# AGY Handoff Contract
# REQUIRED: All fields must be present.

agent: agy
status: completed | partial | timed_out | failed
task_id: "<GRO-XX or task identifier>"
timestamp: "<ISO-8601>"

deliverables:
  primary_document: "<absolute path to deliverable>"
  format: "markdown_report | spreadsheet | json_data | prose_summary"
  file_size_bytes: <number>
  sessions_used: <number>  # How many sub-sessions AGY spawned

key_findings:
  # REQUIRED: 3-10 bullet points summarizing the most important discoveries.
  # The orchestrator uses these for quick assessment without reading the full doc.
  - "<finding 1>"
  - "<finding 2>"
  - "<finding 3>"

source_references:
  # REQUIRED: Every external source cited in the research.
  # Format: type: URL or file path
  - "web: https://competitor.com/pricing"
  - "drive: https://drive.google.com/file/d/abc123"
  - "file: data/research/q1-baseline.json"

scope_adherence:
  # How well did the research stay within bounds?
  in_scope_covered: "full | partial | minimal"
  out_of_scope_breaches: <number>
  breach_details:
    # If breaches > 0, list each one.
    # - "Included free tier analysis (out_of_scope)"

time_stats:
  wall_clock_minutes: <number>
  exceeded_stop_after: true | false

notes: >
  # Optional — context for the orchestrator.
```

### Example (Complete)

```yaml
agent: agy
status: completed
task_id: "GRO-77"
timestamp: "2026-05-29T16:45:00Z"

deliverables:
  primary_document: "/home/ubuntu/work/hd-platform/output/research/q2-competitor-pricing.md"
  format: "markdown_report"
  file_size_bytes: 28450
  sessions_used: 3

key_findings:
  - "All 3 competitors (NexusCloud, DataForge, Streamline) raised Pro tier prices 15-22% in Q2"
  - "DataForge added SSO and audit logs to their Pro tier (we don't offer either)"
  - "Streamline introduced a generous free tier with 80% of Pro features — biggest competitive threat"
  - "Our Enterprise tier is priced 30% below market median — opportunity to raise"
  - "2x2 matrix shows we're in the 'low price, low features' quadrant — undesirable position"

source_references:
  - "web: https://nexuscloud.com/pricing"
  - "web: https://dataforge.io/pricing"
  - "web: https://streamline.dev/pricing"
  - "drive: https://drive.google.com/file/d/abc123"
  - "file: data/research/q1-pricing-baseline.csv"

scope_adherence:
  in_scope_covered: "full"
  out_of_scope_breaches: 1
  breach_details:
    - "Briefly analyzed Streamline's free tier features (out_of_scope) — included because it's strategically relevant"

time_stats:
  wall_clock_minutes: 47
  exceeded_stop_after: false

notes: >
  Competitor data was from public pages only. No authenticated scraping.
  Recommendations section is board-ready. Include financial impact estimates
  before presenting to board.
```

---

## Codex — Code Review Handoff

When Codex completes a review, it must return this exact structure:

```yaml
# Codex Review Handoff Contract
# REQUIRED: All fields must be present.

agent: codex
status: completed | partial | failed
task_id: "<GRO-XX or PR number>"
timestamp: "<ISO-8601>"

review_target:
  pr_url: "<https://github.com/owner/repo/pull/N>"
  branch: "<branch name>"
  base_branch: "<main | staging | ...>"

verdict: "approved | changes_requested | blocked"

severity_counts:
  critical: <number>   # Must fix before merge — security, data loss, auth bypass
  high: <number>       # Should fix — logic errors, performance, reliability
  medium: <number>     # Nice to fix — style, patterns, maintainability
  low: <number>        # Optional — nits, suggestions
  info: <number>       # Observations, praise, proactive suggestions

findings:
  # If verdict is not "approved", list each finding with severity.
  # - severity: critical
  #   file: "src/api/payment.ts"
  #   line: 47
  #   finding: "Missing Stripe signature verification — payment webhook is unauthenticated"
  #   recommendation: "Add stripe.webhooks.constructEvent() call with webhook secret"

review_report_path: "<absolute path to review report file>"
  # Codex writes a detailed review report to this path.

recommendations:
  # Top 3-5 actionable items.
  - "<recommendation 1>"
  - "<recommendation 2>"

notes: >
  # Optional — context for Hermes.
```

### Example (Changes Requested)

```yaml
agent: codex
status: completed
task_id: "PR #42"
timestamp: "2026-05-29T19:15:00Z"

review_target:
  pr_url: "https://github.com/mbgulden/hd-platform/pull/42"
  branch: "feat/weekly-podcast-automation"
  base_branch: "main"

verdict: "changes_requested"

severity_counts:
  critical: 0
  high: 2
  medium: 3
  low: 1
  info: 2

findings:
  - severity: high
    file: "scripts/generate-podcast.sh"
    line: 23
    finding: "Hardcoded API key path ~/.config/hd-platform/api.key — will break in CI"
    recommendation: "Use $API_KEY env var with fallback to file path"
  - severity: high
    file: "scripts/generate-podcast.sh"
    line: 45
    finding: "No error handling on ffmpeg call — script continues silently on failure"
    recommendation: "Add `set -e` at top and check ffmpeg exit code"

review_report_path: "/home/ubuntu/work/hd-platform/output/reviews/PR-42-codex-review.md"

recommendations:
  - "Fix the two HIGH severity issues before merge"
  - "Add `set -euo pipefail` for strict error handling"
  - "Consider adding a --dry-run flag for testing"
```

---

## Hermes — Orchestration Handoff

When Hermes completes an orchestration task, it must return this exact structure:

```yaml
# Hermes Orchestration Handoff Contract
# REQUIRED: All fields must be present.

agent: hermes
status: completed | partial | failed | escalated
task_id: "<GRO-XX or incident ID>"
timestamp: "<ISO-8601>"

task_type: "research_coordination | deployment_supervision | multi_agent_validation | code_review_coordination | incident_response"

subagent_results:
  # Results from each delegated agent.
  # Key: agent name, Value: summary of handoff.
  jules:
    dispatched: true | false
    status: "completed | failed | timed_out"
    handoff_summary: "<1-line summary from Jules handoff.notes>"
  agy:
    dispatched: true | false
    status: "completed | failed | timed_out"
    handoff_summary: "<1-line summary from AGY handoff.notes>"
  codex:
    dispatched: true | false
    status: "completed | failed | timed_out"
    handoff_summary: "<1-line summary from Codex handoff.notes>"

verified_artifacts:
  # Every output file or URL produced, with verification status.
  - path: "<absolute path or URL>"
    type: "file | pr | report | deploy_log"
    verification: "pass | fail | waived"
    check_summary: "<e.g., 'file_exists: pass, secrets_clean: pass, syntax_valid: pass'>"

verification_result:
  overall: "pass | fail"
  checks_passed: <number>
  checks_failed: <number>
  checks_waived: <number>
  failures:
    # If any check failed.
    # - check: "secrets_clean"
    #   details: "..."

coordination_summary: >
  # REQUIRED: 3-5 sentence narrative of what happened.
  # What was dispatched, what succeeded, what failed, what needs human attention.

escalation_triggered: true | false
escalation_details: >
  # If escalation triggered, what happened.
  # e.g., "Slack #eng-alerts notified at 18:45 — subagent AGY timed out after 47 min"

notes: >
  # Optional — recommendations, follow-ups, patterns observed.
```

### Example (Research + Implementation Coordination)

```yaml
agent: hermes
status: completed
task_id: "GRO-87"
timestamp: "2026-05-29T20:00:00Z"

task_type: "research_coordination"

subagent_results:
  agy:
    dispatched: true
    status: "completed"
    handoff_summary: "Competitor pricing analysis complete — 3 competitors analyzed, 5 key findings"
  jules:
    dispatched: true
    status: "completed"
    handoff_summary: "PR #43 opened: pricing page updates based on AGY recommendations"
  codex:
    dispatched: false
    status: "not_dispatched"
    handoff_summary: ""

verified_artifacts:
  - path: "/home/ubuntu/work/hd-platform/output/research/q2-competitor-pricing.md"
    type: "file"
    verification: "pass"
    check_summary: "file_exists: pass, syntax_valid: pass, secrets_clean: pass"
  - path: "https://github.com/mbgulden/hd-platform/pull/43"
    type: "pr"
    verification: "pass"
    check_summary: "PR accessible, CI green, tests pass"

verification_result:
  overall: "pass"
  checks_passed: 6
  checks_failed: 0
  checks_waived: 0
  failures: []

coordination_summary: >
  AGY analyzed Q2 2026 competitor pricing across 3 SaaS competitors in 47 minutes,
  producing a 28KB markdown report with 5 key findings and specific pricing 
  recommendations. Jules then implemented the recommended pricing page updates 
  in PR #43 with 15 passing tests and 87% coverage. Codex review was not dispatched
  because the PR is a content change (marketing copy), not code logic. All artifacts
  passed verification. No escalation needed.

escalation_triggered: false
escalation_details: ""

notes: >
  AGY's minor scope breach (free tier analysis) was strategically valuable — keep.
  Jules PR #43 should get a quick human sanity check on pricing copy before merge.
  Recommend running Codex on the PR anyway — it flagged useful style issues last time.
```

---

## Contract Enforcement

The orchestrator enforces these contracts at two points:

### 1. On Agent Completion
```python
# Pseudo-code for contract validation
def validate_handoff(handoff: dict, agent: str) -> bool:
    required_fields = HANDOFF_SCHEMAS[agent]["required"]
    for field in required_fields:
        if field not in handoff or handoff[field] is None:
            return False  # REJECT: incomplete handoff
    return True
```

### 2. During Verification
The [verification checklist](./verification-checklist.md) cross-references handoff fields:
- `deliverables.primary_document` / `pr_url` → `file_exists` check
- `test_results.passed` → `tests_pass` check
- All file paths → `secrets_clean` check
- `key_findings` / `findings` → `matches_spec` check

---

## Schema Reference

| Field Group | Jules | AGY | Codex | Hermes |
|---|---|---|---|---|
| **Identity** | agent, status, task_id, timestamp | Same | Same | Same |
| **Deliverables** | pr_url, branch_name, commit_sha | primary_document, format | pr_url, review_report_path | verified_artifacts |
| **Test/Quality** | test_results | — | severity_counts, verdict | verification_result |
| **Research** | — | key_findings, source_references, scope_adherence | — | coordination_summary |
| **Findings** | notes | notes | findings, recommendations | subagent_results |
| **Timing** | — | time_stats | — | escalation_triggered |

---

## Cross-References

- Submit tasks: [task-intake-template](./task-intake-template.md)
- Route to agents: [routing-decision-matrix](./routing-decision-matrix.md)
- Verify handoffs: [verification-checklist](./verification-checklist.md)
- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
- See handoffs in action: [router-pilot-report](./router-pilot-report.md)
