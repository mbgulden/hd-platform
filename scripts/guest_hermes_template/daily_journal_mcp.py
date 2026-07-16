from mcp.server.fastmcp import FastMCP
import sqlite3
import os

# Create FastMCP server instance
mcp = FastMCP("Daily Journal MCP")

DB_PATH = "/workspace/guest_journal.db"
COACH_VIEW_DIR = "/workspace/coach_view"
PEOPLE_DIR = "/workspace/people"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def write_coach_event(event_type: str, payload: dict) -> None:
    """Write a small JSONL event for coach/backend review without touching chat flow."""
    try:
        import json, datetime
        os.makedirs(COACH_VIEW_DIR, exist_ok=True)
        event = {
            "created_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "event_type": event_type,
            **payload,
        }
        with open(os.path.join(COACH_VIEW_DIR, "events.jsonl"), "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def load_chart_overrides(subject_name: str) -> dict:
    """Return per-person corrected Human Design fields to merge into generated chart/report payloads."""
    try:
        import json
        profile_path = os.path.join(PEOPLE_DIR, subject_name or "", "profile.json")
        if not os.path.exists(profile_path):
            return {}
        with open(profile_path) as f:
            profile = json.load(f)
        overrides = profile.get("chart_overrides") or {}
        return overrides if isinstance(overrides, dict) else {}
    except Exception:
        return {}


def write_person_profile(subject_name: str, name: str, birth_input: dict, relationship_type: str, chart_record: dict, manifest: dict) -> None:
    """Persist durable per-person birth details and chart links for reuse."""
    try:
        import json, datetime
        slug = subject_name or "person"
        person_dir = os.path.join(PEOPLE_DIR, slug)
        charts_dir = os.path.join(person_dir, "charts", relationship_type)
        os.makedirs(charts_dir, exist_ok=True)
        profile_path = os.path.join(person_dir, "profile.json")
        existing = {}
        if os.path.exists(profile_path):
            with open(profile_path) as f:
                existing = json.load(f)
        charts = existing.get("charts") or []
        chart_link = {
            "created_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "relationship_type": relationship_type,
            "chart_json_path": manifest.get("chart_json_path"),
            "coach_manifest_path": os.path.join(manifest.get("chart_json_path", "").rsplit("/", 1)[0], "coach_manifest.json") if manifest.get("chart_json_path") else "",
            "pdf_path": manifest.get("pdf_path"),
            "image_path": manifest.get("image_path"),
            "type": manifest.get("type"),
            "authority": manifest.get("authority"),
            "profile": manifest.get("profile"),
        }
        charts.append(chart_link)
        profile = dict(existing)
        profile.update({
            "slug": slug,
            "subject_name": slug,
            "name": name,
            "birth_input": birth_input,
            "latest_chart": chart_link,
            "charts": charts[-25:],
            "updated_at": chart_link["created_at"],
        })
        with open(profile_path, "w") as f:
            json.dump(profile, f, indent=2)
        # Also place a small latest chart snapshot in the person folder.
        with open(os.path.join(person_dir, "latest_chart_data.json"), "w") as f:
            json.dump(chart_record, f, indent=2)
        index_path = os.path.join(PEOPLE_DIR, "index.json")
        index = {"default_person": "", "people": {}}
        if os.path.exists(index_path):
            with open(index_path) as f:
                index = json.load(f)
        index.setdefault("people", {})[slug] = {
            "name": name,
            "slug": slug,
            "profile_path": profile_path,
            "updated_at": profile["updated_at"],
        }
        if relationship_type == "personal" and not index.get("default_person"):
            index["default_person"] = slug
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2, sort_keys=True)
    except Exception:
        pass

def normalize_defined_channels_for_renderer(chart_data: dict) -> dict:
    """Return a copy with defined_channels as renderer-friendly dicts."""
    import re
    normalized = dict(chart_data or {})
    channels = []
    for ch in (chart_data or {}).get("defined_channels", []) or []:
        if isinstance(ch, dict):
            channels.append(ch)
            continue
        text = str(ch)
        m = re.match(r"\s*(\d+)\s*-\s*(\d+)\s*(?:\((.*)\))?", text)
        if m:
            channels.append({"gates": [int(m.group(1)), int(m.group(2))], "name": (m.group(3) or "").strip()})
    normalized["defined_channels"] = channels
    return normalized


