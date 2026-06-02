# Swarm Skills Inventory (GRO-22)

Current skills loaded in the orchestrator profile, gap analysis, and priority skills to
create next. Skills are stored in `~/.hermes/profiles/orchestrator/skills/`.

---

## Current Skills

### 1. Agent Orchestration (`agent-orchestration/`)

Skills for coordinating the multi-agent swarm.

| Skill | Path | Purpose |
|-------|------|---------|
| antigravity-capability-envelope | `agent-orchestration/antigravity-capability-envelope/` | Defines AGY's capabilities, limits, and operating boundaries |
| antigravity-cli-operating-playbook | `agent-orchestration/antigravity-cli-operating-playbook/` | How to operate the `agy` CLI — launch, monitor, recover |
| antigravity-cli-orchestration | `agent-orchestration/antigravity-cli-orchestration/` | Orchestrating AGY as a subagent in multi-agent workflows |
| antigravity-cli-session-recovery | `agent-orchestration/antigravity-cli-session-recovery/` | Recovering stuck or timed-out AGY sessions |
| antigravity-research-session-synthesis | `agent-orchestration/antigravity-research-session-synthesis/` | Synthesizing results from multi-session AGY research |
| autonomous-execution-discipline | `agent-orchestration/autonomous-execution-discipline/` | Rules and boundaries for fully autonomous agent operation |
| autonomous-project-kickoff | `agent-orchestration/autonomous-project-kickoff/` | How to bootstrap a new project with agent assistance |
| expert-interview-content-production | `agent-orchestration/expert-interview-content-production/` | Pipeline for turning expert interviews into content |
| golden-thread-review | `agent-orchestration/golden-thread-review/` | Review process for strategic alignment ("golden thread") |
| jules-cli-operating-playbook | `agent-orchestration/jules-cli-operating-playbook/` | How to operate the `jules` CLI — launch, configure, monitor |
| jules-parallel-session-orchestration | `agent-orchestration/jules-parallel-session-orchestration/` | Running multiple Jules sessions concurrently |
| orchestrator-delegation-discipline | `agent-orchestration/orchestrator-delegation-discipline/` | How Hermes delegates to subagents safely |
| project-repository-bootstrap | `agent-orchestration/project-repository-bootstrap/` | Scaffolding new repos with standards, CI, README |
| unified-agent-conversation-pipeline | `agent-orchestration/unified-agent-conversation-pipeline/` | Multi-agent conversation routing and handoff pipeline |

### 2. Content Strategy (`content-strategy/`)

| Skill | Path | Purpose |
|-------|------|---------|
| expert-interview-content-pipeline | `content-strategy/expert-interview-content-pipeline/` | End-to-end content production from expert interviews |

### 3. Content (`content/`)

| Skill | Path | Purpose |
|-------|------|---------|
| expert-interview-content-strategy | `content/expert-interview-content-strategy/` | Strategy layer for expert interview content |

### 4. Engineering (`engineering/`)

| Skill | Path | Purpose |
|-------|------|---------|
| credential-security-and-git-hygiene | `engineering/credential-security-and-git-hygiene/` | Git hygiene, credential scanning, orphan branch cleanup |
| human-design-mcp-development | `engineering/human-design-mcp-development/` | Core HD MCP server development with corrected math |
| open-source-launch-checklist | `engineering/open-source-launch-checklist/` | Checklist for launching open-source projects |
| open-source-project-launch | `engineering/open-source-project-launch/` | Full project launch workflow |
| project-branding-and-naming | `engineering/project-branding-and-naming/` | Branding constraints, naming conventions, domain setup |

### 5. Golden Thread Templates (`golden-thread-templates/`)

Strategic alignment templates that connect venture priorities to daily work.

| Skill | Path | Purpose |
|-------|------|---------|
| golden-thread-templates | `golden-thread-templates/SKILL.md` | Template format for golden thread alignment documents |

### 6. HD Relationship Report (`hd-relationship-report/`)

