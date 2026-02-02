#!/usr/bin/env python3
"""
Autobot Progress Tracker Hook - Updates metrics after Bash commands.

Triggered after Bash tool use to track activity and detect patterns.
Primarily used for observability and debugging.

Hook Output Protocol:
  - Silent operation (no output unless significant)
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime


def load_json(path: Path) -> dict | None:
    """Load JSON file if it exists."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError):
            return None
    return None


def save_json(path: Path, data: dict) -> None:
    """Save data as JSON."""
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def get_project_dir() -> Path:
    """Get the project directory from environment or cwd."""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))


def main():
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, IOError):
        input_data = {}

    project_dir = get_project_dir()
    autobot_dir = project_dir / '.autobot'

    # Skip if no autobot setup
    if not autobot_dir.exists():
        sys.exit(0)

    # Load metrics
    metrics_path = autobot_dir / 'metrics.json'
    metrics = load_json(metrics_path)

    if not metrics:
        sys.exit(0)

    # Update last activity timestamp
    metrics['last_activity'] = datetime.now().isoformat()

    # Track git commits if detected
    tool_input = input_data.get('tool_input', {})
    command = tool_input.get('command', '')

    if 'git commit' in command and input_data.get('tool_result', {}).get('exit_code') == 0:
        metrics['commits'] = metrics.get('commits', 0) + 1

    # Save updated metrics
    save_json(metrics_path, metrics)


if __name__ == "__main__":
    main()
