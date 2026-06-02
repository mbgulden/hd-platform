# Multiplexed SSE Streams for Swarm Monitoring (GRO-66)

## Problem Statement

The current swarm monitoring sends a single SSE (Server-Sent Events) stream per session.
When an orchestrator delegates to multiple subagents in parallel — e.g., AGY researching
competitors while Jules builds a data pipeline and Codex audits a third task — the operator
has no way to watch all three task streams simultaneously in one view.

Current workarounds and their failures:

| Workaround | Problem |
|-----------|---------|
| Open 3 browser tabs, one per task | Cross-tab sync (GRO-61), resource waste, context fragmentation |
| Single merged stream | Impossible to filter per-task, interleaved frames confuse parsers |
| Polling REST endpoints per task | High latency (1s+), misses real-time events, adds server load |
| Scroll through interleaved log | Operator misses critical errors buried in other task output |

Operators need a **single SSE endpoint** that carries **multiple logical task streams**
with client-side demuxing into a multi-column live log view.

---

## Design

### 1. Multiplexed Stream Protocol

The SSE endpoint at `GET /api/sessions/{sessionId}/stream` accepts an optional query
parameter `tasks`:

```
GET /api/sessions/{sessionId}/stream?tasks=all          # All tasks (default)
GET /api/sessions/{sessionId}/stream?tasks=gro-61,gro-66  # Specific task IDs only
```

Each SSE event carries a `task-id` field in its metadata, plus the standard SSE fields:

```
id: <monotonic-event-id>
event: <event-type>
data: <json-payload>
:task-id <task-id>          # ← multiplexing key
:task-state <state>         # ← optional, for quick client filtering
:parent-task <parent-id>    # ← optional, for subtask hierarchy
:timestamp <iso-8601>       # ← server-side timestamp
```

**Event types:**

| event | Semantics | Example |
|-------|-----------|---------|
| `task:created` | New task dispatched to an agent lane | `{"taskId":"gro-66","agent":"hermes","lane":"orchestration"}` |
| `task:progress` | Agent heartbeat or intermediate output | `{"taskId":"gro-66","message":"Compiling design doc...","progress":0.4}` |
| `task:log` | A line of agent output (stdout, log line) | `{"taskId":"gro-66","stream":"stdout","line":"✓ Section 2 complete"}` |
| `task:artifact` | File or artifact produced | `{"taskId":"gro-66","path":"docs/swarm/multiplexed-sse-streams.md","size":12400}` |
| `task:error` | Non-fatal error or warning | `{"taskId":"gro-66","severity":"warn","message":"Retry 1/3"}` |
| `task:completed` | Task finished (success or failure) | `{"taskId":"gro-66","status":"completed","handoff":{...}}` |
| `task:heartbeat` | Keep-alive per task (30s period) | `{"taskId":"gro-66"}` |
| `session:metadata` | Global session-level event | `{"activeTasks":3,"completedTasks":7,"uptime":"2h14m"}` |
| `session:error` | Session-level error | `{"message":"PTY disconnected","code":"PTY_HUNG_UP"}` |
| `stream:eos` | Server-side stream end (all tasks done) | `{"totalTasks":10,"failedTasks":0}` |

### 2. Namespacing and Metadata Frames

Every task gets a `task-id` namespace derived from the Linear issue key or GRO number:

```typescript
type TaskId = string; // "gro-61", "gro-66", "gro-67"

interface TaskStreamMetadata {
  taskId: TaskId;
  agent: 'jules' | 'agy' | 'hermes' | 'codex' | 'qwen';
  lane: 'code' | 'research' | 'orchestration' | 'review';
  parentTaskId?: TaskId;        // For subtask hierarchies
  startedAt: string;            // ISO-8601
  estimatedDuration?: number;   // seconds, from historical data
  priority: 'critical' | 'high' | 'normal' | 'low';
}
```

The server prepends a `task:created` event when a new task enters the stream. The client
uses this to allocate a new column/panel. If a task ends (completed or error), the server
sends a `task:completed` event and stops multiplexing that task ID.

**Late-joining clients** (page refresh, new viewer tab from GRO-61) receive a
**stream replay** starting from the `Last-Event-ID` header they provide. The server
replays all events since that ID across all active tasks.

### 3. Server-Side Multiplexer

The server maintains one SSE response per session and fans in events from multiple
PTY/agent backends:

