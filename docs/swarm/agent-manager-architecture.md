# Agent Manager — Architecture (GRO-34 + GRO-36 + GRO-37)

Unified design for the Hermes Agent Manager: the central UI/orchestration interface
unifying workspace management, session oversight, agent inventory, real-time
monitoring, and PTY/SSE integration across the entire swarm.

---

## Design Philosophy

The Agent Manager is the **human-in-the-loop cockpit** — an air traffic control
tower above individual agent profiles and workspaces. It provides:

- **Orchestration** — Launch, monitor, and chain multi-agent workflows
- **Inventory** — Every profile, model, provider, and wrapper with live state
- **Workspace context** — Organize work by business domain / Linear project
- **Real-time awareness** — Watch live sessions, cron jobs, and CLI agents
- **Quick-launch** — Create sessions in 2 clicks from known-good templates

It is **not** an agent — it's the management layer Hermes operates within.
GRO-34 covers architecture, GRO-36 the registry, GRO-37 the dashboard UI.

---

## Architecture Overview

```
┌──────────┬───────────────────────────────────────┬──────────┐
│  LEFT    │              CENTER                   │  RIGHT   │
│  NAV     │              MAIN                     │  DETAIL  │
│          │                                       │          │
│  🕹️ Orch │  ┌─────────────────────────────────┐  │  📡 Live │
│  📁 Wksp │  │  ORCHESTRATOR AREA (global)     │  │  Stream  │
│  📦 Inv  │  │  Active · Escalations · Timeline│  │  (SSE)   │
│  ⚡ Lnch │  └─────────────────────────────────┘  │          │
│          │  ┌─────────────────────────────────┐  │  Filter: │
│          │  │  INVENTORY / REGISTRY           │  │  Wksp ▾  │
│          │  │  Profiles · Models · Providers  │  │  Agent▾  │
│          │  │  Wrappers · Live State          │  │  Type ▾  │
│          │  └─────────────────────────────────┘  │          │
│          │  ┌─────────────────────────────────┐  │  23:49:01│
│          │  │  WORKSPACE TREE                 │  │  write → │
│          │  │  Sessions · Cron · Repos        │  │  arch.md │
│          │  │  Linear Issues                  │  │  23:48:45│
│          │  └─────────────────────────────────┘  │  term →  │
│          │                                       │  pip ... │
└──────────┴───────────────────────────────────────┴──────────┘
```

3-column layout (nav 60px/200px | center flex | right 400px). Adapts to viewport.
Full components in [agent-manager-plugin-design.md](./agent-manager-plugin-design.md).

---

## 1. Top-Level Orchestrator Area

Not bound to any workspace — the **global command center**.

| Component | Purpose | Data Source |
|-----------|---------|-------------|
| Active Orchestrations | Multi-agent workflows in flight with per-agent status and progress | `sessions.json` filtered by Hermes + `subagent_results` |
| Escalation Queue | Tasks hitting subagent timeout, verification failure, Codex blocked | Router escalation triggers |
| Orchestration Timeline | Chronological: dispatched → handoff → verified → escalated | `handoff-contracts` from outputs |
| Intervention Panel | Buttons: retry, escalate to human, rollback, waive check | Operator actions mapped to escalation paths |
| Recently Completed | Tasks finished in last 24h | Sessions: `completed_at > now-24h` |

```
┌──────────────────────────────────────────────────────────────┐
│ 🕹️ ORCHESTRATOR                                    [⚡ New] │
├──────────────────────────────────────────────────────────────┤
│ ACTIVE (2)                                                   │
│  🔵 GRO-87  research_coordination   ████████░░░░ 75%        │
│     AGY ✅ → Jules ✅ → Codex ⏳ → Verify ⬜                │
│  🟡 INC-47  incident_response       ████░░░░░░░░ 27%        │
│                                                              │
│ ESCALATION (1): 🔴 GRO-102 [Retry] [Escalate to Human]      │
│ RECENT: ✅GRO-85 ✅GRO-77 ✅GRO-81 ✅GRO-80                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Workspace Organization Model

Workspaces map 1:1 to `config.yaml → workspaces[]` and mirror **Linear projects**
and GitHub repos. Each entry defines local paths, repos, Linear projects,
default/allowed profiles, and tags.

```yaml
workspaces:
  - id: agentic-swarm-ops
    name: Agentic Swarm Ops
    local_paths: [/home/ubuntu/work/agentic-swarm-ops]
    github_repos: [mbgulden/agentic-swarm-ops]
    linear_projects: [Agentic Swarm Ops Documentation]
    default_profile: orchestrator
    allowed_profiles: [orchestrator, hermes-local, agy, codex, jules]
