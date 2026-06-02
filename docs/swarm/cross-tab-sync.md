# Cross-Tab Synchronization for Dashboard (GRO-61)

## Problem Statement

Operators frequently open multiple browser tabs pointing at the same swarm dashboard.
Each tab independently initializes a session, connects to the PTY stream, and renders
widgets. This creates several failure modes:

- **Double PTY ownership:** Two tabs both attempt `pty=true` connections to the same
  orchestrator session. The second handshake steals the PTY, breaking the first tab's
  I/O mid-operation.
- **Divergent state:** Each tab builds its own in-memory task tree from the stream.
  When a task completes in tab A but tab B hasn't processed the frame yet, the operator
  sees conflicting status.
- **Write conflicts:** Both tabs send commands through the same session, interleaving
  stdin in unpredictable order.
- **Resource waste:** N tabs × (SSE connection + render loop + state store) scales
  linearly with no benefit.

The platform needs a **single-writer, multi-reader** model: one tab owns the session;
all others are passive viewers.

---

## Design

### Architecture Overview

```
┌───────────────────────────────────────────────────────────┐
│                     Same-Origin Tabs                       │
│                                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │  Tab A   │    │  Tab B   │    │  Tab C   │            │
│  │ (LEADER) │    │ (VIEWER) │    │ (VIEWER) │            │
│  │  Owns    │    │  Reads   │    │  Reads   │            │
│  │  PTY +   │    │  shared  │    │  shared  │            │
│  │  SSE     │    │  state   │    │  state   │            │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘            │
│       │               │               │                  │
│       └───────┬───────┴───────┬───────┘                  │
│               │               │                          │
│       ┌───────┴───────┐ ┌─────┴──────────┐              │
│       │BroadcastChannel│ │ localStorage   │              │
│       │ (real-time     │ │ (durable state │              │
│       │  coordination) │ │  + fallback)   │              │
│       └───────────────┘ └────────────────┘              │
└───────────────────────────────────────────────────────────┘
```

### 1. BroadcastChannel — Real-Time Tab Coordination

The [`BroadcastChannel` API](https://developer.mozilla.org/en-US/docs/Web/API/BroadcastChannel)
provides same-origin pub/sub between tabs, windows, and iframes. No server involvement.
All modern browsers support it. Messages are delivered in real time (~1–5ms intra-tab).

```typescript
// Channel name scoped to the session being viewed
const channelName = `swarm:dashboard:${sessionId}`;
const channel = new BroadcastChannel(channelName);
```

**Message types:**

| Type | Direction | Payload | Purpose |
|------|-----------|---------|---------|
| `LEADER_HEARTBEAT` | Leader → Viewers | `{tabId, sessionId, seq}` | Proves leader is alive; every 2s |
| `LEADER_ELECTION` | Candidate → All | `{tabId, sessionId, priority}` | Bully-algorithm election request |
| `LEADER_ACK` | Electee → All | `{tabId, sessionId}` | Declares victory |
| `LEADER_ABDICATE` | Leader → All | `{tabId, reason}` | Graceful handoff (tab close, error) |
| `STATE_DELTA` | Leader → Viewers | `{path, value, version}` | Incremental state update |
| `VIEWER_HELLO` | Viewer → Leader | `{tabId}` | New viewer requesting full state sync |
| `VIEWER_GOODBYE` | Viewer → All | `{tabId}` | Tab closing |
| `WRITE_REQUEST` | Viewer → Leader | `{tabId, command}` | Viewer wants to send a command |
| `WRITE_ACK` | Leader → Viewer | `{tabId, ok, error?}` | Command accepted or rejected |

### 2. Leader Election Protocol

Election uses a simplified Bully algorithm on the `BroadcastChannel`:

```typescript
interface LeaderElectionState {
  tabId: string;          // crypto.randomUUID() generated on tab open
  sessionId: string;      // the PTY/session being coordinated
  isLeader: boolean;
  leaderTabId: string | null;
  electionInProgress: boolean;
  lastHeartbeat: number;  // Date.now()
  heartbeatInterval: number; // 2000ms
  heartbeatTimeout: number;  // 6000ms (3× interval)
}
```

**Election rules:**

1. On tab open, generate a unique `tabId` and join the `BroadcastChannel`.
2. Send `VIEWER_HELLO`. If no `LEADER_HEARTBEAT` arrives within 500ms, initiate election.
3. To initiate election: broadcast `LEADER_ELECTION {tabId, priority}` where `priority`
   is `Date.now()` (newer tabs have higher priority — tiebreaker is lexicographic `tabId`).
4. Wait 300ms. If any election message with higher priority arrives, stand down.
5. If no higher priority is seen, broadcast `LEADER_ACK` and become leader.
6. Leader starts the heartbeat timer. Viewers start the heartbeat timeout watch.
7. If a viewer misses 3 consecutive heartbeats (6s), trigger re-election.

**Conflict resolution — two tabs try same session:**

```
Tab A opens → VIEWER_HELLO → no heartbeat → LEADER_ELECTION(priority=1000)
Tab B opens → VIEWER_HELLO → no heartbeat → LEADER_ELECTION(priority=1001)
Tab A sees Tab B's priority is higher → stands down
Tab B broadcasts LEADER_ACK → becomes leader
Tab A transitions to viewer mode
```

### 3. Shared State via localStorage

`BroadcastChannel` messages are ephemeral — a late-joining tab misses earlier deltas.
`localStorage` provides the durable state backbone:

```typescript
const STATE_KEY = `swarm:state:${sessionId}`;
const STATE_VERSION_KEY = `swarm:state:${sessionId}:version`;

interface SharedDashboardState {
  version: number;                // Monotonic counter
  leaderTabId: string | null;
  session: {
    id: string;
    status: 'connected' | 'disconnected' | 'error';
    connectedAt: string;          // ISO-8601
  };
  tasks: Record<string, TaskNode>; // taskId → current task state
  stream: {
    lastEventId: string;          // Last SSE event ID processed
    lastEventTime: string;        // ISO-8601
  };
  ui: {
    activeView: string;           // 'overview' | 'task-detail' | 'logs'
    focusedTaskId: string | null;
    logFilters: LogFilter[];
  };
}
```

**Write rules:**
- Only the leader writes to `localStorage`. Viewers read-only.
- Every write increments `version`. Viewers poll `version` to detect changes.
- On `VIEWER_HELLO`, leader does a full state dump to localStorage so the viewer can hydrate.

**Conflict prevention:**
- Before writing, leader checks `localStorage` version matches its in-memory version.
- If a stale write is detected (version mismatch), the leader re-reads and merges.
- `localStorage` `"storage"` event fires in all other tabs when any tab writes — used
  as a secondary notification channel for browsers where `BroadcastChannel` is throttled
  in background tabs.

### 4. UX: "Session Active in Another Tab"

**Leader tab UI:**
- Subtle green indicator: "🟢 Owning session — 2 viewer tabs connected"
- Full control: PTY input, task actions (retry, cancel, escalate)

**Viewer tab UI:**
- Prominent banner (non-blocking, dismissible):

```
┌────────────────────────────────────────────────────────────┐
│ ⚠️  This session is active in another tab                  │
│                                                            │
│  Tab "Chrome #3" owns this session. You are in view-only   │
│  mode. To take control, close the leader tab or click      │
│  [Take Control].                                          │
└────────────────────────────────────────────────────────────┘
```

- All input controls are disabled (greyed out) with tooltip explanations.
- "Take Control" button triggers graceful leader abdication: sends `LEADER_ABDICATE`,
  waits for leader to release, then initiates election.
- If the leader tab closes (beforeunload sends `LEADER_ABDICATE` + clears leader
  entry from localStorage), viewers auto-detect the gap and trigger election after
  3 missed heartbeats.
- The new leader banner changes to: "🟢 You now own this session."

**Edge case — user closes laptop (both tabs suspend):**
- On wake, both tabs detect heartbeat timeout simultaneously.
- Election runs as normal; the tab with the higher priority (later wake timestamp) wins.
- No data loss — the leader reconnects to the SSE stream using `Last-Event-ID` and
  replays missed events.

### 5. Fallback: No BroadcastChannel Support

For environments where `BroadcastChannel` isn't available (older browsers, some
WebView implementations), the system degrades to a localStorage-only coordination
model:

