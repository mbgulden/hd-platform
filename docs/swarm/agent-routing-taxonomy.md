# Agent Routing Taxonomy (GRO-16)

Complete classification of task types, which agent owns each, escalation paths, output
expectations, and Linear label bindings. This is the canonical routing reference — if a
task type isn't listed here, it defaults to Hermes for triage.

---

## Task Type Catalog

### CODE — Implementation & Refactoring

**Owner: Jules** (sole owner)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Bug fix | "Fix 500 error on POST /api/contact" | `agent:jules` |
| Feature implementation | "Add newsletter signup component" | `agent:jules` |
| Refactoring | "Extract payment logic into shared module" | `agent:jules` |
| Dependency update | "Upgrade React to 19.x" | `agent:jules` |
| Test writing | "Add integration tests for checkout flow" | `agent:jules` |
| Documentation (code) | "Add JSDoc to API handlers" | `agent:jules` |
| Configuration | "Update CI pipeline for Node 22" | `agent:jules` |
| Scaffolding | "Initialize new microservice repo" | `agent:jules` |

**File signatures that trigger CODE routing:** `.ts`, `.tsx`, `.py`, `.astro`, `.yaml`,
`.json`, `.js`, `.jsx`, `.css`, `.html`, `.toml`, `.toml`, `.dockerfile`, `.sh`

**Output expectations:**
- PR opened against target branch
- Tests pass (or `tests_required: false` explicitly set)
- Conventional commit message
- Branch name follows `gro-XX/description` or `type/description`
- Jules handoff contract returned (see [handoff-contracts](./handoff-contracts.md))

**Ownership rule:** Jules is the **sole owner** of CODE tasks. No other agent may open PRs.
Hermes may write/patch files directly in exceptional cases (Jules at capacity), but Jules
must review that work afterward.

**Escalation path:**
1. Jules attempts → if CI fails, Jules retries up to 2×
2. If Jules fails 3× → auto-escalate to **Hermes** for triage
3. If Hermes can't resolve → escalates to **Michael** via Slack `#eng-alerts`

**Pre-flight checks (enforced by router):**
- Repo `main` CI is green
- Repo accessible via `jules remote list --repo`
- Package lockfile exists and is recent (<24h old)

---

### RESEARCH — Analysis & Synthesis

**Owner: AGY** (primary), Hermes (coordinator/fallback)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Competitor analysis | "Analyze Q2 competitor pricing" | `agent:agy` |
| SEO audit | "Audit blog SEO performance" | `agent:agy` |
| Document analysis | "Cross-reference 3 Google Docs for inconsistencies" | `agent:agy` |
| Market research | "Research HD practitioner tooling landscape" | `agent:agy` |
| Content audit | "Audit website for broken links and outdated copy" | `agent:agy` |
| Drive extraction | "Extract and analyze Google Takeout archive" | `agent:agy` |
| Web scraping | "Scrape competitor feature lists" | `agent:agy` |
| Vision analysis | "Analyze screenshots of competitor dashboards" | `agent:agy` |

**Output expectations:**
- Primary document at declared `deliverable_path`
- Key findings (3–10 bullet points)
- Source references for every external citation
- Scope adherence report
- AGY handoff contract returned (see [handoff-contracts](./handoff-contracts.md))

**Ownership rule:** AGY is the **primary owner** of RESEARCH tasks. Hermes coordinates
multi-phase research (AGY → Jules → Codex pipeline). If AGY is unavailable, Hermes may
perform bounded research directly.

**Escalation path:**
1. AGY attempts within `stop_after` wall-clock limit
2. If AGY times out → partial results accepted; Hermes reviews
3. If partial results insufficient → Hermes dispatches follow-up AGY session
4. If follow-up also fails → escalates to **Michael** via Slack `#eng-alerts`

**Scope guard:** AGY must stay within `out_of_scope` boundaries. Breaches > 2 trigger a
warn flag. Implementation details in research output are flagged for Hermes review.

---

### REVIEW — Code Review & Security Audit

**Owner: Codex (ChatGPT 5.5)** (primary), Hermes (fallback)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| PR review | "Review PR #412 for correctness" | `agent:chatgpt55` |
| Security audit | "Audit repo for credential leaks" | `agent:chatgpt55` |
| Code quality scan | "Check codebase for anti-patterns" | `agent:chatgpt55` |
| Architecture review | "Review new microservice design" | `agent:chatgpt55` |
| Proactive scan | "Periodic repo health scan" | `agent:chatgpt55` |

**Output expectations:**
- Verdict: `approved` / `changes_requested` / `blocked`
- Severity counts (critical, high, medium, low, info)
- Findings with file:line references
- Review report at declared path
- Codex handoff contract returned (see [handoff-contracts](./handoff-contracts.md))

**Ownership rule:** Codex is the **primary owner** of REVIEW tasks. Hermes may perform
basic review as fallback (when Codex tokens exhausted), but Hermes reviews are flagged
as "fallback quality."

**Escalation path:**
1. Codex reviews → if `verdict: blocked` → auto-escalates to **Hermes**
2. Hermes investigates blocked findings → if valid security issue → escalates to **Michael**
3. If Codex unavailable (3hr token refresh) → Hermes performs shallow review

**Token windowing:** Deep reviews scheduled within first 60 min of Codex token refresh
cycle. Shallow reviews can run anytime.

---

### DEPLOY — Deployment & Operations

