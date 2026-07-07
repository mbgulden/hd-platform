# Agent Manager — Dashboard Plugin Design (GRO-37)

Skeleton design for the Hermes Dashboard plugin that renders the Agent Manager
as an interactive UI surface. This is a **presentation-layer design** — it defines
the visual structure, navigation, panels, and data bindings. No implementation.

---

## Plugin Registration

The Agent Manager registers as a Hermes Dashboard plugin, extending the existing
dashboard infrastructure.

### Plugin Manifest (Conceptual)

```yaml
# ~/.hermes/plugins/agent-manager/plugin.yaml
id: agent-manager
name: Agent Manager
version: 1.0.0
description: Multi-agent swarm cockpit — orchestration, workspaces, sessions, inventory
author: Hermes Swarm Team
dashboard:
  theme: cyberpunk
  icon: "🕹️"
  nav:
    - id: orchestrator
      label: Orchestrator
      component: OrchestratorPanel
      default: true
    - id: workspaces
      label: Workspaces
      component: WorkspaceTree
    - id: inventory
      label: Inventory
      component: InventoryPanel
    - id: streams
      label: Live Stream
      component: StreamPanel
    - id: quick-launch
      label: Quick Launch
      component: QuickLaunchPanel
  data_sources:
    - config_path: "~/.hermes/profiles/orchestrator/config.yaml"
      bindings: [workspaces, profiles, providers]
    - config_path: "~/.hermes/profiles/orchestrator/sessions/sessions.json"
      bindings: [session_list]
    - config_path: "~/.hermes/profiles/orchestrator/cron/jobs.json"
      bindings: [cron_jobs]
    - config_path: "~/.hermes/profiles/orchestrator/models_dev_cache.json"
      bindings: [model_catalog]
    - config_path: "~/.hermes/profiles/orchestrator/channel_directory.json"
      bindings: [channels]
    - live_source: session_file_watcher
      bindings: [session_details, session_output, stream_events]
    - live_source: health_poller
      bindings: [provider_status, model_status, auth_status]
    - live_source: webhook_receiver
      bindings: [github_events, linear_events]
  refresh:
    inventory: 30s
    session_list: 5s
    session_details: 2s (when focused)
    streams: real-time (push)
    health: 60s
    webhooks: real-time (push)
```

---

## Layout: 3-Column Dashboard

```
┌──────────┬───────────────────────────────┬──────────┐
│          │                               │          │
│  LEFT    │         CENTER                │  RIGHT   │
│  NAV     │         MAIN                  │  DETAIL  │
│          │                               │          │
│  ┌────┐  │  ┌─────────────────────────┐  │  ┌────┐  │
│  │ 🕹️ │  │  │                         │  │  │Live│  │
│  │ Orch│  │  │   ORCHESTRATOR AREA     │  │  │Str.│  │
│  │     │  │  │                         │  │  │    │  │
│  ├────┤  │  │  Active · Escalations    │  │  │    │  │
│  │ 📁 │  │  │  Completed · Timeline    │  │  │    │  │
│  │ Wksp│  │  │                         │  │  │    │  │
│  │     │  │  └─────────────────────────┘  │  │    │  │
│  ├────┤  │  ┌─────────────────────────┐  │  │    │  │
│  │ 📦 │  │  │   INVENTORY / REGISTRY  │  │  │    │  │
│  │ Inv │  │  │                         │  │  └────┘  │
│  │     │  │  │  Profiles · Models      │  │          │
│  ├────┤  │  │  Providers · Wrappers    │  │          │
│  │ 🔍 │  │  │                         │  │          │
│  │ Srch│  │  └─────────────────────────┘  │          │
│  │     │  │  ┌─────────────────────────┐  │          │
│  ├────┤  │  │   WORKSPACE TREE         │  │          │
│  │ ⚡ │  │  │                         │  │          │
│  │Lnch│  │  │  Folders · Sessions      │  │          │
│  │     │  │  │  Cron · Repos · Linear  │  │          │
│  └────┘  │  │                         │  │          │
│          │  └─────────────────────────┘  │          │
│          │                               │          │
└──────────┴───────────────────────────────┴──────────┘
```