```typescript
// Server — simplified
class SessionStreamMultiplexer {
  private tasks: Map<TaskId, AsyncIterable<SwarmEvent>> = new Map();
  private clients: Set<ServerSentEventResponse> = new Set();
  private eventSeq: number = 0;

  registerTask(taskId: TaskId, eventStream: AsyncIterable<SwarmEvent>): void {
    this.tasks.set(taskId, eventStream);
    this.broadcast({
      event: 'task:created',
      taskId,
      data: this.taskMeta.get(taskId)
    });
    // Start consuming the async iterable, broadcasting each event
    this.consumeTask(taskId, eventStream);
  }

  private async consumeTask(
    taskId: TaskId,
    stream: AsyncIterable<SwarmEvent>
  ): Promise<void> {
    for await (const event of stream) {
      this.broadcast({ ...event, taskId, seq: ++this.eventSeq });
    }
    // Stream exhausted → task done
    this.broadcast({
      event: 'task:completed',
      taskId,
      data: this.taskResults.get(taskId),
      seq: ++this.eventSeq
    });
    this.tasks.delete(taskId);
    if (this.tasks.size === 0) {
      this.broadcast({ event: 'stream:eos' });
    }
  }

  private broadcast(envelope: BroadcastEnvelope): void {
    for (const client of this.clients) {
      client.writeSSE(envelope);
    }
  }
}
```

**Per-task heartbeat:** If a task produces no events for 30 seconds, the multiplexer
injects a `task:heartbeat` event to keep the SSE connection alive and signal that the
task hasn't stalled silently.

**Backpressure handling:**
- Each client has a high-water mark (64KB). If the write buffer exceeds this, the
  multiplexer drops non-critical events (`task:log` lines) and sends a
  `session:metadata` event with `backpressure: true` so the client can throttle.
- When backpressure clears, the server sends a batch replay of skipped `task:log` events
  from its ring buffer (last 500 log lines per task).

### 4. Client-Side Stream Demuxer

```typescript
// Client
class StreamDemuxer {
  private tasks: Map<TaskId, TaskPanel> = new Map();
  private eventSource: EventSource;

  constructor(sessionId: string, taskFilter?: TaskId[]) {
    const params = taskFilter?.length
      ? `?tasks=${taskFilter.join(',')}`
      : '?tasks=all';
    this.eventSource = new EventSource(
      `/api/sessions/${sessionId}/stream${params}`
    );

    this.eventSource.addEventListener('task:created', (e) => {
      const data = JSON.parse(e.data);
      this.tasks.set(data.taskId, new TaskPanel(data));
      dashboard.addColumn(data.taskId);
    });

    // Generic handler for all event types
    const eventTypes = [
      'task:progress', 'task:log', 'task:artifact',
      'task:error', 'task:completed', 'task:heartbeat'
    ];
    for (const type of eventTypes) {
      this.eventSource.addEventListener(type, (e: MessageEvent) => {
        const taskId = (e as any).taskId; // from SSE comment field
        const data = JSON.parse(e.data);
        this.tasks.get(taskId)?.handleEvent(type, data);
      });
    }
  }
}
```

### 5. Visual Design: Multi-Column Live Log View

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Swarm Dashboard — Session #47 (active 2h14m)                   [3 active]  │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│  GRO-61 (Hermes) │  GRO-66 (Hermes) │  GRO-67 (AGY)    │  Completed Tasks   │
│  Cross-Tab Sync  │  SSE Streams     │  Memory Tiering  │                    │
│  ⬤ In Progress   │  ⬤ In Progress   │  ◉ Researching   │  ✓ GRO-60  1:23pm  │
│                  │                  │                  │  ✓ GRO-58  12:47pm │
│  ▶ Analyzing     │  ▶ Writing SSE   │  ▶ Searching     │  ✓ GRO-55  11:02am │
│    BroadcastCh   │    protocol      │    daily-memory  │                    │
│    annel API     │    spec          │    -journal      │  ✗ GRO-52  10:11am │
│                  │                  │                  │    (PR rejected)   │
│  ✓ Section 1     │  ✓ Event types   │  ▶ Reading       │                    │
│    complete      │    defined       │    context-      │  ➤ Collapsed       │
│                  │                  │    window-       │    (5 more)        │
│  ▶ Section 2     │  ▶ Writing       │    pruning.md    │                    │
│    Leader        │    server-side   │                  │                    │
│    election      │    multiplexer   │  ⚠️ Retry 1/3    │                    │
│                  │    code          │    researching   │                    │
│                  │                  │    compression   │                    │
├──────────────────┴──────────────────┴──────────────────┴────────────────────┤
│  [Filter: All] [Auto-scroll ✓] [Wrap lines] [Dark mode]   Log lines: 1,247  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Column behavior:**
- Each active task gets a fixed-width column (min 320px, flex-grow equal).
- Columns auto-arrange in a horizontal scrollable container when >3 tasks are active.
- Completed and errored tasks stay visible for 60 seconds, then collapse into the
  "Completed Tasks" sidebar panel.