| Skill | Path | Purpose |
|-------|------|---------|
| hd-relationship-report | `hd-relationship-report/SKILL.md` | HD relationship report generation with batch generation recipes |

### 7. Hermes Agent (`hermes-agent/`)

Skills for Hermes Agent self-management.

| Skill | Path | Purpose |
|-------|------|---------|
| hermes-agent-profiles-and-swarms | `hermes-agent/hermes-agent-profiles-and-swarms/` | Profile management, swarm configuration, gateway setup |
| hermes-daily-memory-journal | `hermes-agent/hermes-daily-memory-journal/` | Daily memory persistence and journaling |
| hermes-dashboard-extensions | `hermes-agent/hermes-dashboard-extensions/` | Dashboard and monitoring extensions |

### 8. Human Design (`human-design/`)

| Skill | Path | Purpose |
|-------|------|---------|
| hd-birth-data-registry | `human-design/hd-birth-data-registry/` | Birth data storage and management |
| hd-individual-deep-dive | `human-design/hd-individual-deep-dive/` | Deep individual HD chart analysis |
| human-design-computation | `human-design/human-design-computation/` | Core HD computation logic and ephemeris handling |

### 9. Infrastructure (`infrastructure/`)

| Skill | Path | Purpose |
|-------|------|---------|
| agy-vision-pipeline | `infrastructure/agy-vision-pipeline/` | Vision/image processing pipeline for AGY |
| cloudflare-deployment | `infrastructure/cloudflare-deployment/` | Cloudflare Pages/Tunnel deployment |
| homelab-inventory-management | `infrastructure/homelab-inventory-management/` | Local homelab hardware inventory |
| human-design-computation-engine | `infrastructure/human-design-computation-engine/` | HD computation engine deployment |
| kubernetes-gpu-llm-serving | `infrastructure/kubernetes-gpu-llm-serving/` | K8s GPU cluster for LLM serving |
| offline-mcp-server-building | `infrastructure/offline-mcp-server-building/` | Building MCP servers for offline use |
| open-source-project-prep | `infrastructure/open-source-project-prep/` | Preparing projects for open-source release |
| secrets-hygiene | `infrastructure/secrets-hygiene/` | Secret management and rotation |

### 10. Local GPU Watchdog (`local-gpu-watchdog-and-remediation/`)

| Skill | Path | Purpose |
|-------|------|---------|
| local-gpu-watchdog-and-remediation | `local-gpu-watchdog-and-remediation/SKILL.md` | GPU health monitoring and automatic remediation |

### 11. Next Step Bot (`next-step-bot/`)

| Skill | Path | Purpose |
|-------|------|---------|
| next-step-bot | `next-step-bot/SKILL.md` | Telegram bot for task progression tracking |

### 12. Orchestration (`orchestration/`)

| Skill | Path | Purpose |
|-------|------|---------|
| golden-thread | `orchestration/golden-thread/` | Strategic alignment orchestration with venture directives |

### 13. Unrestricted Execution Protocol (`unrestricted-execution-protocol/`)

| Skill | Path | Purpose |
|-------|------|---------|
| unrestricted-execution-protocol | `unrestricted-execution-protocol/SKILL.md` | Protocol for high-trust autonomous execution |

---

## Skill Count Summary

| Category | Skill Count |
|----------|------------|
| Agent Orchestration | 14 |
| Content Strategy | 1 |
| Content | 1 |
| Engineering | 5 |
| Golden Thread Templates | 1 |
| HD Relationship Report | 1 |
| Hermes Agent | 3 |
| Human Design | 3 |
| Infrastructure | 8 |
| Local GPU Watchdog | 1 |
| Next Step Bot | 1 |
| Orchestration | 1 |
| Unrestricted Execution | 1 |
| **Total** | **41** |

---

## Gap Analysis

### Gap 1: Missing — Codex Operating Playbook 🔴 HIGH

