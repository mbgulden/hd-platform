import json
import os
import logging
from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("next-step-mcp")

# Initialize FastMCP Server
mcp = FastMCP("Next Step Tracker")

DB_FILE = "/workspace/guest_next_steps.json"

def load_tasks() -> List[Dict[str, Any]]:
    """Load tasks from JSON file."""
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception as e:
        logger.error("Failed to load tasks from json: %s", e)
        return []

def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    """Save tasks to JSON file."""
    try:
        # Ensure parent directory exists (just in case)
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except Exception as e:
        logger.error("Failed to save tasks to json: %s", e)

@mcp.tool()
def add_task(title: str, status: str = "todo") -> str:
    """
    Add a new task to the guest's tracker.
    status can be: 'todo', 'in_progress', 'completed'
    """
    tasks = load_tasks()
    task_id = len(tasks) + 1
    new_task = {
        "id": task_id,
        "title": title,
        "status": status
    }
    tasks.append(new_task)
    save_tasks(tasks)
    return f"Successfully added task #{task_id}: '{title}' with status '{status}'"

@mcp.tool()
def list_tasks() -> str:
    """
    List all tasks in the guest's tracker.
    """
    tasks = load_tasks()
    if not tasks:
        return "No tasks found in your tracker."
    
    result = []
    for t in tasks:
        result.append(f"[{t['status'].upper()}] #{t['id']}: {t['title']}")
    return "\n".join(result)

@mcp.tool()
def update_task_status(task_id: int, status: str) -> str:
    """
    Update the status of a task by its numeric ID.
    status can be: 'todo', 'in_progress', 'completed'
    """
    if status not in ["todo", "in_progress", "completed"]:
        return "Error: Status must be one of: 'todo', 'in_progress', 'completed'"
        
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            old_status = t["status"]
            t["status"] = status
            save_tasks(tasks)
            return f"Successfully updated task #{task_id} status from '{old_status}' to '{status}'"
            
    return f"Error: Task #{task_id} not found."

if __name__ == "__main__":
    mcp.run()