- Clicking a completed task expands its full log in a modal/drawer.

**Log line rendering:**
- `task:log` lines render as monospaced text in the column, color-coded by stream:
  `stdout` = default, `stderr` = red.
- `task:error` lines get a ⚠️ prefix and yellow background.
- `task:artifact` lines get a 📎 prefix and are clickable (opens file or downloads).
- `task:progress` updates a thin progress bar at the top of the column.

**Filtering:**
- Top-level filter bar: "All" | task ID checkboxes | "Active only"
- Per-column filter: "stdout" | "stderr" | "Artifacts" | "Errors only"
- Search: typeahead filters all visible columns, highlights matches

### 6. Integration with Cross-Tab Sync (GRO-61)

The SSE connection is **owned by the leader tab only**. The demuxer runs in the leader
tab; viewer tabs receive state updates through the `BroadcastChannel`/`localStorage`
pipeline defined in [cross-tab-sync.md](./cross-tab-sync.md).

```
Leader Tab                   Viewer Tab
──────────                   ──────────
EventSource ──► Demuxer        Hydrate from
  (SSE)          │             localStorage
                 │                  ▲
                 ▼                  │
            TaskPanel[]       TaskPanel[] (read-only)
                 │                  ▲
                 ▼                  │
            BroadcastChannel ───────┘
            STATE_DELTA messages
```

This ensures only one SSE connection per session, regardless of how many tabs are open.

---

## Performance Budget

| Metric | Target | Rationale |
|--------|--------|-----------|
| Max concurrent task streams | 10 | Typical swarm max; beyond this, UI becomes unusable |
| SSE event latency | <100ms p95 | Real-time feel; JSON parse + DOM update |
| Bandwidth per task | ~2KB/s avg | Mostly log lines; bursts up to 50KB for artifacts |
| Server memory per session | <5MB | Ring buffers (500 lines × 10 tasks × 1KB) |
| Client DOM nodes per task column | <200 | Virtual scrolling for log lines beyond viewport |
| Reconnect replay window | 5 minutes | Ring buffer depth for late-joiners |

---

## Fallback: Polling Mode

When SSE is unavailable (corporate proxies stripping `text/event-stream`, restrictive
CSP policies), the client degrades to polling:

```
GET /api/sessions/{sessionId}/events?since={lastEventId}&tasks=gro-61,gro-66
```

- Poll interval: 2 seconds (adaptive: increases to 5s if no new events for 30s)
- Response: JSON array of events since `lastEventId`
- Max response size: 256KB; if exceeded, the server paginates and the client paginates
  with `?since={id}&page=2`
- UX indicator: "🔄 Polling mode — 2s refresh" instead of live SSE

---

## Implementation Checklist

- [ ] Server: `SessionStreamMultiplexer` with fan-in from multiple PTY/agent backends
- [ ] Server: SSE endpoint with `task-id` comment field on every event
- [ ] Server: `?tasks=` query filter to limit streamed tasks
- [ ] Server: `Last-Event-ID` replay support for reconnecting clients
- [ ] Server: per-task heartbeat injection (30s)
- [ ] Server: ring buffer for backpressure recovery (500 lines/task)
- [ ] Client: `StreamDemuxer` class with `Map<TaskId, TaskPanel>`
- [ ] Client: Multi-column layout with virtual scrolling per column
- [ ] Client: Log line color coding, filtering, and search
- [ ] Client: Completed-task collapse into sidebar (60s delay)
- [ ] Client: Polling fallback mode with adaptive interval
- [ ] Integration: Leader-only SSE connection per cross-tab-sync (GRO-61)

---

## Cross-References

- [Cross-Tab Synchronization (GRO-61)](./cross-tab-sync.md) — leader election determines
  which tab owns the single SSE connection
- [Handoff Contracts (GRO-84)](./handoff-contracts.md) — the `task:completed` event
  payload format aligns with the handoff contract schema
- [Context Window Pruning (GRO-58)](./context-window-pruning.md) — task streams contribute
  to session context growth; compression events are visible in the stream