```

### Workspace Tree

```
Agentic Swarm Ops                    🟢 3 active
├── 📁 Sessions (12)
│   ├── 🔵 session_20260529_234901  [running · orchestrator]
│   └── ✅ session_cron_fb95eb46ffd7 [completed · cron]
├── ⏰ Cron (4): jules-session-manager[15m] pr-auto-merger[60m] ...
├── 📦 GitHub: mbgulden/agentic-swarm-ops
└── 🏷️ Linear: GRO-34, GRO-36, GRO-37
Sovereign Sentinel · Active Oahu · Asset Forge 3D · ... (7 total)
```

**Affordances:** Click filters panels to workspace; right-click sets active context
for Quick-Launch; badges show session count + escalation alerts; default profile
pre-selects Quick-Launch.

**Session binding:** (1) explicit launch selector, (2) cwd/file ops in `local_paths`,
(3) GitHub ops in `github_repos`, (4) last active workspace context. Cross-workspace
sessions appear under both trees with "shared" indicator.

---

## 3. Profile / Model / Agent Registry with States

The Inventory Panel is the single source of truth for everything that CAN run an
agent. Full taxonomy: [agent-registry-design.md](./agent-registry-design.md).

### Profiles

| Profile | Default Model | Context | Primary Role |
|---------|--------------|---------|-------------|
| `orchestrator` | deepseek-v4-pro | 1M | Coordination, ops, deploy |
| `hermeslocal` | hermes3:70b-q4 | 65K–131K | Local orchestration |
| `qwenlocal` | qwen3:32b-q4 | 65K–256K | Lightweight local tasks |
| `agy` | varies | — | Research, vision, Drive |
| `codex` | gpt-5.5 | 272K | Code review, security audit |
| `jules` | N/A (CLI) | — | Code implementation, PRs |

### Models & Providers

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| deepseek-v4-pro | deepseek (cloud) | 1M | Orchestration, large ctx |
| deepseek-v4-flash | deepseek (cloud) | 1M | Compression, fast aux |
| gpt-5.5 | openai-codex (cloud) | 272K | Code review, security |
| gpt-5.4-mini/nano | openai-codex | —/400K | Vision, extraction |
| hermes3:70b-q4 | ollama-hermes (local) | 65K–131K | Local orchestration |
| qwen3:32b-q4 | ollama-qwen (local) | 65K–256K | Local lightweight tasks |

### Agent Wrappers

| Wrapper | Invocation | Output |
|---------|-----------|--------|
| Hermes profile | `hermes -p <profile>` | Sessions, file edits, handoff |
| AGY CLI | `agy --print` (PTY) | Research docs, analysis |
| Jules CLI | `jules new --repo ...` | GitHub PR, branch, commit |
| Codex CLI | `hermes -p codex-5-5 -z "..."` | Review report, verdict |
| Cron job | `cron/jobs.json` | Periodic markdown output |
| Gateway | Telegram/Slack message | Conversational response |

### State Tracking

Every item has a live state. Session states: `running` 🔵, `idle` 🟢, `completed` ✅,
`failed` ❌, `timed_out` ⏰, `cancelled` 🚫, `escalated` 🔴.

| State | Icon | Applies To | Trigger |
|-------|------|-----------|---------|
| `active` | 🟢 | Profiles, models, providers | Operating normally |
| `busy` | 🔵 | Profiles, Jules (near cap) | At capacity |
| `available` | 🟢 | Profiles, models | Idle, ready |
| `inactive` | ⚫ | Local models, optional profiles | Configured, not running |
| `endpoint-down` | 🔴 | Providers | 3× health check failure |
| `auth-unverified` | 🟡 | Providers | API key needs rotation |
| `rate-limited` | 🟡 | codex (3hr), cloud (429) | Token refresh active |
| `degraded` | 🟠 | Profiles | Running on fallback |
| `error` | 🔴 | Profiles, cron, providers | Needs intervention |

State cascades: Provider health → Model availability → Profile status → Session
capacity. Alerts on endpoint-down, auth-unverified, 3+ failures/hr, escalated.

---

## 4. Quick-Launch Orchestrator Session Creator

Guided 4-step workflow: **Select Workspace → Select Recipe → Configure → Launch.**

| Recipe | Profile | Description |
|--------|---------|-------------|
| Quick code fix | jules | Bug fix, small feature, refactor |
| Research question | agy | Analyze docs, web, Drive |
| Code review | codex | Audit a PR for security/quality |
| Multi-agent pipeline | orchestrator | AGY → Jules → Codex → Verify |
| Deploy supervision | orchestrator | Watch k8s deploy, health checks |
| Incident response | orchestrator | Triage alert, delegate fix |
| Documentation | orchestrator | Write/update swarm docs |

Panel flow:
```
Workspace: [Agentic Swarm Ops ▾]   Profile: [orchestrator ▾]  Model: [deepseek-v4-pro ▾]
Recipe:  ○ Quick fix  ○ Research  ● Multi-agent  ○ Custom
Goal:   [Design the Agent Manager plugin dashboard              ]
Phases: ☑ AGY Research  ☐ Jules (skip)  ☑ Verify   Timeout: [45 min]
Verification: ☑ file_exists  ☑ syntax_valid  ☑ matches_spec
              [🚀 Launch Orchestration]
