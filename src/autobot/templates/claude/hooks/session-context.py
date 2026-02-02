#!/usr/bin/env python3
"""
Autobot Session Context Hook - Loads state at session start.

Triggered on SessionStart to provide Claude with current task context,
progress status, and any important learnings from previous iterations.

Hook Output Protocol:
  - Print JSON with "hookSpecificOutput" to inject context
"""
import json
import os
import sys
from pathlib import Path


def load_json(path: Path) -> dict | None:
    """Load JSON file if it exists."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return None
    return None


def get_project_dir() -> Path:
    """Get the project directory from environment or cwd."""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))


def format_progress_bar(completed: int, total: int, width: int = 10) -> str:
    """Create a visual progress bar."""
    if total == 0:
        return "[" + "-" * width + "]"
    filled = int(width * completed / total)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def main():
    project_dir = get_project_dir()
    autobot_dir = project_dir / '.autobot'

    context_parts = []

    # Check if autobot is set up
    if not autobot_dir.exists():
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "Autobot: No active task. Use /init-task to start."
            }
        }))
        sys.exit(0)

    # Load current task
    task = load_json(autobot_dir / 'task.json')
    if task and task.get('id') and task.get('status') != 'idle':
        context_parts.append(f"ACTIVE TASK: {task.get('title', 'Unknown')}")
        context_parts.append(f"STATUS: {task.get('status', 'unknown')}")
    else:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "Autobot: No active task. Use /init-task to start."
            }
        }))
        sys.exit(0)

    # Load plan status
    plan = load_json(autobot_dir / 'plan.json')
    if plan and plan.get('subtasks'):
        subtasks = plan.get('subtasks', [])
        completed = len([t for t in subtasks if t.get('status') == 'completed'])
        in_progress = [t for t in subtasks if t.get('status') == 'in_progress']
        pending = [t for t in subtasks if t.get('status') == 'pending']
        total = len(subtasks)

        progress_bar = format_progress_bar(completed, total)
        context_parts.append(f"PROGRESS: {progress_bar} {completed}/{total} subtasks")

        # Show current/next subtask
        if in_progress:
            context_parts.append(f"CURRENT: {in_progress[0].get('title')}")
        elif pending:
            context_parts.append(f"NEXT: {pending[0].get('title')}")

    # Load metrics
    metrics = load_json(autobot_dir / 'metrics.json')
    if metrics:
        iteration = metrics.get('current_iteration', 0)
        max_iter = metrics.get('max_iterations', 50)
        context_parts.append(f"ITERATION: {iteration}/{max_iter}")

        # Warn about consecutive failures
        failures = metrics.get('consecutive_test_failures', 0)
        if failures > 0:
            context_parts.append(f"WARNING: {failures} consecutive test failures")

    # Check for pause flag
    if (autobot_dir / '.paused').exists():
        context_parts.append("STATUS: PAUSED (use /resume to continue)")

    # Load recent learnings from progress.md (last 300 chars)
    progress_path = autobot_dir / 'progress.md'
    if progress_path.exists():
        progress = progress_path.read_text(encoding='utf-8')
        # Find recent entries (after the header)
        if '---' in progress:
            recent = progress.split('---')[-1].strip()
            if recent and len(recent) > 10:
                # Truncate if too long
                if len(recent) > 300:
                    recent = "..." + recent[-300:]
                context_parts.append(f"\nRECENT LEARNINGS:\n{recent}")

    # Output context
    if context_parts:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(context_parts)
            }
        }))


if __name__ == "__main__":
    main()
