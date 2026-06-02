# Visible Terminal Workflow (GRO-19)

When to use VS Code terminal tabs vs MCP vs non-interactive CLI, how Michael can watch
agents work in real time, terminal multiplexing strategies, and session visibility patterns.

---

## Terminal Mode Decision Matrix

Three execution modes are available for agent work. Choose based on the interaction
requirements of the task.

| Mode | What It Is | Best For | Michael Can Watch? |
|------|-----------|----------|-------------------|
| **VS Code Terminal Tab** | Agent runs in a visible terminal pane inside VS Code | Interactive debugging, exploration, pair-programming sessions | ✅ Yes — real-time, full visibility |
| **MCP (Model Context Protocol)** | Agent calls tools via structured protocol (no visible terminal) | Production automation, batch tasks, cron-driven work | ❌ No — output via logs/Linear only |
| **Non-Interactive CLI** | Agent runs a single command, returns output, exits | Health checks, verification scripts, git operations | ⚠️ Partial — output captured, not real-time |

---

## When to Use Each Mode

### VS Code Terminal Tabs — Interactive Visibility

**Use when:**
- Michael wants to watch the agent's reasoning in real time
- The task involves exploration or debugging (uncertain path)
- Pair-programming or collaborative problem solving
- Teaching/demonstrating — Michael learns from watching the agent
- High-stakes operations where human oversight is desired
- Tasks where the agent may need interactive input

**How it works:**
1. Michael opens a terminal tab in VS Code
2. Launches agent with `pty=true` (pseudo-terminal mode for interactivity)
3. Agent output streams in real time — Michael sees every command and response
4. Michael can interrupt, redirect, or provide input at any point
5. Terminal history is preserved for review

**Example launch:**
```bash
# Interactive agent in VS Code terminal
hermes --profile orchestrator --pty "Debug the checkout API 500 error"
```

### MCP — Production Automation

**Use when:**
- Task is fully automated (cron-driven, label-driven)
- No human oversight needed (well-tested workflows)
- Batch operations (many tasks, parallel agents)
- Running on a headless server (no display)
- Standard code tasks, research tasks, reviews
- Task has clear success criteria and verification

**How it works:**
1. Router detects task (Linear label, cron trigger)
2. Dispatches to agent via MCP tool calls
3. Agent works without visible terminal — output captured in logs
4. Results posted to Linear, GitHub, or filesystem
5. Michael checks results asynchronously

**Example (no visible terminal):**
```
Linear: [agent:jules] → Jules Session Manager detects → dispatches → PR opened
Michael checks PR when notified (no live watching needed)
```

### Non-Interactive CLI — One-Shot Commands

**Use when:**
- Quick verification or health check
- Git operations (branch discipline, status)
- Script execution with known output
- Log tailing, metrics queries
- Configuration validation

**How it works:**
1. Command executed in foreground or background
2. Output captured and returned
3. No interactivity — fire and forget

---

## How Michael Watches Agents Work in Real Time

### Pattern 1: Direct Terminal Watch

Michael opens a VS Code terminal tab and launches the agent interactively.

```
┌─────────────────────────────────────────────────────────┐
│  VS Code Terminal Tab                                   │
│                                                         │
│  $ hermes --pty "Investigate slow API endpoints"        │
│                                                         │
│  Agent: I'll start by checking the API metrics...        │
│  $ curl -s metrics-api:9090/api/v1/query?...            │
│  { "latency_p95": 2.3, "latency_p99": 8.7 }            │
│                                                         │
│  Agent: The p99 latency is 8.7s — let me check which    │
│  endpoint is slow...                                     │
│  $ curl -s metrics-api:9090/api/v1/query?...            │
│  { "checkout_api": { "p99": 12.4 }, ... }               │
│                                                         │
│  Agent: Checkout API is the culprit. Let me look at     │
│  recent deploys...                                       │
│                                                         │
│  ← Michael watches this unfold in real time             │
│  ← Can type input or Ctrl+C at any point                │
└─────────────────────────────────────────────────────────┘
```