```

On launch: generates Hermes prompt → dispatches → session appears in Orchestrator
and Workspace Tree → Live Stream begins. See [hermes-prompt-template.md](./hermes-prompt-template.md).

---

## 5. Workspace → Session → Run Hierarchy

```
WORKSPACE (business domain) → SESSION (agent invocation) → RUN (tool call)
```

| Level | Identity | 1:N | Tracks |
|-------|----------|-----|--------|
| **Workspace** | `workspace.id` | N sessions | Repos, paths, Linear projects, allowed profiles |
| **Session** | `session_YYYYMMDD_HHMMSS_<random6>.json` | N runs | Profile, model, provider, channel, context %, tokens, tool calls, cwd, handoff, verification |
| **Run** | Turn number | — | Tool name/args, execution time, output, success/failure |

Session state machine: `created → running → (completed | failed | timed_out | cancelled)`.
Gateway sessions may enter `idle` between user messages.

```
Workspace: agentic-swarm-ops
├── Session: session_20260529_234901  [running · orchestrator]
│   ├── Run 1: search_files("hermes*")           [0.8s ✅]
│   ├── Run 2: read_file("config.yaml")           [0.3s ✅]
│   ├── Run 3: write_file("agent-manager-*.md")   [1.2s ✅]
│   └── Run 4: terminal("git status")             [0.5s ✅]
├── Session: session_cron_fb95eb46ffd7  [completed · cron]
│   └── Runs: Linear API query → write cron output
├── Session: session_20260529_224927  [idle · telegram]
│   └── Runs 1–23: multi-turn conversation
└── Session: session_20260529_223340  [failed · jules]
    └── Runs: git clone ✅ → npm install ✅ → test run ❌ → escalated
