#!/usr/bin/env python3
"""
Jules Session Manager — Linear → Jules Bridge
==============================================
Queries Linear for issues labeled 'agent:jules' that don't have active
Jules sessions, then launches bounded Jules sessions for each.

Also handles: review requests, conflict resolution, and status sync.

Run: python3 jules_session_manager.py
Cron: every 15min
"""

import os, sys, json, re, time, subprocess
import urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════

LINEAR_KEY = os.environ.get('LINEAR_API_KEY', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', os.environ.get('GITHUB_PAT_KEY', ''))

# Linear project → GitHub repo mapping
PROJECT_REPO_MAP = {
    # Human Design Engine & sub-products
    "HD Engine Core": ("mbgulden/hd-platform", "hd-platform"),
    "HD Reports Engine": ("mbgulden/hd-platform", "hd-platform"),
    "HD Growth Engine": ("mbgulden/hd-platform", "hd-platform"),
    "HD Creator Tools": ("mbgulden/hd-platform", "hd-platform"),
    "HD Coach Platform": ("mbgulden/hd-platform", "hd-platform"),
    "HD Consumer App": ("mbgulden/hd-platform", "hd-platform"),
    "HD Enterprise": ("mbgulden/hd-platform", "hd-platform"),
    "HD Dating Products": ("mbgulden/hd-platform", "hd-platform"),
    "HD Education": ("mbgulden/hd-platform", "hd-platform"),
    "HD AI Lab": ("mbgulden/hd-platform", "hd-platform"),
    "Human Design Engine": ("mbgulden/hd-platform", "hd-platform"),
    # Open source engine
    "OpenHumanDesignMCP": ("mbgulden/OpenHumanDesignMCP", "hd-engine"),
    # Swarm ops & infra
    "Agentic Swarm Ops": ("mbgulden/agentic-swarm-ops", "swarm-ops"),
    "Agentic Swarm Ops Documentation": ("mbgulden/agentic-swarm-ops", "swarm-ops"),
    # Sentinel
    "Sovereign Sentinel Homelab": ("mbgulden/SovereignSentinel", "sentinel"),
    # Consulting & other
    "Active Oahu Tours": ("mbgulden/activeoahutours.com", "active-oahu"),
    "Project Honeybadger": ("mbgulden/hd-platform", "hd-platform"),
    "AI Implementation Consulting": ("mbgulden/ai-consulting", "ai-consulting"),
}

# Default repo if no mapping found
DEFAULT_REPO = "mbgulden/hd-platform"

# Max concurrent Jules sessions
MAX_CONCURRENT = 10

# Jules session tracking file
TRACKING_FILE = Path("/tmp/jules-session-tracker.json")

# ═══════════════════════════════════════════════════════════════════
# API Helpers
# ═══════════════════════════════════════════════════════════════════

def linear_request(query, variables=None):
    if not LINEAR_KEY: return None
    data = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=data,
        headers={"Content-Type": "application/json", "Authorization": LINEAR_KEY},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read())
    except Exception as e:
        print(f"  Linear API error: {e}")
        return None

def github_request(url, method="GET", data=None):
    if not GITHUB_TOKEN: return None
    req_data = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=req_data,
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read())
    except Exception as e:
        print(f"  GitHub API error: {e}")
        return None

def jules_list_sessions():
    """Get list of all Jules sessions."""
    try:
        result = subprocess.run(
            ["jules", "remote", "list", "--session"],
            capture_output=True, text=True, timeout=30
        )
        sessions = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if parts and parts[0].isdigit() and len(parts[0]) >= 15:
                sessions.append({
                    "id": parts[0],
                    "description": " ".join(parts[1:-4]) if len(parts) > 4 else "",
                    "status": parts[-1] if parts else "unknown"
                })
        return sessions
    except Exception as e:
        print(f"  Jules list error: {e}")
        return []

def jules_launch(repo, task_prompt):
    """Launch a new Jules session."""
    try:
        cmd = ["jules", "new", "--repo", repo, task_prompt]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        # Extract session ID from output
        match = re.search(r'ID:\s*(\d+)', output)
        if match:
            return match.group(1), output
        return None, output
    except Exception as e:
        return None, str(e)

# ═══════════════════════════════════════════════════════════════════
# Core Logic
# ═══════════════════════════════════════════════════════════════════

def load_tracker():
    if TRACKING_FILE.exists():
        return json.loads(TRACKING_FILE.read_text())
    return {"sessions": {}, "last_run": None}

def save_tracker(tracker):
    TRACKING_FILE.write_text(json.dumps(tracker, indent=2))