### Pattern 2: tmux Shared Session

Michael and the agent share a tmux session — Michael attaches to watch.

```bash
# Agent creates named tmux session
tmux new-session -d -s "agent-task-GRO-100"

# Michael attaches to watch
tmux attach-session -t "agent-task-GRO-100"

# Both see the same terminal output
# Michael can type in the same session (shared control)
```

### Pattern 3: Background + Log Tail

Agent runs in background with `notify_on_complete=true`. Michael tails the log.

```bash
# Terminal 1: Michael tails the log
tail -f /tmp/hermes-session-ABC123.log

# Terminal 2 (or background): Agent runs
hermes --profile orchestrator -z "Task GRO-100" &

# Michael sees output streaming in terminal 1
# Gets notified when agent completes
```

### Pattern 4: Watch Patterns (Mid-Process Signals)

For long-running processes that never exit (servers), Michael sets watch patterns.

```bash
# Michael launches agent with watch pattern
hermes --profile orchestrator \
  --watch-patterns "Application startup complete" \
  --background \
  "Start the API server and run integration tests"

# Michael gets notified when server is ready
# Then hits the endpoint to verify
```

---

## Terminal Multiplexing Strategies

When multiple agents run simultaneously, use these patterns to organize terminals.

### Strategy 1: tmux Window-Per-Agent

Best for 2–4 concurrent agents with live watching.

```
tmux session: "swarm-ops"
├─ Window 0: "hermes-orch"  — Hermes orchestrator (control center)
├─ Window 1: "jules-GRO-100" — Jules working on task GRO-100
├─ Window 2: "agy-GRO-101"   — AGY researching task GRO-101
├─ Window 3: "codex-review"  — Codex reviewing PR #42
└─ Window 4: "monitor"       — htop / watch commands / log tails
```

```bash
# Create the session
tmux new-session -d -s "swarm-ops" -n "hermes-orch"
tmux new-window -t "swarm-ops" -n "jules-GRO-100"
tmux new-window -t "swarm-ops" -n "agy-GRO-101"
tmux new-window -t "swarm-ops" -n "codex-review"
tmux new-window -t "swarm-ops" -n "monitor"

# Michael attaches and switches between windows
tmux attach-session -t "swarm-ops"
```

### Strategy 2: VS Code Split Terminals

Best for small-scale concurrent work within VS Code.

```
┌──────────────────────┬──────────────────────┐
│  Terminal 1          │  Terminal 2          │
│  Hermes orchestrator │  Jules session       │
│                      │                      │
│  $ hermes -z         │  $ tail -f           │
│  "Coordinate GRO-99" │  /tmp/jules.log      │
│                      │                      │
├──────────────────────┴──────────────────────┤
│  Terminal 3                                  │
│  $ watch -n 5 'cat /tmp/session-tracker.json'│
└──────────────────────────────────────────────┘
```

### Strategy 3: Background + Poll (Lightweight)

Best for fully automated batch operations where Michael checks occasionally.

```bash
# Dispatch all agents in background
hermes --profile orchestrator -z "Task GRO-100: code" --background --notify &
hermes --profile orchestrator -z "Task GRO-101: research" --background --notify &
hermes --profile orchestrator -z "Task GRO-102: review" --background --notify &

# Check progress
hermes process list
hermes process poll --session-id SESSION_ID

# Wait for all
hermes process wait --session-id SESSION_ID_1 --timeout 600
```

### Strategy 4: Orchestrator-as-Dashboard

Hermes orchestrator itself becomes the single pane of glass.

```bash
# Hermes manages all sub-agents and reports progress
hermes -z "
Coordinate three parallel tasks:
1. Jules: GRO-100 (code)
2. AGY: GRO-101 (research)
3. Codex: GRO-102 (review)

Report progress every 5 minutes.
Notify on each completion.
"
```

---