```

---

## 6. Dashboard Plugin Layout

Registers as a Hermes Dashboard plugin (theme: cyberpunk). Full skeletons in
[agent-manager-plugin-design.md](./agent-manager-plugin-design.md).

### Panel Map

| Panel | Nav | Content | Refresh |
|-------|-----|---------|---------|
| Orchestrator | 🕹️ | Active orchestrations, escalation queue, timeline, completed | 5s |
| Workspaces | 📁 | Tree: workspace → sessions → cron → repos → Linear | 5s |
| Inventory | 📦 | Profiles, models, providers, wrappers + live states | 30s |
| Live Stream | 🔍 | Real-time events: tool calls, handoffs, cron, escalations | Push |
| Quick Launch | ⚡ | Guided session creator with recipes | On demand |

### Data Sources

| Data | Source | Update |
|------|--------|--------|
| Workspaces, Profiles, Providers | `config.yaml` | Config reload |
| Models | `models_dev_cache.json` | 24h TTL |
| Sessions | `sessions/sessions.json` + `session_*.json` | File watch 5s |
| Cron jobs | `cron/jobs.json` | File watch 30s |
| Health status | Runtime polls (HTTP, Ollama `/api/tags`, inference) | 60s–3600s |
| Stream events | File watcher + log tailer + webhooks | Push |
| GitHub/Linear | Webhook → state.db | Push |

### Responsive & Shortcuts

Desktop 1200px+: 3-column. Tablet: 2-column (icons+center, right=drawer). Mobile:
single column, bottom tabs. Keys: `1`–`5` switch panels, `/` search, `n` new,
`j`/`k` navigate, `p` pause stream, `Ctrl+[`/`]` collapse/expand nav.

---

## 7. Integration: PTY Manager & SSE Streams

### PTY Manager

Integrates with the PTY session layer (see [visible-terminal-workflow.md](./visible-terminal-workflow.md)):

- **Session lifecycle:** PTY manager handles `pty=true` connections (AGY, Hermes
  in VS Code). Agent Manager reads state from `sessions/session_*.json` and
  displays terminal output in stream panel.
- **Single-writer enforcement:** Only one browser tab owns the PTY/SSE connection.
  [cross-tab-sync.md](./cross-tab-sync.md) leader election (BroadcastChannel +
  localStorage) ensures leader tab maintains sole connection; viewers get STATE_DELTA.
- **Intervention:** Intervention Panel commands (`hermes process submit | kill | close`)
  flow through PTY manager for stdin injection, session kill, or EOF.
- **tmux multiplexing:** PTY manager supports tmux window-per-agent for concurrent
  watching; Agent Manager shows tmux session names with attach/detach.

### Multiplexed SSE Streams

Live Stream panel consumes multiplexed SSE as defined in
[multiplexed-sse-streams.md](./multiplexed-sse-streams.md):

```
PTY (AGY) ──┐
PTY (Jules)─┼──→ SessionStreamMultiplexer ──→ GET /api/sessions/{id}/stream
PTY (Codex)─┘         (server fan-in)                    │
                                              ┌──────────▼─────────┐
                                              │  StreamDemuxer      │
                                              │  (leader tab only)  │
                                              └──────────┬──────────┘
                                                         │
                                         BroadcastChannel STATE_DELTA
                                                         │
                                              Leader Tab · Viewer 1 · Viewer 2
```

- **Single SSE endpoint** carries all tasks. Events include `task-id`, `task-state`,
  `parent-task` fields for client-side demuxing.
- **Event types:** `task:created`, `task:progress`, `task:log`, `task:artifact`,
  `task:error`, `task:completed`, `task:heartbeat`, `session:metadata`, `stream:eos`.
- **Leader-only EventSource:** Viewer tabs receive state via BroadcastChannel
  (per cross-tab-sync). Late-joiners replay from 5-min ring buffer via `Last-Event-ID`.
- **Backpressure:** Client buffer >64KB drops non-critical `task:log`; server replays
  from ring buffer when pressure clears.
- **Polling fallback:** When SSE unavailable, polls `GET .../events?since={id}` at
  2s intervals (adaptive to 5s when idle).

---

## Data Flow

```
config.yaml ──→ Workspaces, Profiles, Providers
sessions.json + session_*.json ──→ Sessions, runs, handoffs
models_dev_cache.json ──→ Model catalog
cron/jobs.json ──→ Cron jobs
channel_directory.json ──→ Gateway channels
Health polls ──→ Provider/model status
Webhooks (GitHub/Linear) ──→ Repo + issue events
File watchers ──→ Stream events
     │
     ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   AGENT MANAGER STATE   │───→│  DASHBOARD PLUGIN UI    │
│  (unified aggregation)  │    │  (Hermes Dashboard)     │
└─────────────────────────┘    └─────────────────────────┘
```

---

## Cross-References

- [agent-registry-design.md](./agent-registry-design.md) — Roles, models, providers, wrappers, states (GRO-36)
- [agent-manager-plugin-design.md](./agent-manager-plugin-design.md) — UI component skeletons (GRO-37)
- [multiplexed-sse-streams.md](./multiplexed-sse-streams.md) — Real-time stream protocol
- [cross-tab-sync.md](./cross-tab-sync.md) — Leader election, shared state
- [visible-terminal-workflow.md](./visible-terminal-workflow.md) — PTY modes, terminal multiplexing
- [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md) — Overall agent architecture
- [handoff-contracts.md](./handoff-contracts.md) — Output formats for Orchestrator Area
- [hermes-prompt-template.md](./hermes-prompt-template.md) — YAML structure Quick-Launch generates