### Column Definitions

| Column | Width | Content | Responsive Behavior |
|--------|-------|---------|-------------------|
| **Left Nav** | 60px (icons only) / 200px (expanded) | Icon strip: Orchestrator, Workspaces, Inventory, Search, Quick Launch | Collapses to icon-only on narrow screens |
| **Center Main** | Flexible (60%) | Active panel content: orchestrator view, workspace tree, inventory, or quick-launch form | Scrolls vertically |
| **Right Detail** | 400px (collapsible) | Live stream panel + contextual detail (selected session, escalated task, agent status) | Can be hidden to maximize center |

---

## Panel 1: Orchestrator Top Area

The primary dashboard view. Shows all active orchestrations, escalation queue,
recently completed tasks, and the orchestration timeline.

### Data Bindings

| UI Element | Data Source | Refresh |
|-----------|-------------|---------|
| Active orchestrations list | `sessions.json` filtered: `profile=orchestrator AND status=running AND has(subagent_results)` | 5s |
| Orchestration progress bars | Session file: `tool_calls / max_turns`, `elapsed / timeout_minutes` | 5s |
| Escalation queue | Sessions where `status=escalated OR verification_result.overall=fail` | 10s |
| Recently completed | Sessions: `status=completed AND completed_at > now-24h` | 30s |
| Timeline feed | Aggregated stream events filtered to orchestration type | Real-time (push) |

### Component Skeleton