## Session Visibility Patterns

### Full Visibility (Michael Watches Everything)

- Agent runs in VS Code terminal tab with `pty=true`
- Every command, response, and tool call is visible
- Michael can intervene at any point
- **Use for:** Debugging, exploration, high-stakes operations, learning

### Checkpoint Visibility (Michael Checks Milestones)

- Agent runs in background with `notify_on_complete=true`
- Michael checks progress at defined milestones
- Progress updates posted to Linear or Slack
- **Use for:** Standard code tasks, research, reviews

### Async Visibility (Michael Checks When Done)

- Agent runs fully automated (MCP, cron)
- Results posted to Linear/GitHub when complete
- Michael reviews asynchronously
- **Use for:** Batch operations, routine tasks, overnight runs

### Audit Visibility (Logs Only)

- Agent runs non-interactively
- Full logs captured to file
- Michael checks logs only if something went wrong
- **Use for:** Health checks, verification scripts, maintenance

---

## Real-Time Monitoring Commands

### Check What Agents Are Running

```bash
# List all background processes
hermes process list

# Check Jules session tracker
cat /tmp/jules-session-tracker.json | jq .

# Check AGY research progress
cat /home/ubuntu/work/hd-platform/output/research/.agy-progress.json

# Watch session tracker live
watch -n 5 'cat /tmp/jules-session-tracker.json | jq .daily_stats'
```

### View Agent Output

```bash
# Full log of a session
hermes process log --session-id ABC123

# Tail the last 50 lines
hermes process log --session-id ABC123 --offset -50

# Poll for new output
hermes process poll --session-id ABC123

# Wait for completion (blocking)
hermes process wait --session-id ABC123 --timeout 600
```

### Intervene in Running Sessions

```bash
# Send input to interactive agent
hermes process submit --session-id ABC123 --data "Try a different approach"

# Kill a stuck session
hermes process kill --session-id ABC123

# Close stdin (signal EOF to agent)
hermes process close --session-id ABC123
```

---

## Recommended Setup for Michael

### Daily Driver: VS Code Terminal Tab

For most interactive work where Michael wants visibility:

```bash
# Open VS Code terminal (Ctrl+`)
# Launch orchestrator interactively
hermes --profile orchestrator --pty "What should we work on today?"
```

### Heavy Batch Day: Background + Monitor

When pushing many tasks through the swarm:

```bash
# Terminal 1: Orchestrator dispatches
hermes -z "Dispatch batch: GRO-103 through GRO-110" --background --notify &

# Terminal 2: Live monitoring dashboard
watch -n 10 '
  echo "=== Jules ===" 
  cat /tmp/jules-session-tracker.json | jq .daily_stats
  echo "=== Processes ==="
  hermes process list
'
```

### Overnight: Fully Automated

When Michael is offline:

```bash
# Cron handles dispatch via Linear labels
# Michael checks results in the morning:
# 1. Open Linear → check completed tasks
# 2. Open GitHub → check PRs opened/merged
# 3. Check #eng-alerts Slack for escalations
```

---

## Visibility for Each Agent

| Agent | Default Mode | Watch Option | Notes |
|-------|-------------|-------------|-------|
| **Hermes** | MCP (production) | VS Code terminal with `pty=true` | Orchestrator can run interactively or automated |
| **Jules** | MCP (cron dispatch) | Not directly watchable | Works on remote GitHub state; output via Linear/PRs |
| **AGY** | MCP + local file writes | Can watch file outputs appear | Research results written to disk; `tail -f` the output dir |
| **Codex** | MCP (API-based) | Not directly watchable | Review results posted to Linear; Michael checks there |

---

## Cross-References

- Operator quickstart: [operator-quickstart](./operator-quickstart.md)
- Swarm workflow architecture: [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md)
- Agent capabilities: [lane-capabilities](./lane-capabilities.md)
- Jules evaluation: [jules-cli-evaluation](./jules-cli-evaluation.md)
