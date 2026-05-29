# Swarm Workflow — How All Agents Work Together

## The Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│                  LINEAR                         │
│  Task Ledger — every task has an issue          │
│  Labels route work: agent:jules, agent:agy, etc │
└──────────────────┬──────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────────┐
│  JULES  │  │   AGY    │  │ HERMES/FRED  │
│  Coder  │  │Research  │  │ Orchestrator │
└────┬────┘  └────┬─────┘  └──────┬───────┘
     │            │               │
     ▼            ▼               ▼
┌─────────────────────────────────────────────────┐
│                 GITHUB                          │
│  Code + PRs + Reviews — the durable ledger      │
│  Feature branches per Linear issue              │
└─────────────────────────────────────────────────┘
```

## Repo Map — Which Linear Project → Which GitHub Repo

| Linear Project | GitHub Repo | Nickname |
|---------------|-------------|----------|
| HD Engine Core, Reports, Growth, Creator, Coach, Consumer, Enterprise, Dating, Education, AI Lab | `mbgulden/hd-platform` | `hd-platform` |
| OpenHumanDesignMCP | `mbgulden/OpenHumanDesignMCP` | `hd-engine` |
| Agentic Swarm Ops | `mbgulden/agentic-swarm-ops` | `swarm-ops` |
| Sovereign Sentinel | `mbgulden/SovereignSentinel` | `sentinel` |
| Active Oahu Tours | `mbgulden/activeoahutours.com` | `active-oahu` |
| Project Honeybadger | `mbgulden/hd-platform` | `hd-platform` |
| AI Consulting | `mbgulden/ai-consulting` | `ai-consulting` |

## Branch Convention

Every task uses a feature branch named after its Linear issue:

```
gro-XX/brief-description
```

Examples:
- `gro-100/weekly-podcast-automation`
- `gro-96/rapidapi-marketplace-listing`
- `gro-88/launch-hd-api`

**Never work directly on `main`.** Jules auto-creates branches when given repo access.

## How Jules Gets Assigned

### Method 1: Linear Label (Automated)
1. Add label `agent:jules` to any Linear issue in "Todo" or "In Progress"
2. The **Jules Session Manager** (cron every 15min) detects it
3. Automatically launches `jules new --repo OWNER/REPO "Linear: GRO-XX ..."`
4. Jules session ID posted as Linear comment
5. Session tracked in `/tmp/jules-session-tracker.json`

### Method 2: GitHub Issue Comment
1. On any GitHub issue in an orchestrated repo, comment `/agent jules`
2. The **Orchestration Router** GitHub Action fires
3. Classifies and routes to Jules
4. Decision artifact saved as workflow artifact

### Method 3: Direct CLI (Manual)
```bash
jules new --repo mbgulden/hd-platform "Linear: GRO-100 — Build weekly podcast automation"
```

## The Review Pipeline

```
Agent completes work → pushes to feature branch → opens PR
                        ↓
              PR Auto-Merger checks CI + tests
                        ↓
    ┌─ CI passes + approved → AUTO-MERGE to main
    │
    └─ CI fails → Linear comment with failure details
                        ↓
              Human or Hermes reviews and fixes
```

To request a Jules review of completed work:
1. Add label `agent:jules-review` to the Linear issue
2. Jules Session Manager launches a review session
3. Jules reviews the PR, adds comments, reports findings

## Agent Role Matrix

| Agent | Best For | How to Invoke |
|-------|----------|---------------|
| **Jules** | Coding, PRs, docs, tests, refactors, security audits | Label `agent:jules` on Linear |
| **AGY** | Research, Google Docs analysis, broad synthesis, vision | Label `agent:agy` on Linear |
| **Hermes/Fred** | Orchestration, planning, validation, cross-agent coordination | Default — no label needed |
| **Codex** | Local interactive debugging, conflict resolution, review | Label `agent:codex` on Linear |

## Jules Capacity & Limits

- **Max: 300 sessions/day**
- **Max concurrent: 10** (configurable in session manager)
- Jules works from **GitHub state only** — push before assigning
- Jules cannot touch local files, env vars, or secrets
- Repos with broken CI/CD should not be routed to Jules

## How to Use This System

### To assign work to Jules:
```
1. Create a Linear issue with a clear title and description
2. Add label "agent:jules"
3. The system handles the rest:
   - Session launched within 15 minutes
   - Branch created, code written, PR opened
   - CI runs, PR auto-merged if approved
```

### To have Jules review completed work:
```
1. Add label "agent:jules-review" to the Linear issue
2. Ensure the PR is open and linked to the issue
3. Jules reviews and comments within 15 minutes
```

### Active Cron Jobs That Power This:

| Job | Interval | What It Does |
|-----|----------|-------------|
| `jules-session-manager` | Every 15min | Linear → Jules bridge |
| `pr-auto-merger` | Every 60min | Auto-merge approved PRs, route conflicts |
| `jules-monitor` | Every 30min | Pull completed Jules sessions |
| `agy-reporter` | Every 60min | Check AGY research progress |

## Repo Health Requirements

Before routing work to Jules, the target repo must:
1. Have a clean `main` branch (CI passing)
2. Be accessible via `jules remote list --repo`
3. Not have uncommitted local-only files that Jules needs
4. Have clear issue descriptions (Jules works from Linear text)