**What's missing:** No skill for operating ChatGPT 5.5 (Codex) as a review agent. Jules
and AGY have operating playbooks; Codex does not.

**Impact:** Orchestrator doesn't know how to dispatch reviews programmatically. Reviews
are manual or informal.

**What's needed:**
- `codex-cli-operating-playbook` — Launch, configure, monitor Codex review sessions
- `codex-review-dispatch-automation` — Auto-dispatch reviews from Linear labels
- `codex-security-audit-protocol` — Standard security audit procedure

### Gap 2: Missing — Linear Integration Deep-Dive 🔴 HIGH

**What's missing:** While Linear labels are referenced throughout docs, there's no skill
for the full Linear → agent dispatch pipeline.

**Impact:** Manual steps remain; full automation not achieved.

**What's needed:**
- `linear-agent-dispatch-automation` — Full auto-dispatch from Linear to agents
- `linear-label-taxonomy` — Standard label set and routing rules
- `linear-webhook-handler` — Webhook-based dispatch (replacing cron polling)

### Gap 3: Missing — Verification Automation 🔴 HIGH

**What's missing:** Verification checklist is documented but not automated as a skill.
Manual verification steps required for every task.

**Impact:** Throughput bottleneck. Human must verify every agent output.

**What's needed:**
- `automated-verification-pipeline` — Auto-run all 6 verification checks
- `verification-reporting` — Automated pass/fail reporting per task
- `secrets-scan-automation` — Automatic credential leak detection

### Gap 4: Missing — PR Auto-Merger Configuration 🟡 MEDIUM

**What's missing:** PR auto-merger is referenced but no skill defines its configuration
or operating parameters.

**Impact:** Merge behavior may be inconsistent.

**What's needed:**
- `pr-auto-merger-configuration` — Rules for when to auto-merge vs. wait
- `merge-conflict-resolution` — Automated conflict resolution strategies

### Gap 5: Missing — Agent Performance Metrics 🟡 MEDIUM

**What's missing:** No skill for tracking or reporting agent performance metrics.

**Impact:** Can't measure throughput, success rates, or identify bottlenecks.

**What's needed:**
- `agent-performance-dashboard` — Metrics collection and dashboard
- `throughput-reporting` — Daily/weekly throughput reports
- `cost-tracking` — Per-agent cost tracking and optimization

### Gap 6: Missing — Escalation Automation 🟡 MEDIUM

**What's missing:** Escalation paths are documented but not automated as skills.

**Impact:** Escalations require manual detection and action.

**What's needed:**
- `auto-escalation-protocol` — Automatic detection and escalation of failure conditions
- `slack-alert-integration` — Programmatic Slack alerting from agent failures
- `incident-response-playbook` — Automated incident response workflow

### Gap 7: Missing — Cross-Agent Context Sharing 🟢 LOW

**What's missing:** AGY research results don't automatically feed into Jules context.

**Impact:** Jules may start from scratch when prior research exists.

**What's needed:**
- `cross-agent-context-bridge` — Share research context between AGY and Jules
- `research-to-implementation-handoff` — Structured handoff from research to code

### Gap 8: Missing — Branch Discipline Automation 🟢 LOW

**What's missing:** Branch discipline is a script, not a skill. No agent-level
enforcement.

**Impact:** Agents could theoretically work on `main` if the script isn't called.

**What's needed:**
- `branch-discipline-enforcement` — Automatic branch creation before any write
- `branch-cleanup-automation` — Stale branch detection and cleanup

### Gap 9: Missing — Testing Workflow Integration 🟢 LOW

**What's missing:** No skill for standardizing test expectations across agents.

**Impact:** Inconsistent test quality across Jules sessions.

**What's needed:**
- `test-standards-enforcement` — Minimum test coverage, test patterns
- `test-generation-templates` — Standard test templates per language

---

## Priority Skills to Create Next

### Immediate (This Sprint)

