# PEP 668 Pipx Sandboxing for Plugin Runners (GRO-64)

> **Status:** Draft Recommendation  
> **Date:** 2026-05-29  
> **Author:** Hermes Agent (research subagent)  
> **Linear:** [GRO-64](https://linear.app/growthwebdev/issue/GRO-64/optimize-swarm-setup-pep-668-pipx-sandboxing-for-plugin-runners)

---

## 1. Problem Statement

Installing Hermes dashboard plugin backends and MCP server dependencies into a single shared virtual environment causes dependency conflicts. When Plugin A needs `requests>=2.31` and MCP Server B pins `requests<2.28`, both cannot coexist in one venv. As the plugin/MCP ecosystem grows, this becomes a blocker.

Additionally, Ubuntu 24.04 enforces **PEP 668** — the system Python (`/usr/bin/python3`) is marked `EXTERNALLY-MANAGED`, meaning `pip install` refuses to operate without `--break-system-packages`. Pipx was explicitly designed to address this by creating isolated venvs per application.

## 2. Current State

### 2.1 Hermes Agent Installation

| Component | Path | Notes |
|-----------|------|-------|
| pipx binary | `/usr/bin/pipx` | v1.4.3, system-installed |
| Hermes Agent venv | `/home/ubuntu/.local/share/pipx/venvs/hermes-agent` | Single shared venv for everything |
| Python | `/usr/bin/python3.12` | 3.12.3 |
| PEP 668 enforced? | No (venvs are exempt) | `EXTERNALLY-MANAGED` only applies to system site-packages |

### 2.2 Plugin Architecture

```
~/.hermes/
├── profiles/orchestrator/
│   ├── config.yaml          # Main config (MCP servers, profiles, etc.)
│   └── home/.local/share/pipx/  # Profile-level pipx home (EMPTY - unused)
├── plugins/                 # Dashboard plugins (JS frontends + Python API backends)
│   ├── hermes-plugin-vram-observability/
│   │   └── dashboard/
│   │       ├── plugin_api.py       # FastAPI router: imports subprocess, os, time, fastapi
│   │       └── dist/index.js       # Frontend bundle
│   ├── hermes-plugin-orchestrator-command-deck/
│   ├── hermes-plugin-mcp-controller/
│   ├── hermes-plugin-realtime-activity-stream/
│   ├── hermes-plugin-workspace-tree-navigator/
│   ├── hermes-plugin-swarm-manager/
│   ├── hermes-inbox/
│   └── kanban/
```

### 2.3 Plugin Dependency Analysis

All current dashboard plugin API backends (`plugin_api.py`) import from:
- **Standard library**: `subprocess`, `os`, `time`, `pathlib`, `json`, `base64`, `re`, `secrets`, `datetime`, `mimetypes`
- **From hermes-agent venv**: `fastapi` (APIRouter, File, Form, HTTPException, UploadFile, FileResponse), `pydantic` (BaseModel)

**No plugin currently has external dependencies beyond the hermes-agent venv.** However, this is by design constraint, not by feature sufficiency — plugin authors are limited to what's already in the hermes-agent venv.

### 2.4 MCP Server Configuration (from config.yaml)

```yaml
mcp_servers:
  gdrive:
    command: node
    args:
    - /home/ubuntu/work/local-gdrive-mcp/server.js
    enabled: true
```

Current MCP servers use node-based or binary-based transports. No Python-based MCP servers are configured, but the architecture supports them via `command` + `args`.

### 2.5 Built-in Plugins

Hermes ships with built-in plugins inside its own package:
```
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages/plugins/
├── context_engine/
├── disk-cleanup/
├── example-dashboard/
├── google_meet/
├── hermes-achievements/
├── image_gen/
├── kanban/
├── memory/
├── model-providers/
├── observability/
├── platforms/
├── spotify/
├── teams_pipeline/
├── video_gen/
└── web/
```

These are part of the `hermes-agent` pip package and share its venv automatically.

---

## 3. PEP 668 Background

**PEP 668** ("Marking Python base environments as 'externally managed'") was implemented in Python 3.11+ and adopted by Debian/Ubuntu, Homebrew, and other distributors. Key points:

1. When a Python environment has an `EXTERNALLY-MANAGED` marker file, `pip install` refuses to operate unless `--break-system-packages` is passed
2. This prevents users from accidentally breaking their OS Python with conflicting packages
3. **pipx** was created as the canonical solution — each application gets its own isolated venv
4. Pipx venvs are **not** externally managed — they are fully writable

### How pipx Isolates Environments

```
pipx install some-package
```

Creates:
```
~/.local/share/pipx/venvs/some-package/     # Isolated venv
~/.local/bin/some-package                   # Symlink to console script
```

Each package's dependencies are confined to its own venv. `pipx inject` can add packages to an existing venv, but this reintroduces conflict risk.

---

## 4. Recommended Approach

### 4.1 Architecture Decision: **Plugin-Level Venv Isolation via pipx**

Each dashboard plugin and MCP server that needs external Python dependencies gets its own pipx-managed virtual environment. Plugins that only use standard library + `fastapi`/`pydantic` (already in the hermes-agent venv) continue to run from the main venv with zero overhead.

```
~/.hermes/profiles/orchestrator/home/.local/share/pipx/venvs/
├── hermes-plugin-vram-observability/    # Only if it needs custom deps
├── hermes-plugin-inbox/                 # Only if it needs custom deps
├── mcp-python-server-1/                 # MCP server deps
└── ...
```

### 4.2 Plugin Dependency Declaration

Each plugin that needs external dependencies declares them in a standard format:

```
~/.hermes/plugins/hermes-plugin-foo/
├── dashboard/
│   ├── plugin_api.py
│   └── dist/index.js
├── manifest.json           # Plugin metadata
└── requirements.txt        # NEW: pip-compatible dependency list
```

**manifest.json addition:**
```json
{
  "name": "hermes-plugin-foo",
  "version": "1.0.0",
  "api": "dashboard/plugin_api.py",
  "dependencies": {
    "type": "pipx",
    "requirements": "requirements.txt"
  }
}
```

### 4.3 Plugin Runner Architecture

The dashboard backend (FastAPI app at port 9119) currently imports plugin API routers directly. With sandboxing, the runner changes:

**Current (single venv):**
```python
# Dashboard imports plugin_api.py directly — same Python process
from plugins.hermes_plugin_foo.dashboard.plugin_api import router
app.include_router(router, prefix="/api/plugins/hermes-plugin-foo")
```

**Recommended (sandboxed):**
Plugin backends with external deps run as **subprocess microservices**. The dashboard proxy-routes to them:

```python
# Dashboard registers a proxy route instead of direct import
# The plugin runs as: pipx run --spec hermes-plugin-foo plugin-foo-server --port 9101
app.mount("/api/plugins/hermes-plugin-foo", ProxyRoute("http://127.0.0.1:9101"))
```

**Benefits:**
- Full pipx isolation — each plugin's deps never conflict
- Plugin crashes don't take down the dashboard
- Plugins can use different Python versions
- MCP servers already follow this model (subprocess with `command` + `args`)

**Trade-offs:**
- Slightly more complex than direct imports
- Process management overhead (manage subprocess lifecycle)
- IPC latency (negligible on localhost)

### 4.4 MCP Server Sandboxing

MCP servers already run as subprocesses. For Python-based MCP servers, the config extends naturally:

```yaml
mcp_servers:
  gdrive:
    command: node
    args: [/home/ubuntu/work/local-gdrive-mcp/server.js]
    enabled: true
  human-design:
    command: pipx
    args:
      - run
      - --spec
      - openhumandesignmcp[server]
      - openhumandesignmcp-server
      - --transport
      - stdio
    enabled: false
```

The `pipx run` command creates a temporary venv if needed, or reuses an existing one. Dependencies are fully isolated.

### 4.5 Plugin Lifecycle Management

Use a lightweight process supervisor (or integrate with existing PM2 setup):

```
~/.hermes/plugins/plugin-supervisor.json
```

```json
{
  "hermes-plugin-foo": {
    "type": "pipx-subprocess",
    "package": "hermes-plugin-foo",
    "port": 9101,
    "auto_start": true,
    "restart_on_failure": true
  }
}
```

The dashboard startup sequence:
1. Start main FastAPI app on port 9119
2. Read plugin manifests with `dependencies.type == "pipx"`
3. For each sandboxed plugin: install via pipx if not present, start subprocess
4. Mount proxy routes

---

## 5. Implementation Steps

### Phase 1: Infrastructure (Week 1)

1. **Create pipx home for orchestrator profile**
   - Already exists at `~/.hermes/profiles/orchestrator/home/.local/share/pipx/`
   - Set `PIPX_HOME` environment variable in dashboard systemd/PM2 config
   - Verify: `pipx ensurepath` (profile-scoped)

2. **Add `manifest.json` to each dashboard plugin**
   - Add `dependencies` field
   - Default: no external deps (runs in main venv)
   - Explicit: `{"type": "pipx", "requirements": "requirements.txt"}`

3. **Build plugin supervisor module**
   - Python module: `hermes_dashboard.plugin_supervisor`
   - Reads manifests, manages subprocess lifecycle
   - Integrates with PM2 via `pm2 start` / `pm2 stop`

### Phase 2: Plugin Migration (Week 2)

4. **Migrate plugins with custom deps**
   - For each plugin that needs deps beyond current venv:
     - Create `requirements.txt`
     - `pipx install --editable .` (from plugin directory)
     - Add subprocess config to supervisor
   - **No current plugins need this** — this is forward-looking

5. **Update dashboard route registration**
   - For sandboxed plugins: use `httpx`-based proxy instead of direct import
   - For non-sandboxed: keep direct import (faster, simpler)

### Phase 3: MCP Integration (Week 3)

6. **Add pipx runner to MCP launcher**
   - Support `command: pipx` in MCP server config
   - Handle `pipx run --spec <package>` as a first-class transport

7. **Template for Python MCP servers**
   - Create `mcp-server-template/` with pyproject.toml
   - Document `pipx install` + config.yaml pattern

### Phase 4: Testing & Docs (Week 4)

8. **Conflict-free dependency test**
   - Create two test plugins with intentionally conflicting deps
   - Verify both can run simultaneously

9. **Update runbooks and onboarding**
   - Document plugin dependency declaration
   - Add pipx sandboxing to swarm ops runbooks

---

## 6. Migration Plan for Existing Plugins

### 6.1 No-Break Guarantee

All existing plugins import only `fastapi` + standard library. They run fine from the main hermes-agent venv and require **zero changes**. The sandboxing infrastructure is opt-in:

| Plugin | External Deps? | Action |
|--------|---------------|--------|
| vram-observability | None (stdlib only) | No change |
| orchestrator-command-deck | None (stdlib only) | No change |
| mcp-controller | None (stdlib only) | No change |
| realtime-activity-stream | None (stdlib only) | No change |
| workspace-tree-navigator | None (stdlib only) | No change |
| hermes-inbox | None (`fastapi`, `pydantic`, stdlib) | No change |
| kanban | None (stdlib only) | No change |
| swarm-manager | None (JS-only, no Python backend) | No change |

### 6.2 When to Sandbox

A plugin should be sandboxed via pipx when:
1. It needs a package **not** in the hermes-agent venv
2. It needs a **different version** of a package than what's in the main venv
3. It is a Python MCP server with its own dependency tree

---

## 7. Alternative Approaches Considered

### 7.1 pipx inject (Rejected)

```bash
pipx inject hermes-agent plugin-dep-1 plugin-dep-2
```

**Why rejected:** This installs all plugin deps into the single hermes-agent venv — exactly the conflict problem we're solving. `pipx inject` is useful for adding tools to an existing pipx app, but not for isolating mutually incompatible dependencies.

### 7.2 Docker per Plugin (Rejected for now)

Each plugin runs in its own Docker container with port mapping.

**Why rejected (for now):** Overkill for simple plugins. The MCP hosting product already uses Docker for tenant isolation, but dashboard plugins are lightweight Python modules. Pipx subprocess isolation provides sufficient separation without Docker's overhead.

**Future consideration:** If a plugin needs system-level dependencies (e.g., `nvidia-smi` wrapper, video processing with ffmpeg), Docker may be the right choice. The supervisor architecture supports mixed isolation levels.

### 7.3 Conda/Mamba Environments (Rejected)

**Why rejected:** Conda adds complexity (separate package manager, channel management) and large disk footprint. Pipx is already installed and understood.

### 7.4 Single venv with pip --target (Rejected)

```bash
pip install --target=plugins/foo/vendor -r requirements.txt
```

**Why rejected:** Vendoring deps per plugin works but creates import path complications, binary extension issues, and doesn't integrate with pipx's upgrade/uninstall workflow.

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| pipx subprocess crashes | Low | Plugin unavailable, dashboard unaffected | PM2 auto-restart, health checks |
| Port conflicts | Low | Plugin won't start | Supervisor assigns ports from pool |
| pipx version too old | Low | Missing features | v1.4.3 supports `pipx run --spec`; upgrade if needed |
| Profile pipx home confusion | Medium | Packages installed in wrong location | Explicit `PIPX_HOME` in service config |
| Startup time increase | Low | 1-2s per sandboxed plugin | Only sandbox plugins that need it; lazy-start |

---

## 9. Quick Reference

### Plugin Developer: Adding Dependencies

```bash
# 1. Create requirements.txt
cat > ~/.hermes/plugins/my-plugin/requirements.txt << EOF
requests>=2.31.0
pillow>=10.0.0
EOF

# 2. Update manifest.json
# Add: "dependencies": {"type": "pipx", "requirements": "requirements.txt"}

# 3. Install for development
PIPX_HOME=~/.hermes/profiles/orchestrator/home/.local/share/pipx \
  pipx install --editable ~/.hermes/plugins/my-plugin/

# 4. Dashboard auto-discovers and starts on next restart
```

### Adding a Python MCP Server

```yaml
# In config.yaml mcp_servers:
my-python-mcp:
  command: pipx
  args:
    - run
    - --spec
    - my-mcp-server>=1.0
    - my-mcp-server
    - --transport
    - stdio
  enabled: true
```

---

## 10. References

- [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
- [pipx documentation](https://pipx.pypa.io/stable/)
- [Hermes Agent Plugin Architecture](https://hermes-agent.nousresearch.com/docs)
- [GRO-64 Linear Task](https://linear.app/growthwebdev/issue/GRO-64/optimize-swarm-setup-pep-668-pipx-sandboxing-for-plugin-runners)
