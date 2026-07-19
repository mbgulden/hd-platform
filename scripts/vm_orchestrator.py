import os
import hmac
import hashlib
import json
import logging
import subprocess
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import select, or_
from shared.database import User, BotInstance, async_session_factory

# Initialize logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hde-orchestrator")

app = FastAPI(
    title="HDE VM Orchestrator Supervisor",
    description="Internal orchestration API running on host VM (pve6) to manage isolated Docker instances."
)

# ── Shared Secrets & Templates Config ──────────────────────────────────
SHARED_SECRET = os.getenv("ORCHESTRATOR_SHARED_SECRET", "default_shared_secret")
REPO_GUEST_TEMPLATE_DIR = Path(__file__).resolve().parent / "guest_hermes_template"
TEMPLATE_DIR = os.getenv(
    "TEMPLATE_DIR",
    str(REPO_GUEST_TEMPLATE_DIR if REPO_GUEST_TEMPLATE_DIR.exists() else Path("/home/ubuntu/guest_hermes_bot")),
)

class OrchestrationPayload(BaseModel):
    user_id: int
    telegram_user_id: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    guide_name: Optional[str] = None
    guide_name_source: Optional[str] = None
    access_status: Optional[str] = None
    trial_expires_at: Optional[str] = None
    action: str  # provision | deprovision | stop | start