```
┌──────────────────────────────────────────────────────────────┐
│ 🕹️ ORCHESTRATOR                                    [⚡ New] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌─ Active Orchestrations (2) ────────────────────────────┐  │
│ │                                                        │  │
│ │  🔵 GRO-87  research_coordination                     │  │
│ │  ┌──────────────────────────────────────────────────┐ │  │
│ │  │ Pipeline: AGY → Jules → Codex → Verify            │ │  │
│ │  │ AGY      ✅ completed  47m  q2-pricing.md         │ │  │
│ │  │ Jules    ✅ PR #43     15 tests pass, 87% cov     │ │  │
│ │  │ Codex    ⏳ pending     scheduled in 12m          │ │  │
│ │  │ Verify   ⬜ waiting                                │ │  │
│ │  │ Progress ████████████░░░░ 75%   Elapsed: 62m/90m │ │  │
│ │  └──────────────────────────────────────────────────┘ │  │
│ │  [View Details]  [Cancel]  [Escalate]                │  │
│ │                                                        │  │
│ │  🟡 INC-47  incident_response                         │  │
│ │  ┌──────────────────────────────────────────────────┐ │  │
│ │  │ Investigating checkout 503 errors                │ │  │
│ │  │ Root cause: suspected deploy v2.4.1              │ │  │
│ │  │ Progress ████░░░░░░░░░░░░ 27%  Elapsed: 8m/15m  │ │  │
│ │  └──────────────────────────────────────────────────┘ │  │
│ │  [View Details]  [Rollback]  [Escalate]              │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ Escalation Queue (1) ────────────────────────────────┐  │
│ │                                                        │  │
│ │  🔴 GRO-102  jules  test failure                      │  │
│ │  ┌──────────────────────────────────────────────────┐ │  │
│ │  │ 3/8 tests failing · Stripe webhook sig verify    │ │  │
│ │  │ Escalated: 23:45  Reason: subagent failure       │ │  │
│ │  │ Action needed: config Stripe test secret in CI    │ │  │
│ │  └──────────────────────────────────────────────────┘ │  │
│ │  [Retry Jules]  [Escalate to Human ↗]  [Dismiss]     │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ Recently Completed (last 24h) ───────────────────────┐  │
│ │                                                        │  │
│ │  ✅ GRO-85  20:15  operator quickstart                │  │
│ │  ✅ GRO-77  18:45  competitor pricing analysis        │  │
│ │  ✅ GRO-81  17:30  hermes prompt template             │  │
│ │  ✅ GRO-80  17:00  jules prompt template              │  │
│ │  ✅ GRO-79  16:15  agy prompt template                │  │
│ │  ... 7 more                                           │  │
│ │                                   [View All History →] │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ Orchestration Timeline ───────────────────────────────┐  │
│ │                                                        │  │
│ │  23:49  GRO-34 launched          orchestrator          │  │
│ │  23:45  GRO-102 escalated        test failure          │  │
│ │  23:33  cron:fb95eb completed     output written       │  │
│ │  23:30  GRO-87  AGY handoff      verification pass    │  │
│ │  23:15  GRO-87  Jules started    PR in progress       │  │
│ │  22:45  GRO-87  AGY completed     key findings: 5     │  │
│ │  22:00  GRO-87  launched          multi-agent coord.  │  │
│ │                                                        │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Panel 2: Workspace Tree

Hierarchical navigation showing all workspaces, their sessions, cron jobs, GitHub
repos, and Linear projects. Mirrors the `workspaces[]` array from `config.yaml`.

### Data Bindings

| UI Element | Data Source | Refresh |
|-----------|-------------|---------|
| Workspace list | `config.yaml → workspaces[]` | On config reload |
| Session count per workspace | `sessions.json` filtered by workspace binding | 5s |
| Session items under workspace | Session files with matching `workspace` field | 5s |
| Cron jobs under workspace | `cron/jobs.json` filtered by workspace | 30s |
| GitHub repos under workspace | `workspace.github_repos` + webhook events | Webhook (push) |
| Linear projects under workspace | `workspace.linear_projects` + webhook events | Webhook (push) |

### Workspace-to-Session Binding

Sessions bind to workspaces via:
1. **Explicit:** Session was launched with a workspace selector
2. **Path-based:** Session's `cwd` or file operations are within `workspace.local_paths[]`
3. **Repo-based:** Session's GitHub operations target `workspace.github_repos[]`
4. **Default:** Gateway sessions use the last active workspace context

### Component Skeleton

```
┌──────────────────────────────────────────────────────────────┐
│ 📁 WORKSPACES                                        [Filter]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ▼ Agentic Swarm Ops                      🟢 3 active       │
│  │  📁 Sessions (12)                                        │
│  │  ├── 🔵 session_20260529_234901   orchestrator  running  │
│  │  ├── 🔵 session_20260529_234902   orchestrator  running  │
│  │  ├── 🔵 session_20260529_234903   orchestrator  running  │
│  │  ├── ✅ session_cron_fb95eb46ffd7  cron         completed│
│  │  ├── ✅ session_20260529_224927    telegram     completed│
│  │  ├── 🟢 session_20260529_223340    telegram     idle     │
│  │  ├── ✅ session_20260529_224025    telegram     completed│
│  │  ├── ❌ session_20260529_223341    jules        failed   │
│  │  └── ... 4 more                                          │
│  │  ⏰ Cron Jobs (4)                                        │
│  │  ├── jules-session-manager  15m   last: 23:45 ✅        │
│  │  ├── pr-auto-merger         60m   last: 23:00 ✅        │
│  │  ├── jules-monitor          30m   last: 23:30 ✅        │
│  │  └── agy-reporter           60m   last: 23:00 ✅        │
│  │  📦 GitHub (mbgulden/agentic-swarm-ops)                 │
│  │  ├── Branch: gro-34/agent-manager-arch                  │
│  │  ├── Branch: gro-36/agent-registry                      │
│  │  └── Branch: gro-37/agent-manager-plugin                │
│  │  🏷️ Linear (Agentic Swarm Ops Documentation)           │
│  │  ├── GRO-34  In Progress  Agent Manager Architecture    │
│  │  ├── GRO-36  In Progress  Agent Registry Design         │
│  │  └── GRO-37  In Progress  Agent Manager Plugin Design   │
│  │                                                          │
│  ▶ Sovereign Sentinel                      ⚫ 0 active      │
│  ▶ Sentinel IT Asset Logistics             ⚫ 0 active      │
│  ▶ Active Oahu                             🟢 1 active      │
│  ▶ Asset Forge 3D                          ⚫ 0 active      │
│  ▶ Google Drive / Gemini Context           🟢 1 active      │
│  ▶ Hermes Inbox                            ⚫ 0 active      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Workspace Tree Interactions

