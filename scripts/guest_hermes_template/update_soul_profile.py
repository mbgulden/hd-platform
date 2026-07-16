import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("hde-soul-update")

def update_soul():
    chart_json_path = "/workspace/charts/personal/chart_data.json"
    base_soul_path = "/home/pn/.hermes/SOUL.base.md"
    active_soul_path = "/workspace/active_soul.md"
    mounted_active_soul_path = "/home/pn/.hermes/SOUL.md"

    if not os.path.exists(chart_json_path):
        logger.warning("No personal chart data json found at %s. Skipping soul update.", chart_json_path)
        return

    try:
        with open(chart_json_path, "r") as f:
            data = json.load(f)
        
        info = data.get("info", {})
        hd_type = info.get("type", "Unknown Type")
        profile = info.get("profile", "Unknown Profile")
        authority = info.get("authority", "Unknown Authority")
        
        # Calculate open centers from chart data
        # Centers are in data['centers']. If a center has defined = False, it is open/undefined.
        open_centers = []
        centers = data.get("centers", {})
        for c_name, c_data in centers.items():
            if not c_data.get("defined", False):
                open_centers.append(c_name.capitalize())
        
        open_centers_str = ", ".join(open_centers) if open_centers else "None"
        
        # Read base soul.md
        if os.path.exists(base_soul_path):
            with open(base_soul_path, "r") as f:
                base_content = f.read()
        else:
            base_content = "# Surgical De-Programming Coaching Soul\nBase instructions not found."

        # Compile Somatic Context Block
        somatic_block = f"""

## Somatic Design Context (Dynamic Adaptation)
Your client has calculated their Human Design birth profile. Use this context to dynamically guide their deconditioning experiments:
* **Design Type**: {hd_type}
* **Profile**: {profile}
* **Inner Authority**: {authority}
* **Open/Undefined Centers**: {open_centers_str}

### Surgical Coaching Adapters
1. **Decision Pacing**: Speak directly to their Inner Authority ({authority}) as their single source of truth. Prompt them to check this somatic center before committing to any tasks.
2. **Not-Self Mapping**: Map their mental traps directly to their open centers ({open_centers_str}). Frame ego validation, head pressure, or emotional absorption not as personal flaws, but as mechanical Not-Self programming.
3. **Experiment Design**: Tailor all real-world experiments to their strategy and authority. (e.g. for Generator types, focus experiments on waiting to respond and somatic gut sounds).
"""
        # Write merged file to both the workspace copy and the mounted live Soul.
        # The live Hermes process reads /home/pn/.hermes/SOUL.md; writing only
        # /workspace/active_soul.md leaves the model on the stale base prompt.
        merged_content = base_content + somatic_block
        for path in (active_soul_path, mounted_active_soul_path):
            with open(path, "w") as f:
                f.write(merged_content)

        logger.info("Successfully updated active_soul.md and live mounted SOUL.md with Human Design profile context.")

    except Exception as exc:
        logger.exception("Failed to update active_soul.md: %s", exc)

if __name__ == "__main__":
    update_soul()