**Owner: Hermes** (sole owner)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Production deploy | "Deploy v2.4.1 to production" | (none — Hermes default) |
| Canary release | "Roll out checkout-api canary to 10%" | (none) |
| Rollback | "Rollback payment-api to v2.4.0" | (none) |
| Health check | "Verify all services post-deploy" | (none) |
| CI/CD pipeline | "Fix broken CI on main" | (none) |
| Infrastructure | "Provision new K8s namespace" | (none) |

**Output expectations:**
- Deploy log or health check report
- Verified artifacts listed
- Verification result (overall pass/fail)
- Hermes handoff contract returned (see [handoff-contracts](./handoff-contracts.md))

**Ownership rule:** Hermes is the **sole owner** of DEPLOY tasks. No other agent has
cluster access or deployment authority.

**Approval gate:** Production deploys **always** require `approval_required: true` with
populated `verification_criteria`. The router rejects deploy tasks without verification
criteria.

**Escalation path:**
1. Hermes deploys → monitors health for 10 min
2. If error rate > 0.1% → auto-rollback → alert `#eng-alerts`
3. If rollback fails → **immediate escalation to Michael**

---

### INCIDENT — Incident Response

**Owner: Hermes** (sole owner)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Outage | "Checkout flow returning 503 for 15% of users" | (none — Hermes default) |
| Performance degradation | "API latency > 2s p95" | (none) |
| Security incident | "Suspicious credential in logs" | (none) |
| Data integrity | "Mismatched chart data in reports" | (none) |

**Output expectations:**
- Triage assessment within 5 min
- Fix deployed or delegated to Jules
- Postmortem at `docs/incidents/<id>.md`
- Incident handoff contract

**Escalation path:**
1. Hermes triages → if automated fix possible, delegates to Jules
2. If unable to fix within 15 min → escalates to **Michael** via Slack `#eng-alerts`
3. Postmortem filed within 24 hours

**Priority override:** Tasks labeled `priority: urgent` bypass classification and route
directly to Hermes.

---

### COORDINATION — Multi-Agent Orchestration

**Owner: Hermes** (sole owner)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Research → Implement | "Research competitor pricing then update our pricing page" | (none) |
| Implement → Review | "Build feature X then have Codex review" | (none) |
| Full pipeline | "AGY research → Jules implement → Codex review → merge" | (none) |
| Cross-validation | "Have 2 agents solve same problem, compare results" | (none) |

**Output expectations:**
- All subagent handoffs aggregated
- Verified artifacts from each phase
- Coordination summary narrative
- Hermes handoff contract returned

**Escalation path:**
1. Any subagent fails → Hermes retries once
2. Subagent fails twice → partial results accepted; Hermes completes manually
3. If Hermes can't complete → escalates to **Michael**

---

### CONTENT — Content Generation & Marketing

**Owner: AGY** (primary), Hermes (fallback)

| Subtype | Examples | Linear Label |
|---------|----------|-------------|
| Blog post | "Write blog post from podcast transcript" | `agent:agy` |
| Social media | "Generate 5 tweets from blog post" | `agent:agy` |
| Podcast notes | "Generate show notes from audio transcript" | `agent:agy` |
| Landing page copy | "Write hero copy for new pricing page" | `agent:agy` |
| Email campaign | "Draft product launch email sequence" | `agent:agy` |

**Output expectations:**
- Content in markdown at declared path
- Research-backed claims with source references
- Scope adherence report

**Escalation path:**
1. AGY generates → Hermes reviews for factual accuracy
2. If inaccurate → AGY regenerates with corrections
3. If still inaccurate after 2 cycles → escalates to **Michael** for human review

---

## Escalation Summary

```
Agent fails once → Retry (automatic)
Agent fails twice → Hermes triage (automatic)
Hermes can't resolve → Michael (Slack #eng-alerts)
```

### Michael Escalation Triggers (Immediate)

| Trigger | Channel | Urgency |
|---------|---------|---------|
| Secrets leaked in output | `#eng-alerts` + key rotation | 🔴 Immediate |
| Production deploy failed + rollback failed | `#eng-alerts` | 🔴 Immediate |
| Agent timed out twice | `#eng-alerts` | 🔴 Immediate |
| Jules CI red after 3 attempts | `#eng-alerts` | 🔴 Immediate |
| `secrets_clean` verification fail | `#eng-alerts` | 🔴 Immediate |

### Michael Escalation Triggers (Deferred — within 1 hour)

| Trigger | Channel |
|---------|---------|
| Verification keeps failing | `#eng-deploys` |
| AGY scope breaches > 3 | `#eng-deploys` |
| Codex `verdict: blocked` with false positive | `#eng-deploys` |
| Subagent stall > 30 min | `#eng-deploys` |

---

## Linear Label Reference

Every automated path ties to a Linear label:

| Task Destination | Linear Label | Automated? |
|-----------------|-------------|------------|
| Jules (code work) | `agent:jules` | ✅ Cron every 15 min |
| Jules (review work) | `agent:jules-review` | ✅ Cron every 15 min |
| AGY (research) | `agent:agy` | ✅ Cron every 60 min |
| Codex (review/audit) | `agent:chatgpt55` | ✅ Cron every 60 min |
| Hermes (orchestration) | (no label — default) | ✅ Default routing |
| Michael (human) | `needs:human` or escalation | ❌ Manual |
| Urgent (bypass routing) | `priority:urgent` | ✅ Auto-routes to Hermes |

---

## Cross-References

- Full routing logic: [routing-decision-matrix](./routing-decision-matrix.md)
- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
- Handoff contracts: [handoff-contracts](./handoff-contracts.md)
- Verification: [verification-checklist](./verification-checklist.md)
- Operator guide: [operator-quickstart](./operator-quickstart.md)
- Architecture overview: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