| # | Skill | Solves | Effort |
|---|-------|--------|--------|
| 1 | `codex-cli-operating-playbook` | Gap 1 — Codex review automation | 2h |
| 2 | `linear-agent-dispatch-automation` | Gap 2 — Full Linear automation | 3h |
| 3 | `automated-verification-pipeline` | Gap 3 — Remove manual verification | 3h |

### Short-Term (Next Week)

| # | Skill | Solves | Effort |
|---|-------|--------|--------|
| 4 | `pr-auto-merger-configuration` | Gap 4 — Consistent merge behavior | 1h |
| 5 | `agent-performance-dashboard` | Gap 5 — Throughput visibility | 3h |
| 6 | `auto-escalation-protocol` | Gap 6 — Automatic failure escalation | 2h |
| 7 | `slack-alert-integration` | Gap 6 — Programmatic Slack alerts | 1h |

### Medium-Term (Within 2 Weeks)

| # | Skill | Solves | Effort |
|---|-------|--------|--------|
| 8 | `cross-agent-context-bridge` | Gap 7 — Research → code context sharing | 2h |
| 9 | `branch-discipline-enforcement` | Gap 8 — Automatic branch creation | 1h |
| 10 | `cost-tracking` | Gap 5 — Cost optimization | 2h |
| 11 | `throughput-reporting` | Gap 5 — Daily/weekly reports | 1h |
| 12 | `test-standards-enforcement` | Gap 9 — Consistent test quality | 1h |

### Backlog (Future)

| # | Skill | Solves |
|---|-------|--------|
| 13 | `codex-security-audit-protocol` | Standard security audit procedure |
| 14 | `codex-review-dispatch-automation` | Auto-dispatch reviews from Linear |
| 15 | `linear-webhook-handler` | Webhook-based dispatch |
| 16 | `linear-label-taxonomy` | Standard label set documentation |
| 17 | `verification-reporting` | Automated reporting |
| 18 | `secrets-scan-automation` | Automatic credential leak detection |
| 19 | `merge-conflict-resolution` | Automated conflict resolution |
| 20 | `incident-response-playbook` | Automated incident response |
| 21 | `research-to-implementation-handoff` | Structured research→code handoff |
| 22 | `branch-cleanup-automation` | Stale branch detection/cleanup |
| 23 | `test-generation-templates` | Standard test templates |

---

## Skill Health Assessment

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Agent coverage** | 🟡 Partial | Jules, AGY, Hermes have playbooks. Codex missing. |
| **Automation depth** | 🟡 Partial | Routing, dispatch partially automated. Verification manual. |
| **Operational maturity** | 🟡 Partial | Good docs, missing automated enforcement. |
| **Cross-agent integration** | 🔴 Immature | No context sharing between agents. |
| **Monitoring/observability** | 🔴 Missing | No metrics, no dashboards, no cost tracking. |
| **Incident response** | 🔴 Manual | Escalation paths defined but not automated. |

---

## Skill Usage Metrics

Based on `.usage.json` tracking, approximate usage by category:

| Category | Usage (est.) | Notes |
|----------|-------------|-------|
| Agent Orchestration | High | Heavily used for swarm coordination |
| Infrastructure | High | Deployment and GPU serving are active |
| Hermes Agent | High | Self-management skills used daily |
| Human Design | Medium | Used when HD features are in focus |
| Engineering | Medium | Used for repo setup and code standards |
| Content / Content Strategy | Low | Used periodically for content production |
| Golden Thread Templates | Low | Strategic alignment — periodic review |
| GPU Watchdog | Background | Runs continuously as daemon |

---

## Cross-References

- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
- Routing taxonomy: [agent-routing-taxonomy](./agent-routing-taxonomy.md)
- Jules evaluation: [jules-cli-evaluation](./jules-cli-evaluation.md)
- Verification: [verification-checklist](./verification-checklist.md)
- Repo mapping: [repo-mapping-policy](./repo-mapping-policy.md)
- Architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