def get_jules_issues():
    """Get Linear issues labeled 'agent:jules' that are Todo/In Progress."""
    query = """
    query JulesIssues {
      issues(
        filter: {
          labels: { name: { in: ["agent:jules", "agent:jules-review"] } }
          state: { type: { in: ["unstarted", "started"] } }
        }
        first: 30
      ) {
        nodes {
          id
          identifier
          title
          description
          state { name type }
          project { name }
          labels { nodes { name } }
          assignee { name }
        }
      }
    }
    """
    result = linear_request(query)
    if not result:
        return []
    return result.get("data", {}).get("issues", {}).get("nodes", [])

def build_jules_prompt(issue):
    """Build a self-contained Jules prompt from a Linear issue."""
    identifier = issue.get("identifier", "???")
    title = issue.get("title", "")
    description = issue.get("description", "") or ""
    project_name = (issue.get("project") or {}).get("name", "")
    labels = [l.get("name","") for l in (issue.get("labels") or {}).get("nodes", [])]
    
    repo_name, _ = PROJECT_REPO_MAP.get(project_name, (DEFAULT_REPO, "unknown"))
    
    is_review = "agent:jules-review" in labels
    
    if is_review:
        prompt = (
            f"Linear: {identifier} — REVIEW: {title}\n\n"
            f"Repo: {repo_name}\n"
            f"Goal: Review recent changes for this issue. Check the PR linked in Linear "
            f"and the latest commits on the feature branch. Verify: correctness, security, "
            f"style, and completeness against the issue requirements.\n"
            f"Context from issue:\n{description[:1000]}\n\n"
            f"Constraints:\n"
            f"- Review-only; do not merge\n"
            f"- Add review comments on the PR\n"
            f"- Summarize findings in a Linear comment\n"
            f"- If issues found, suggest fixes but don't implement unless minor\n"
            f"Deliverables: Review summary with approved/changes-requested status"
        )
    else:
        prompt = (
            f"Linear: {identifier} — {title}\n\n"
            f"Repo: {repo_name}\n"
            f"Goal: {title}\n"
            f"Context:\n{description[:1500]}\n\n"
            f"Constraints:\n"
            f"- PR-only; do not merge\n"
            f"- Keep changes scoped to this issue\n"
            f"- Do not touch secrets, billing, production infra, or unrelated modules\n"
            f"- Link work back to Linear issue {identifier} in branch/PR text\n"
            f"- Use a feature branch named {identifier.lower()}/description\n"
            f"Deliverables: Files changed, tests run, summary and blockers"
        )
    
    return prompt, repo_name

def sync_sessions():
    """Main sync loop: find unassigned Jules issues → launch sessions."""
    tracker = load_tracker()
    tracker["last_run"] = datetime.now(timezone.utc).isoformat()
    
    # Get current Jules sessions
    active_sessions = jules_list_sessions()
    active_ids = {s["id"] for s in active_sessions}
    active_count = len(active_ids)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Jules Session Manager")
    print(f"  Active Jules sessions: {active_count}")
    
    if active_count >= MAX_CONCURRENT:
        print(f"  At max concurrent ({MAX_CONCURRENT}). Skipping launch.")
        save_tracker(tracker)
        return
    
    # Get issues from Linear
    issues = get_jules_issues()
    print(f"  Linear issues labeled agent:jules: {len(issues)}")
    
    launched = 0
    slots_left = MAX_CONCURRENT - active_count
    
    for issue in issues:
        if launched >= slots_left:
            break
        
        issue_id = issue.get("id")
        identifier = issue.get("identifier")
        
        # Skip if already tracked with an active session
        if issue_id in tracker["sessions"]:
            old_session_id = tracker["sessions"][issue_id]
            if old_session_id in active_ids:
                continue  # Session still active
        
        # Build prompt and launch
        prompt, repo = build_jules_prompt(issue)
        print(f"  Launching Jules for {identifier}: {issue.get('title','')[:60]}")
        print(f"    Repo: {repo}")
        
        session_id, output = jules_launch(repo, prompt)
        
        if session_id:
            tracker["sessions"][issue_id] = session_id
            launched += 1
            print(f"    ✅ Session {session_id} launched")
            
            # Update Linear with session ID
            linear_comment = (
                f"🤖 Jules session launched: `{session_id}`\n"
                f"Repo: `{repo}`\n"
                f"Monitor: `jules remote pull --session {session_id}`"
            )
            comment_mutation = f'''
            mutation {{
              commentCreate(input: {{
                issueId: "{issue_id}",
                body: "{linear_comment}"
              }}) {{ success }}
            }}
            '''
            linear_request(comment_mutation)
        else:
            print(f"    ❌ Launch failed: {output[:200]}")
    
    print(f"  Launched: {launched} new sessions")
    save_tracker(tracker)

if __name__ == "__main__":
    sync_sessions()