| Action | Behavior |
|--------|----------|
| **Click workspace** | Filters center panel to that workspace's sessions and details |
| **Click session** | Opens session detail in right panel (runs, output, handoff) |
| **Click cron job** | Shows job history, last output, next run time |
| **Click GitHub branch** | Opens PR list for that branch (if any) |
| **Click Linear issue** | Opens issue details, status, linked PRs |
| **Right-click workspace** | Context menu: Set as Active, Quick Launch here, View all sessions, View cron output |
| **Workspace badge** | Shows active session count; red dot if escalation exists |

---

## Panel 3: Session List (Nested Under Workspaces)

When a workspace is selected, the session list shows all sessions in that workspace
with expandable detail.

### Data Bindings

| UI Element | Data Source | Refresh |
|-----------|-------------|---------|
| Session list | `sessions/sessions.json` filtered by workspace | 5s |
| Session metadata | Session JSON file header | On selection |
| Session runs (tool calls) | Session JSON file `messages[]` | 2s (when focused) |
| Session output | Session JSON file tool results | 2s (when focused) |
| Session handoff | Parsed handoff contract YAML from session output | On completion |
| Session verification | Verification results from handoff or post-hoc check | On completion |

### Session Detail (Right Panel)

```
┌──────────────────────────────────────────────────────────────┐
│ Session: session_20260529_234901               🔵 running    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Profile:   orchestrator                                     │
│  Model:     deepseek-v4-pro                                  │
│  Provider:  deepseek 🟢                                      │
│  Channel:   telegram (Michael Gulden)                        │
│  Workspace: agentic-swarm-ops                               │
│  Created:   2026-05-29 23:49:01                              │
│  Elapsed:   4m 32s                                           │
│  Tool calls: 5                                               │
│  Context:   12K / 1M tokens (1%)                            │
│                                                              │
│ ┌─ Runs ────────────────────────────────────────────────┐   │
│ │                                                        │   │
│ │  Run 1  ✅  search_files("hermes*")           0.8s     │   │
│ │  Run 2  ✅  read_file("config.yaml")          0.3s     │   │
│ │  Run 3  ✅  write_file("agent-manager-*.md")  1.2s     │   │
│ │  Run 4  ✅  terminal("git status")            0.5s     │   │
│ │  Run 5  🔵  thinking...                               │   │
│ │                                                        │   │
│ │  [Expand Run 3]                                        │   │
│ │  ┌──────────────────────────────────────────────────┐ │   │
│ │  │ Tool: write_file                                 │ │   │
│ │  │ File: docs/swarm/agent-manager-architecture.md   │ │   │
│ │  │ Bytes written: 33,724                            │ │   │
│ │  │ Duration: 1.2s                                   │ │   │
│ │  │ Status: ✅ success                               │ │   │
│ │  └──────────────────────────────────────────────────┘ │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│  [View Full Output]  [Cancel Session]  [Escalate]           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Session Color Coding

| Color | State | Example |
|-------|-------|---------|
| 🔵 Blue | Running (active tool execution) | Active CLI or gateway session |
| 🟢 Green | Idle (gateway session waiting for user) | Telegram session between messages |
| ✅ Green check | Completed successfully | Handoff contract produced, verification passed |
| ❌ Red X | Failed | Tool error, test failure, handoff incomplete |
| ⏰ Yellow clock | Timed out | Exceeded timeout_minutes |
| 🚫 Gray | Cancelled | Operator cancelled |
| 🔴 Red | Escalated | Hit escalation path, needs human |

---

## Panel 4: Real-Time Stream Panel

A live tail of all agent activity. Displayed in the right column (collapsible)
or as a full-width panel when selected from the left nav.

### Data Bindings

| UI Element | Data Source | Refresh |
|-----------|-------------|---------|
| Stream entries | Aggregated from: session file watcher, log tailer, cron output watcher, webhook events | Real-time (push) |
| Stream filters | Client-side filter state | On filter change |

### Stream Entry Types

| Entry Type | Icon | Color | Source |
|-----------|------|-------|--------|
| Session started | ▶️ | Blue | New session file detected |
| Tool call | 🔧 | Default | Session file `messages[]` append |
| Tool result | ✅/❌ | Green/Red | Session file tool response |
| Thinking/reasoning | 💭 | Dim | Session file reasoning block |
| File written | 📝 | Green | `write_file` / `patch` tool result |
| Terminal output | 💻 | Default | `terminal` tool result |
| Cron tick | ⏰ | Blue | Cron scheduler event |
| Cron completed | ✅ | Green | Cron output file written |
| Handoff produced | 📋 | Blue | Handoff contract parsed from output |
| Verification | ✅/❌ | Green/Red | Verification check result |
| Escalation | 🚨 | Red | Escalation trigger |
| GitHub event | 🔀 | Purple | Webhook: PR, push, review, CI |
| Linear event | 🏷️ | Orange | Webhook: issue update, label, comment |
| Gateway message | 💬 | Blue | User message received on any channel |
| Gateway response | 🤖 | Default | Hermes response sent to channel |
| Health check | 🩺 | Dim | Provider/model health poll result change |
| Error | 🔴 | Red | `logs/errors.log` new entry |

### Component Skeleton

```
┌──────────────────────────────────────────────────────────────┐
│ 🔍 LIVE STREAM                      [All ▾] [🔇 Pause] [🗑] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  23:49:03  ⏰ [cron:c4b717]  AGY session started             │
│            workspace: agentic-swarm-ops                      │
│                                                              │
│  23:49:01  📝 [session:3919d7]  write_file →                 │
│            docs/swarm/agent-manager-architecture.md           │
│            bytes: 33,724  duration: 1.2s                     │
│                                                              │
│  23:48:45  💻 [session:57e797]  terminal →                   │
│            $ pip install agent-manager-deps                  │
│            Successfully installed...                         │
│                                                              │
│  23:48:30  📋 [handoff]  AGY → completed                    │
│            task: GRO-77  deliverable: q2-pricing.md           │
│            verification: file_exists ✅  syntax ✅            │
│                                                              │
│  23:47:00  ⏰ [cron:fb95eb]  Jules session manager tick     │
│            checked Linear: 0 new agent:jules labels          │
│                                                              │
│  23:45:00  💬 [telegram]  Michael Gulden →                   │
│            "Design the Agent Manager architecture"            │
│                                                              │
│  23:44:55  🤖 [telegram]  Hermes →                          │
│            "I'll design the Agent Manager architecture..."    │
│                                                              │
│  23:33:00  ✅ [cron:fb95eb]  Cron job completed              │
│            output: 2026-05-29_23-33-02.md                    │
│                                                              │
│  23:18:59  ✅ [cron:c4b717]  Cron job completed              │
│  23:07:14  ✅ [cron:b7996d]  Cron job completed              │
│  23:04:09  ✅ [cron:289104]  Cron job completed              │
│                                                              │
│ ─── Older (scroll for more) ───                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Stream Filter Dropdown