```typescript
// Fallback: use localStorage "storage" event as message bus
const FALLBACK_KEY = `swarm:channel:${sessionId}`;

function sendFallback(msg: ChannelMessage): void {
  localStorage.setItem(FALLBACK_KEY, JSON.stringify({
    ...msg,
    _ts: Date.now(),
    _nonce: Math.random().toString(36).slice(2)
  }));
  // Immediately clear so next message triggers the event
  localStorage.removeItem(FALLBACK_KEY);
}

window.addEventListener('storage', (e) => {
  if (e.key === FALLBACK_KEY && e.newValue) {
    const msg = JSON.parse(e.newValue);
    if (msg.tabId !== myTabId) handleMessage(msg);
  }
});
```

**Limitations of fallback mode:**
- Higher latency (storage events are throttled to ~50ms minimum in some browsers)
- No guarantee of delivery order under rapid writes
- Election timeout increased to 1500ms to account for latency

When fallback is active, a small indicator appears: "⚡ Sync mode: localStorage (slower)"

---

## Implementation Checklist

- [ ] Generate `tabId` via `crypto.randomUUID()` on dashboard mount
- [ ] Create `BroadcastChannel` scoped to `swarm:dashboard:${sessionId}`
- [ ] Implement leader election state machine (viewer → candidate → leader)
- [ ] Leader: 2s heartbeat interval, broadcast `LEADER_HEARTBEAT`
- [ ] Viewers: 6s heartbeat timeout (3 misses), trigger re-election
- [ ] Leader: write shared state to `localStorage` on every state change
- [ ] Viewers: hydrate from `localStorage` on mount, poll `version`
- [ ] `beforeunload` handler: send `LEADER_ABDICATE` if leader, `VIEWER_GOODBYE` if viewer
- [ ] Viewer UI: banner + disabled controls + "Take Control" button
- [ ] Leader UI: connected viewer count
- [ ] Fallback localStorage-only mode detection and degraded UX indicator
- [ ] Wake-from-suspend re-election and SSE replay via `Last-Event-ID`

---

## Cross-References

- [Multiplexed SSE Streams (GRO-66)](./multiplexed-sse-streams.md) — the real-time data layer
  that the leader tab ingests and redistributes to viewers
- [Context Window Pruning (GRO-58)](./context-window-pruning.md) — session lifecycle management
- [SWARM-WORKFLOW.md](../SWARM-WORKFLOW.md) — overall architecture this dashboard monitors