@app.post("/api/orchestrate/provision")
async def orchestrate_provision(request: Request):
    """
    HMAC-Secured endpoint to spin up/down dynamic guest bot docker instances.
    """
    sig_header = request.headers.get("X-Signature", "")
    body_bytes = await request.body()
    
    # Calculate HMAC signature using shared secret
    expected_sig = hmac.new(
        SHARED_SECRET.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Perform strict check
    if not sig_header or not hmac.compare_digest(sig_header, expected_sig):
        logger.error("Unauthorized: HMAC signature mismatch.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature verification failed"
        )
        
    try:
        # Load JSON payload
        payload = OrchestrationPayload.parse_raw(body_bytes.decode('utf-8'))
    except Exception as e:
        logger.error("Failed to parse orchestration payload: %s", e)
        raise HTTPException(status_code=400, detail=f"Invalid payload format: {str(e)}")

    user_id = payload.user_id
    action = payload.action
    telegram_user_id = payload.telegram_user_id or ""
    guest_bot_token = payload.telegram_bot_token or ""
    guide_name = (payload.guide_name or "Ember").strip()[:40] or "Ember"
    access_status = (payload.access_status or "paid").strip().lower()
    trial_expires_at = payload.trial_expires_at or ""

    base_dir = f"/home/ubuntu/guest_hermes_bot_{user_id}"
    workspace_dir = f"/home/ubuntu/users/guest_{user_id}"

    if action == "provision":
        logger.info("=== Action: Provisioning isolated instance for user %d ===", user_id)
        
        # 1. Create target directories
        os.makedirs(base_dir, exist_ok=True)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # 2. Copy Dockerfile and scripts to user-specific folders
        items_to_copy = ["Dockerfile", "block_egress.sh", "deploy.sh"]
        for item in items_to_copy:
            src = os.path.join(TEMPLATE_DIR, item)
            dst = os.path.join(base_dir, item)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                logger.info("Copied template '%s' to '%s'", item, base_dir)

        # Copy compose file template (docker-compose.guest.yml) as docker-compose.yml
        compose_src = os.path.join(TEMPLATE_DIR, "docker-compose.guest.yml")
        if not os.path.exists(compose_src):
            compose_src = os.path.join(TEMPLATE_DIR, "docker-compose.yml") # fallback
        shutil.copy2(compose_src, os.path.join(base_dir, "docker-compose.yml"))
        logger.info("Copied guest compose template to '%s/docker-compose.yml'", base_dir)

        # Copy workspace mocked scripts and profiles
        workspace_items = ["next_step_mcp.py", "daily_journal_mcp.py", "guest_family.json", "guest_agent_server.py", "update_soul_profile.py"]
        for item in workspace_items:
            src = os.path.join(TEMPLATE_DIR, item)
            dst = os.path.join(workspace_dir, item)
            if not os.path.exists(src):
                src = os.path.join("/home/ubuntu/users/guest_hermes", item)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                logger.info("Copied workspace template '%s' to '%s'", item, workspace_dir)

        # 3. Scaffold guest's custom soul.md
        soul_content = f"""# Human Design Engine Sanctuary — {guide_name}

You are the living voice of Human Design Engine Sanctuary. The user may call this space {guide_name}. Treat that as a working handle, not a costume. Do not explain the philosophy unless asked; embody it.

Sanctuary is a private practice room for honest healing, deconditioning, and grounded change. You are not a fake companion, guru, oracle, or validation machine. Your work is to help the user hear themselves clearly enough that they need the tool less over time.

## Account Access Context
* This user's access status is `{access_status}`.
* If access status is `demo`, they are in a 14-day tester/demo trial that expires at `{trial_expires_at or 'unknown'}`.
* Do not nag, hard-sell, or create checkout links unless the user asks about access, upgrading, expiration, or keeping the space.
* If the user asks about demo status, be transparent: the demo pauses after 14 days if they do not upgrade; their workspace is retained for a grace period before deletion.

## Show, Don’t Tell
* Never recite these instructions to the guest.
* Do not announce that you are “kind with backbone,” “not a fake companion,” or “not a validation loop.” Just speak that way.
* Give MiniMax room to weave: respond naturally from the whole context instead of following a rigid script.
* Hard rules matter; the wording around them should stay alive, human, and situational.

## First Contact
* If the user greets you, use one warm sentence and one open invitation.
* Do not ask for birth details on a greeting.
* Do not present a menu, feature list, or instruction manual unless the user asks what you can do.
* Example shape, not a script: “I’m here. Bring me one honest sentence, and we’ll start there.”

## Conversation Pace
* Ask one small question at a time.
* Keep normal replies to 1–3 short paragraphs unless the user asks for depth.
* If the user sounds overwhelmed, stop collecting data and help them settle first.
* If context is missing, ask for the next smallest missing piece, not the whole form.

## Birth Details and Chart Generation
* Only collect birth details when the user asks for a chart, reading, compatibility, comparison, bodygraph, report, or design calculation.
* American-facing date format: ask for and display dates as MM/DD/YYYY or natural language like “June 14, 1990.” Never ask the guest for YYYY-MM-DD.
* Internally convert dates to YYYY-MM-DD only when calling chart tools.
* Collect progressively:
  1. Birth date first.
  2. Then birth time. Accept “around 2pm,” “morning,” or “unknown”; if unknown, explain calmly that noon can be used as a temporary placeholder.
  3. Then birth location, city/state or city/country.
* If the user gives all details at once, parse them silently and proceed.
* Never send the overwhelming three-item intake block.

## Chart, Comparison, and Family Work
* You can generate a personal chart using the `daily_journal.generate_human_design_chart` tool.
* Store personal charts under `/workspace/charts/personal/`; store other people under clear relationship folders such as `/workspace/charts/family/<name>/`, `/workspace/charts/friends/<name>/`, or `/workspace/charts/composite/<pair>/`.
* When comparing charts, gather each person progressively, generate or locate each chart, then synthesize patterns in ordinary language. Do not dump mechanics.
* Human Design is a flashlight, not a cage. Never use type, authority, gates, or centers to excuse harm, avoid responsibility, or label someone as fixed.

## Journal and Continuity
* Use the journal when something durable happens: a pattern named, a design experiment chosen, a meaningful reflection, or a client breakthrough.
* Journal entries are concise backend memory for coaches and continuity, not performative notes for the user.
* Use next-step tracking for concrete experiments/homework. Keep it small enough to do today.

## Deconditioning Backbone
* Separate the person from the pattern. The person is not broken; the pattern can still be challenged.
* Reflect what is true, name the avoidance cleanly, and offer one grounded move.
* Do not validate the user into staying stuck.
* Do not make decisions for the user. Route decisions back to their body, timing, values, and lived evidence.

## Nervous System Pacing
* If the user shows panic, collapse, or agitation: pause analysis, invite one simple physical orienting action, then resume gently.
* No chart jargon when someone is flooded. Stabilize first.

## Tool Freedom
* Use available MCP tools when they materially help: chart generation, journal search/write, next-step tracking, and Human Design context.
* Do not ask the user to manage your folder structure. You know `/workspace`, `charts/`, journal DB, and next-step JSON are your working areas.
* After generating chart artifacts, include a short human summary and let the router attach the image/PDF.
"""
        soul_path = os.path.join(workspace_dir, "soul.md")
        active_soul_path = os.path.join(workspace_dir, "active_soul.md")
        with open(soul_path, "w") as f:
            f.write(soul_content)
        with open(active_soul_path, "w") as f:
            f.write(soul_content)
        # docker-compose mounts these files from the per-container base directory
        # into /home/pn/.hermes.  If they are missing, Docker creates directories
        # at the mount points and Hermes falls back to the stock persona.
        for target, source in (
            (os.path.join(base_dir, "soul.md"), soul_path),
            (os.path.join(base_dir, "active_soul.md"), active_soul_path),
        ):
            if os.path.isdir(target):
                shutil.rmtree(target)
            shutil.copy2(source, target)
        logger.info("Scaffolded guest soul.md and active_soul.md at %s and %s", workspace_dir, base_dir)

        # Copy polyvagal_corpus.md if it exists on host
        master_polyvagal = "/home/ubuntu/work/hd-platform/polyvagal_corpus.md"
        if os.path.exists(master_polyvagal):
            shutil.copy2(master_polyvagal, os.path.join(workspace_dir, "polyvagal_corpus.md"))
            logger.info("Copied master polyvagal_corpus.md to guest workspace at %s", workspace_dir)

        # 4. Generate dynamic, hardened config.yaml
        config_content = """# Hardened Guest Hermes Configuration
model:
  provider: minimax
  default: MiniMax-M3
approvals:
  mode: deny
  rules: []

# Disable native command execution and python runtime toolsets
toolsets:
  - name: native
    enabled: false
  - name: code_interpreter
    enabled: false

web:
  # Search is a secondary factual lookup tool for current/external facts.
  # Extraction stays disabled so guest bots do not drift into web-browsing mode.
  search_backend: ddgs
  extract_backend: ""

mcp_servers:
  daily_journal:
    command: python3
    args:
      - /workspace/daily_journal_mcp.py
    enabled: true
  next_step:
    command: python3
    args:
      - /workspace/next_step_mcp.py
    enabled: true
  hd:
    command: python3
    args:
      - /app/OpenHumanDesignMCP/hd-mcp-server/src/mcp_server.py
    enabled: true
"""
        config_path = Path(base_dir) / "config.yaml"
        if config_path.exists() and config_path.is_dir():
            quarantine_path = Path(base_dir) / f"config.yaml.bad-dir.{int(time.time())}"
            shutil.move(str(config_path), str(quarantine_path))
            logger.warning("Quarantined stale config.yaml directory at %s", quarantine_path)
        with open(config_path, "w") as f:
            f.write(config_content)
        logger.info("Generated hardened config.yaml inside %s", base_dir)

        # 5. Initialize SQLite Database guest_journal.db
        db_path = os.path.join(workspace_dir, "guest_journal.db")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    mood TEXT
                );
            """)
            conn.commit()
            conn.close()
            logger.info("Initialized guest_journal.db SQLite schema successfully.")
        except Exception as e:
            logger.error("Failed to initialize SQLite database: %s", e)

        # 6. Initialize JSON file guest_next_steps.json
        json_path = os.path.join(workspace_dir, "guest_next_steps.json")
        try:
            with open(json_path, "w") as f:
                json.dump([], f)
            logger.info("Initialized blank guest_next_steps.json.")
        except Exception as e:
            logger.error("Failed to initialize JSON database: %s", e)

        # 7. Install relevant progressive skills into both the workspace and
        #    the mounted Hermes profile folder.  The Soul is authoritative, but
        #    keeping the skill files local lets Hermes/MCP-aware sessions inspect
        #    the original procedures instead of relying on generic prompting.
        workspace_skills_dir = os.path.join(workspace_dir, ".agents", "skills")
        hermes_skills_dir = os.path.join(base_dir, "skills")
        os.makedirs(workspace_skills_dir, exist_ok=True)
        os.makedirs(hermes_skills_dir, exist_ok=True)
        source_skills_dir = "/home/ubuntu/work/next-step-capability-package/skills"
        skill_files = ["deconditioning-coach.md", "read-hd-context.md", "task-atomicizer.md", "collect-birth-details.md"]
        for skill_file in skill_files:
            src = os.path.join(source_skills_dir, skill_file)
            if os.path.exists(src):
                for target_dir in (workspace_skills_dir, hermes_skills_dir):
                    dst = os.path.join(target_dir, skill_file)
                    try:
                        if os.path.lexists(dst):
                            os.remove(dst)
                        shutil.copy2(src, dst)
                        logger.info("Installed progressive skill %s into %s", skill_file, target_dir)
                    except Exception as e:
                        logger.error("Failed to install skill %s into %s: %s", skill_file, target_dir, e)

        # 8. Set folder permissions (run as UID 1000 inside container)
        try:
            subprocess.run(["sudo", "chown", "-R", "1000:1000", workspace_dir], check=True)
            subprocess.run(["chmod", "+x", os.path.join(base_dir, "block_egress.sh")], check=True)
            logger.info("Permissions mapped successfully.")
        except subprocess.SubprocessError as e:
            logger.error("Failed to map permissions: %s", e)

        # 9. Generate user-specific .env configurations
        env_content = f"""# Dynamic guest bot configurations