```
Filter: [All Events ▾]
  ○ All Events
  ○ Sessions Only
  ○ Cron Only
  ○ Handoffs & Verification
  ○ Escalations
  ○ GitHub Events
  ○ Linear Events
  ○ Errors Only
  ○ Custom...

Workspace: [All Workspaces ▾]
  ○ All Workspaces
  ○ Agentic Swarm Ops
  ○ Active Oahu
  ○ Sovereign Sentinel
  ○ ...

Search: [________________] 🔍
```

---

## Panel 5: Quick-Launch Profile Selector

A form-based session creator that turns prompt templates into a guided workflow.
Accessed from the left nav (⚡) or from the Orchestrator panel's [⚡ New] button.

### Data Bindings

| UI Element | Data Source | Refresh |
|-----------|-------------|---------|
| Workspace dropdown | `config.yaml → workspaces[]` | On config reload |
| Profile dropdown | Workspace's `allowed_profiles[]` | On workspace change |
| Model dropdown | Profile's `model.default` + provider models | On profile change |
| Recipe list | Static (defined in plugin) + user-saved templates | On demand |
| Provider status indicator | Health check poll | 60s |

### Component Skeleton

```
┌──────────────────────────────────────────────────────────────┐
│ ⚡ QUICK LAUNCH                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌─ Step 1: Select Context ──────────────────────────────┐   │
│ │                                                        │   │
│ │  Workspace:  [Agentic Swarm Ops          ▾]           │   │
│ │  Profile:    [orchestrator               ▾]  🟢       │   │
│ │  Model:      [deepseek-v4-pro            ▾]  🟢       │   │
│ │  Channel:    [Gateway (telegram)         ▾]           │   │
│ │                                                        │   │
│ │  Provider status: deepseek 🟢 | openai-codex 🟢       │   │
│ │                    ollama-hermes 🟢 | ollama-qwen 🟢   │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌─ Step 2: Choose Recipe ───────────────────────────────┐   │
│ │                                                        │   │
│ │  ○ Quick code fix              Jules                  │   │
│ │  ○ Research question           AGY                    │   │
│ │  ○ Code review                 Codex                  │   │
│ │  ● Multi-agent pipeline        Hermes                 │   │
│ │  ○ Deploy supervision          Hermes                 │   │
│ │  ○ Incident response           Hermes                 │   │
│ │  ○ Documentation               Hermes                 │   │
│ │  ○ Custom orchestration        Any                    │   │
│ │                                                        │   │
│ │  ───── Saved Templates ─────                           │   │
│ │  ○ "Competitor Pricing Pipeline"  AGY→Jules→Codex     │   │
│ │  ○ "Weekly Cron Health Report"    hermeslocal         │   │
│ │  ○ "SEO Audit Combo"              AGY research        │   │
│ │                                                        │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌─ Step 3: Configure ───────────────────────────────────┐   │
│ │                                                        │   │
│ │  Goal:                                                 │   │
│ │  ┌──────────────────────────────────────────────────┐ │   │
│ │  │ Design the Agent Manager plugin dashboard UI     │ │   │
│ │  └──────────────────────────────────────────────────┘ │   │
│ │                                                        │   │
│ │  ───── Multi-Agent Pipeline ─────                      │   │
│ │                                                        │   │
│ │  Phase 1: Research (AGY)   ☑ Enabled                  │   │
│ │  Phase 2: Implement        ☐ Skip (design only)       │   │
│ │  Phase 3: Review           ☐ Skip (design only)       │   │
│ │  Phase 4: Verify           ☑ Enabled                  │   │
│ │                                                        │   │
│ │  ⏱️ Timeout:  [45 min ▾]    ☐ Run phases in parallel    │   │
│ │                                                        │   │
│ │  ───── Verification (auto-generated) ─────             │   │
│ │  ☑ file_exists: docs/swarm/agent-manager-plugin*.md   │   │
│ │  ☑ syntax_valid: markdown                             │   │
│ │  ☑ matches_spec: all 5 plugin areas covered           │   │
│ │  ☑ secrets_clean: no credentials in output            │   │
│ │                                                        │   │
│ │  ───── Advanced ─────                                  │   │
│ │  Escalation:  [2 retries → Slack #eng-alerts ▾]        │   │
│ │  Context links:  [+ Add]                               │   │
│ │  Files to modify:  [+ Add]                             │   │
│ │                                                        │   │
│ └────────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              🚀  LAUNCH ORCHESTRATION                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Save as Template...]  [Preview Prompt YAML]  [Cancel]     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Quick-Launch State Machine

```
[Select Workspace] → [Select Recipe] → [Configure]
                                            │
                                     [Preview YAML]
                                            │
                                     ┌──────▼──────┐
                                     │   LAUNCH    │
                                     └──────┬──────┘
                                            │
                              ┌─────────────┼─────────────┐
                              │             │             │
                         success      validation      provider
                              │         failure        down
                              ▼             │             │
                    ┌──────────────┐        ▼             ▼
                    │ Session live │  [Fix fields]  [Try fallback
                    │ in Orch Area │                 or wait]
                    └──────────────┘