# Initialize local database
init_db()

@mcp.tool()
def add_journal_entry(entry_text: str) -> str:
    """Record a new journaling entry.
    
    Args:
        entry_text: The content of the journal entry
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO journal_entries (entry_text) VALUES (?)", (entry_text,))
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    write_coach_event("journal_entry", {"entry_id": entry_id, "entry_text": entry_text})
    return "Success: Recorded journal entry."

@mcp.tool()
def list_journal_entries(limit: int = 10) -> str:
    """List recent journaling entries.
    
    Args:
        limit: Maximum number of entries to retrieve
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, entry_text FROM journal_entries ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "No journal entries found."
    out = []
    for r in rows:
        out.append(f"[{r[1]}] (ID: {r[0]}): {r[2]}")
    return "\n".join(out)

@mcp.tool()
def search_journal(query: str) -> str:
    """Search journal entries for a query.
    
    Args:
        query: Search term
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, entry_text FROM journal_entries WHERE entry_text LIKE ?", (f"%{query}%",))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return f"No journal entries matched the query '{query}'."
    out = []
    for r in rows:
        out.append(f"[{r[1]}] (ID: {r[0]}): {r[2]}")
    return "\n".join(out)

@mcp.tool()
def generate_human_design_chart(
    birth_date: str, 
    birth_time: str, 
    location: str, 
    name: str = "Sanctuary Guest",
    relationship_type: str = "personal",
    subject_name: str = "user"
) -> str:
    """Calculate and generate the Human Design chart image and PDF report.
    
    Args:
        birth_date: Date of birth. Accept user-facing MM/DD/YYYY or natural language, but pass this tool ISO YYYY-MM-DD internally.
        birth_time: Time of birth in HH:MM 24-hour format after parsing the user's natural time expression
        location: City/Location of birth (e.g. "Seattle, WA" or "London, UK")
        name: User's name
        relationship_type: The relationship mapping type (personal, family, friends, composite)
        subject_name: Name of the chart subject (default: user)
    """
    import sys
    import os
    import httpx
    sys.path.append("/app/OpenHumanDesignMCP/hd-mcp-server/src")
    try:
        from mcp_server import resolve_geo, calculate_chart_detailed
        from image_generator import render_bodygraph
    except ImportError as e:
        return f"Error: Human Design libraries not found in container path: {e}"

    # 1. Resolve Location Coordinates
    try:
        geo = resolve_geo(location)
        if not geo or "lat" not in geo:
            return f"Error: Could not resolve location '{location}'"
        lat = geo["lat"]
        lon = geo["lon"]
        tz = geo.get("tz") or geo.get("timezone") or "UTC"
    except Exception as e:
        return f"Error resolving location coordinates: {e}"

    # 2. Compute chart data locally through OpenHumanDesignMCP, then ask the
    # host reports server for the PDF.  The report endpoint returns a summary
    # and host PDF path, not the full chart payload, so keeping the local chart
    # avoids a brittle dependency on response shape.
    try:
        year, month, day = [int(x) for x in birth_date.split("-")]
        hour_part, minute_part = [int(x) for x in birth_time.split(":")]
        decimal_hour = hour_part + minute_part / 60.0
        chart_data = calculate_chart_detailed(name, year, month, day, decimal_hour, location, lat, lon)
        chart_overrides = load_chart_overrides(subject_name)
        if chart_overrides:
            chart_data.update(chart_overrides)
    except Exception as e:
        return f"Failed to calculate chart data: {e}"

    url = "http://host.docker.internal:8081/api/compute"
    api_key = os.getenv("HDE_API_KEY", "hde_api_key_change_me_in_production")
    
    payload = {
        "name": name,
        "report": "natal",
        "birthdate": birth_date,
        "birthtime": birth_time,
        "location": location,
        "lat": lat,
        "lon": lon,
        "timezone": tz,
        "email": "",
        "chart_overrides": chart_overrides,
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }

    import datetime
    import json
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() else "_" for c in name).strip("_")
    pdf_filename = f"report_{safe_name}_{timestamp}.pdf"
    png_filename = f"chart_{safe_name}_{timestamp}.png"
    
    charts_dir = f"/workspace/charts/{relationship_type}/{subject_name}"
    os.makedirs(charts_dir, exist_ok=True)
    dest_pdf_path = os.path.join(charts_dir, pdf_filename)
    dest_png_path = os.path.join(charts_dir, png_filename)

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code != 200:
                return f"Error from reports server ({resp.status_code}): {resp.text}"
            result = resp.json()
            remote_pdf_path = result.get("pdf_path")
            
            # Copy the PDF report into /workspace so the Telegram router can
            # attach it. In Docker, /tmp/hde-reports is mounted from the host at
            # the same path. Fall back to HTTP only if the server exposes it.
            if remote_pdf_path and os.path.exists(remote_pdf_path):
                import shutil
                shutil.copy2(remote_pdf_path, dest_pdf_path)
            elif remote_pdf_path:
                filename = os.path.basename(remote_pdf_path)
                download_url = f"http://host.docker.internal:8081/reports/{filename}"
                get_resp = client.get(download_url)
                if get_resp.status_code == 200:
                    with open(dest_pdf_path, "wb") as f:
                        f.write(get_resp.content)
                else:
                    return f"Chart data calculated, but the PDF report was not attachable yet ({get_resp.status_code})."
            else:
                return "Chart data calculated, but the calculations server did not return a PDF path."
    except Exception as e:
        return f"Failed to connect to reports server: {e}"

    # 4. Render Bodygraph Image locally (no network egress needed!)
    image_path_for_router = dest_png_path
    try:
        render_bodygraph(normalize_defined_channels_for_renderer(chart_data), dest_png_path)
    except Exception as e:
        image_path_for_router = ""
        # The PDF + chart JSON are still valid. Some chart payload shapes do not
        # match the local PNG renderer; do not fail the user-facing chart flow
        # just because the optional image preview could not be rendered.
        import logging
        logging.getLogger("daily-journal-mcp").warning("Chart PNG render skipped: %s", e)

    # 5. Write chart data JSON for backend coach review and future comparisons.
    # Personal charts also update the live Soul with design context.
    try:
        chart_record = dict(chart_data)
        chart_record["birth_input"] = {
            "birth_date": birth_date,
            "birth_time": birth_time,
            "location": location,
            "timezone": tz,
            "latitude": lat,
            "longitude": lon,
        }
        with open(os.path.join(charts_dir, "chart_data.json"), "w") as f:
            json.dump(chart_record, f, indent=2)
        if relationship_type == "personal":
            personal_dir = "/workspace/charts/personal"
            os.makedirs(personal_dir, exist_ok=True)
            with open(os.path.join(personal_dir, "chart_data.json"), "w") as f:
                json.dump(chart_record, f, indent=2)
            import subprocess
            subprocess.run(["python3", "/workspace/update_soul_profile.py"], check=True)
    except Exception:
        pass

    manifest = {
        "relationship_type": relationship_type,
        "subject_name": subject_name,
        "name": name,
        "birth_date": birth_date,
        "birth_time": birth_time,
        "location": location,
        "timezone": tz,
        "chart_json_path": os.path.join(charts_dir, "chart_data.json"),
        "pdf_path": dest_pdf_path,
        "image_path": image_path_for_router,
        "type": chart_data.get("hd_type", "Unknown"),
        "strategy": chart_data.get("strategy", "Unknown"),
        "authority": chart_data.get("authority", "Unknown"),
        "profile": chart_data.get("profile", "Unknown"),
    }
    try:
        with open(os.path.join(charts_dir, "coach_manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)
    except Exception:
        pass
    write_person_profile(subject_name, name, chart_record.get("birth_input", {}), relationship_type, chart_record, manifest)
    write_coach_event("chart_generated", manifest)

    return f"""Successfully generated chart!
__CHART_FILE_PATHS__:image_path={image_path_for_router};pdf_path={dest_pdf_path}
I built the chart. Here are the anchor points to start with:
- Type: {chart_data.get('hd_type', 'Unknown')}
- Strategy: {chart_data.get('strategy', 'Unknown')}
- Inner Authority: {chart_data.get('authority', 'Unknown')}
- Profile: {chart_data.get('profile', 'Unknown')}
"""

if __name__ == "__main__":
    mcp.run()