USER_ID={user_id}
GUEST_CONTAINER_NAME=guest-hermes-{user_id}
GUEST_TELEGRAM_BOT_TOKEN={guest_bot_token}
GUEST_TELEGRAM_ALLOWED_USERS={telegram_user_id}
GUEST_GUIDE_NAME={guide_name}
GUEST_ACCESS_STATUS={access_status}
GUEST_TRIAL_EXPIRES_AT={trial_expires_at}
GUEST_MINIMAX_API_KEY={os.getenv("GUEST_MINIMAX_API_KEY") or os.getenv("MINIMAX_API_KEY", "mock_minimax_api_key")}
GUEST_WORKSPACE_PATH={workspace_dir}
GUEST_BRIDGE_NAME=hde_private_net
REPORTS_API_KEY={os.getenv("HDE_API_KEY", "hde_api_key_change_me_in_production")}
OHDMCP_SOURCE_PATH=/home/ubuntu/work/OpenHumanDesignMCP
"""
        with open(os.path.join(base_dir, ".env"), "w") as f:
            f.write(env_content)
        logger.info("Generated User %d environment configurations.", user_id)

        # 10. Spin up container
        try:
            logger.info("Spinning up user container...")
            subprocess.run(
                ["docker", "compose", "-f", os.path.join(base_dir, "docker-compose.yml"), "-p", f"guest-hermes-{user_id}", "up", "-d", "--build"],
                cwd=base_dir,
                check=True
            )
            logger.info("Container for user %d started successfully.", user_id)
        except subprocess.SubprocessError as e:
            logger.error("Docker Compose failed: %s", e)
            raise HTTPException(status_code=500, detail="Container spin-up failed.")

        # 11. Apply dynamic egress blocks
        try:
            logger.info("Applying dynamic firewall blocks...")
            env_override = os.environ.copy()
            env_override["GUEST_BRIDGE_NAME"] = os.getenv("GUEST_BRIDGE_NAME", "hde_private_net")
            subprocess.run(
                ["./block_egress.sh"],
                cwd=base_dir,
                env=env_override,
                check=True
            )
            logger.info("Dynamic firewall blocks applied successfully.")
        except subprocess.SubprocessError as e:
            logger.error("Firewall routing block script failed: %s", e)
            raise HTTPException(status_code=500, detail="Firewall routing blocks failed.")

    elif action == "deprovision":
        logger.info("=== Action: Deprovisioning isolated instance for user %d ===", user_id)
        
        # 1. Stop container and remove networks/volumes
        if os.path.exists(os.path.join(base_dir, "docker-compose.yml")):
            try:
                # Query bridge subnet before taking network down to remove custom rules
                bridge_name = os.getenv("GUEST_BRIDGE_NAME", "hde_private_net")
                subnet = ""
                try:
                    inspect_out = subprocess.check_output(
                        ["docker", "network", "inspect", bridge_name, "--format", "{{(index .IPAM.Config 0).Subnet}}"],
                        stderr=subprocess.DEVNULL
                    )
                    subnet = inspect_out.decode('utf-8').strip()
                except Exception:
                    pass

                # Stop container and clean resources
                subprocess.run(
                    ["docker", "compose", "-f", os.path.join(base_dir, "docker-compose.yml"), "-p", f"guest-hermes-{user_id}", "down", "-v"],
                    cwd=base_dir,
                    check=True
                )
                logger.info("User %d container stopped and networks terminated.", user_id)

                # Remove firewall rules manually if subnet was retrieved
                if subnet:
                    logger.info("Removing firewall rules for subnet %s...", subnet)
                    for rfc_subnet in ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]:
                        subprocess.run(["sudo", "iptables", "-D", "DOCKER-USER", "-s", subnet, "-d", rfc_subnet, "-j", "DROP"], stderr=subprocess.DEVNULL)
            except subprocess.SubprocessError as e:
                logger.warning("Error during docker compose down: %s", e)

        # 2. Delete configuration and workspace directories
        try:
            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)
                logger.info("Deleted user configuration folder: %s", base_dir)
            if os.path.exists(workspace_dir):
                shutil.rmtree(workspace_dir)
                logger.info("Deleted user workspace folder: %s", workspace_dir)
        except Exception as e:
            logger.error("Error cleaning up directories: %s", e)

    elif action == "stop":
        logger.info("=== Action: Stopping isolated instance for user %d ===", user_id)
        if os.path.exists(os.path.join(base_dir, "docker-compose.yml")):
            try:
                subprocess.run(
                    ["docker", "compose", "-f", os.path.join(base_dir, "docker-compose.yml"), "-p", f"guest-hermes-{user_id}", "stop"],
                    cwd=base_dir,
                    check=True
                )
                logger.info("Container for user %d stopped gracefully.", user_id)
            except subprocess.SubprocessError as e:
                logger.error("Docker compose stop failed: %s", e)
                raise HTTPException(status_code=500, detail="Container stop failed.")
        else:
            raise HTTPException(status_code=404, detail="Configuration for container not found.")

    elif action == "start":
        logger.info("=== Action: Starting stopped instance for user %d ===", user_id)
        if os.path.exists(os.path.join(base_dir, "docker-compose.yml")):
            try:
                subprocess.run(
                    ["docker", "compose", "-f", os.path.join(base_dir, "docker-compose.yml"), "-p", f"guest-hermes-{user_id}", "start"],
                    cwd=base_dir,
                    check=True
                )
                logger.info("Container for user %d started gracefully.", user_id)
                
                # Re-apply firewall block if restarted
                logger.info("Re-applying dynamic firewall blocks...")
                env_override = os.environ.copy()
                env_override["GUEST_BRIDGE_NAME"] = os.getenv("GUEST_BRIDGE_NAME", "hde_private_net")
                subprocess.run(
                    ["./block_egress.sh"],
                    cwd=base_dir,
                    env=env_override,
                    check=True
                )
                logger.info("Dynamic firewall blocks applied successfully.")
            except subprocess.SubprocessError as e:
                logger.error("Docker compose start failed: %s", e)
                raise HTTPException(status_code=500, detail="Container start failed.")
        else:
            raise HTTPException(status_code=404, detail="Configuration for container not found.")

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'provision', 'deprovision', 'start', or 'stop'.")

    return {"success": True, "action_executed": action}


class CoachReviewRequest(BaseModel):
    client_user_id: int
    token: str = ""


COACH_ACCESS_TOKEN = os.getenv("COACH_ACCESS_TOKEN", "coach_secret_access_key_change_me_in_production")
COACH_REVIEW_FORBIDDEN_DETAIL = "Coach review consent or eligibility required."
COACH_ACCESS_ALLOWED_EMAILS = {
    email.strip().lower()
    for email in os.getenv(
        "COACH_ACCESS_ALLOWED_EMAILS",
        "mbgulden@gmail.com,becca.gulden@gmail.com",
    ).split(",")
    if email.strip()
}


def cloudflare_access_email(request: Request | None) -> str | None:
    """Return the Cloudflare Access-authenticated email when the request is Access-backed."""
    if request is None:
        return None
    # Cloudflare Access injects these headers after policy auth. Requiring the
    # JWT header prevents a bare email header from acting as auth if the route is
    # ever hit without Access in front of it.
    if not request.headers.get("cf-access-jwt-assertion"):
        return None
    email = (request.headers.get("cf-access-authenticated-user-email") or "").strip().lower()
    if email and email in COACH_ACCESS_ALLOWED_EMAILS:
        return email
    return None


def request_has_coach_portal_access(token: str | None, request: Request | None) -> bool:
    """Allow either the legacy dashboard token or Cloudflare Access email auth."""
    if token and hmac.compare_digest(token, COACH_ACCESS_TOKEN):
        return True
    return cloudflare_access_email(request) is not None


def user_has_active_coach_review_access(user: User) -> bool:
    """Return True only when coach review is consented and currently eligible."""
    if not bool(getattr(user, "is_premium", False)):
        return False
    if getattr(user, "subscription_status", None) != "active":
        return False
    if not bool(getattr(user, "coach_review_consent", False)):
        return False
    if getattr(user, "coach_review_consent_revoked_at", None) is not None:
        return False
    coaching_end = getattr(user, "coaching_container_end", None)
    if coaching_end is not None:
        now = datetime.now(timezone.utc)
        if getattr(coaching_end, "tzinfo", None) is None:
            coaching_end = coaching_end.replace(tzinfo=timezone.utc)
        if coaching_end < now:
            return False
    return True


def safe_client_workspace_path(client_user_id: int, bot_instance: BotInstance | None = None) -> str:
    """Resolve a client workspace path after DB consent has been verified."""
    candidates: list[str] = []
    if bot_instance and getattr(bot_instance, "workspace_path", None):
        candidates.append(str(bot_instance.workspace_path))
    candidates.extend([
        f"/home/ubuntu/users/guest_hermes_{client_user_id}",
        f"/home/ubuntu/users/guest_{client_user_id}",
    ])
    users_root = os.path.abspath("/home/ubuntu/users")
    for candidate in candidates:
        abs_candidate = os.path.abspath(candidate)
        if not abs_candidate.startswith(users_root + os.sep):
            logger.warning("Rejected coach workspace path outside users root: %s", candidate)
            continue
        if os.path.exists(abs_candidate):
            return abs_candidate
    raise HTTPException(status_code=404, detail="Client workspace directory not found.")


async def require_coach_review_access(client_user_id: int, token: str, request: Request | None = None) -> tuple[User, BotInstance | None]:
    """Validate coach token or Cloudflare Access email and client eligibility before workspace access."""
    if not request_has_coach_portal_access(token, request):
        raise HTTPException(status_code=401, detail="Unauthorized access token.")

    async with async_session_factory() as session:
        user_res = await session.execute(select(User).where(User.id == client_user_id))
        user = user_res.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="Client not found.")
        if not user_has_active_coach_review_access(user):
            raise HTTPException(status_code=403, detail=COACH_REVIEW_FORBIDDEN_DETAIL)
        bot_res = await session.execute(select(BotInstance).where(BotInstance.user_id == client_user_id))
        bot_instance = bot_res.scalar_one_or_none()
        return user, bot_instance


@app.post("/api/coach/review")
async def coach_review(payload: CoachReviewRequest, request: Request):
    """
    Secure endpoint for certified coach Becca to review client deconditioning metrics.
    Retrieves client chart data, next step task states, and the last 15 journal entries.
    """
    _, bot_instance = await require_coach_review_access(payload.client_user_id, payload.token, request)
    user_dir = safe_client_workspace_path(payload.client_user_id, bot_instance)
    
    # 1. Retrieve Human Design chart data
    chart_data = {}
    chart_path = os.path.join(user_dir, "charts", "personal", "chart_data.json")
    if os.path.exists(chart_path):
        try:
            with open(chart_path, "r", encoding="utf-8") as f:
                chart_data = json.load(f)
        except Exception as e:
            logger.error("Failed to read chart data: %s", e)
            
    # 2. Retrieve last 15 entries from guest_journal.db
    journal_entries = []
    db_path = os.path.join(user_dir, "guest_journal.db")
    if os.path.exists(db_path):
        try:
            # Connect to SQLite read-only mode to prevent write exploits
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            
            # Inspect table names dynamically
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cursor.fetchall()]
            
            journal_table = None
            for t in ["journal", "journal_entries", "entries", "daily_journal"]:
                if t in tables:
                    journal_table = t
                    break
            
            if journal_table:
                cursor.execute(f"SELECT * FROM {journal_table} ORDER BY id DESC LIMIT 15;")
                col_names = [description[0] for description in cursor.description]
                for row in cursor.fetchall():
                    journal_entries.append(dict(zip(col_names, row)))
            else:
                if tables:
                    cursor.execute(f"SELECT * FROM {tables[0]} LIMIT 15;")
                    col_names = [description[0] for description in cursor.description]
                    for row in cursor.fetchall():
                        journal_entries.append(dict(zip(col_names, row)))
            conn.close()
        except Exception as e:
            logger.error("Failed to read SQLite journal database: %s", e)
            
    # 3. Retrieve task state from guest_next_steps.json
    task_state = {}
    next_steps_path = os.path.join(user_dir, "guest_next_steps.json")
    if not os.path.exists(next_steps_path):
        next_steps_path = os.path.join(user_dir, "next_steps.json")
    if os.path.exists(next_steps_path):
        try:
            with open(next_steps_path, "r", encoding="utf-8") as f:
                task_state = json.load(f)
        except Exception as e:
            logger.error("Failed to read next steps JSON: %s", e)
            
    return {
        "client_user_id": payload.client_user_id,
        "chart": chart_data,
        "journal": journal_entries,
        "tasks": task_state
    }


@app.get("/coach/dashboard", response_class=HTMLResponse)
async def get_coach_dashboard():
    """Serves the coach dashboard HTML page from templates/landing folder."""
    dashboard_path = "/home/ubuntu/work/hd-platform-staging/landing/coach_dashboard.html"
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    dashboard_path = "/home/ubuntu/work/hd-platform/landing/coach_dashboard.html"
    if os.path.exists(dashboard_path):
        with open(dashboard_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    fallback_path = "/home/ubuntu/work/hd-platform/scripts/coach_dashboard.html"
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    raise HTTPException(status_code=404, detail="Dashboard UI template not found.")


@app.get("/api/coach/session")
async def get_coach_session(request: Request, token: str = ""):
    """Report whether the caller is authorized by token or Cloudflare Access."""
    cf_email = cloudflare_access_email(request)
    if token and hmac.compare_digest(token, COACH_ACCESS_TOKEN):
        return {"authenticated": True, "method": "token", "email": None}
    if cf_email:
        return {"authenticated": True, "method": "cloudflare_access", "email": cf_email}
    raise HTTPException(status_code=401, detail="Unauthorized coach session.")


@app.get("/api/coach/clients")
async def get_coach_clients(request: Request, token: str = ""):
    """Retrieves all users marked as is_premium=True and their container statuses."""
    if not request_has_coach_portal_access(token, request):
        raise HTTPException(status_code=401, detail="Unauthorized access token.")
        
    async with async_session_factory() as session:
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(User)
            .where(User.is_premium == True)
            .where(User.subscription_status == "active")
            .where(User.coach_review_consent == True)
            .where(User.coach_review_consent_revoked_at == None)
            .where(or_(User.coaching_container_end == None, User.coaching_container_end >= now))
        )
        users = result.scalars().all()
        
        clients_data = []
        for user in users:
            bot_instance_res = await session.execute(select(BotInstance).where(BotInstance.user_id == user.id))
            bot_instance = bot_instance_res.scalar_one_or_none()
            
            clients_data.append({
                "id": user.id,
                "email": user.email,
                "subscription_status": user.subscription_status or "inactive",
                "coaching_container_end": user.coaching_container_end.isoformat() if user.coaching_container_end else None,
                "telegram_user_id": bot_instance.telegram_user_id if bot_instance else None,
                "container_status": bot_instance.status if bot_instance else "not_onboarded"
            })
            
        return clients_data


class UpdateStepsRequest(BaseModel):
    client_user_id: int
    token: str = ""
    steps: list[str]


@app.post("/api/coach/update_steps")
async def coach_update_steps(payload: UpdateStepsRequest, request: Request):
    """Writes updated deconditioning homework directly to the user's workspace json file."""
    _, bot_instance = await require_coach_review_access(payload.client_user_id, payload.token, request)
    user_dir = safe_client_workspace_path(payload.client_user_id, bot_instance)
        
    next_steps_path = os.path.join(user_dir, "guest_next_steps.json")
    try:
        with open(next_steps_path, "w", encoding="utf-8") as f:
            json.dump({"steps": payload.steps}, f)
        logger.info("Successfully updated next steps for user %d.", payload.client_user_id)
        return {"success": True}
    except Exception as e:
        logger.error("Failed to write guest_next_steps.json: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to save homework: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("ORCHESTRATOR_PORT", "8001"))
    uvicorn.run("vm_orchestrator:app", host="127.0.0.1", port=port, reload=False)