```

---

## Panel 6: Inventory / Registry View

Full registry browser showing profiles, models, providers, and agent wrappers.
Accessed from the left nav (📦) or as a section within the center panel.

### Sub-Tabs

```
┌──────────────────────────────────────────────────────────────┐
│ 📦 INVENTORY                    [Profiles|Models|Providers|Wrappers]│
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [Profiles tab active]                                      │
│                                                              │
│  Profile            Status    Model            Context      │
│  ─────────────────  ────────  ───────────────  ───────────  │
│  orchestrator       🟢 Active deepseek-v4-pro  1,000,000    │
│  hermeslocal        🟢 Active hermes3:70b      65,536       │
│  qwenlocal          🟢 Active qwen3:32b        65,536       │
│  agy                🟢 Active varies           —            │
│  codex              🟡 Rate-ltd gpt-5.5       272,000       │
│  jules              🟢 Active N/A              —            │
│                                                              │
│  [Click profile for detail: config path, skills, workspaces, │
│   session history, success rate]                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

For the full inventory data model and taxonomy, see
[agent-registry-design.md](./agent-registry-design.md) (GRO-36).

---

## Navigation & Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Switch to Orchestrator panel |
| `2` | Switch to Workspace Tree |
| `3` | Switch to Inventory |
| `4` | Switch to Live Stream (maximized) |
| `5` | Switch to Quick Launch |
| `/` | Focus global search |
| `n` | New orchestration (opens Quick Launch) |
| `Esc` | Close detail panel / deselect |
| `j` / `k` | Navigate down/up in lists |
| `Enter` | Open selected item |
| `Space` | Toggle expand/collapse |
| `r` | Refresh current view |
| `p` | Pause/resume live stream |
| `Ctrl+[` | Collapse left nav to icons only |
| `Ctrl+]` | Expand left nav |
| `Ctrl+\` | Toggle right panel |

---

## Responsive Behavior

| Viewport | Layout |
|----------|--------|
| **Desktop (1200px+)** | Full 3-column: Left nav (200px) + Center (flex) + Right stream (400px) |
| **Tablet (768–1199px)** | 2-column: Left nav (60px icons) + Center (flex). Right panel is a slide-over drawer |
| **Mobile (<768px)** | Single column: Bottom tab bar for nav. Panels stack vertically. Stream is a bottom sheet |

---

## Dark Theme (Cyberpunk)

The plugin inherits the existing dashboard theme (`theme: cyberpunk` from config.yaml):

- **Background:** Deep navy/black (#0a0a1a)
- **Panels:** Dark with subtle neon borders (#1a1a2e, border #00ff8855)
- **Text:** High-contrast cyan-white (#e0f0ff)
- **Accents:** Neon green (success), magenta (active), amber (warning), red (error)
- **Font:** Monospace for data, sans-serif for labels
- **Animations:** Subtle pulse on active sessions, fade transitions between panels
- **Status dots:** Glowing halos on 🟢🟡🔴 indicators

---

## Cross-References

- **Agent Manager Architecture** — [agent-manager-architecture.md](./agent-manager-architecture.md) (GRO-34) —
  the information architecture this plugin renders
- **Agent Registry Design** — [agent-registry-design.md](./agent-registry-design.md) (GRO-36) —
  the data model for the Inventory panel
- **Swarm Workflow** — [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md) — how agents work together
- **Hermes Prompt Template** — [hermes-prompt-template.md](./hermes-prompt-template.md) —
  the YAML structure Quick-Launch generates
- **Handoff Contracts** — [handoff-contracts.md](./handoff-contracts.md) —
  output formats displayed in session detail
- **Context Window Pruning** — [context-window-pruning.md](./context-window-pruning.md) —
  per-model context budgets shown in inventory
