#!/usr/bin/env python3
"""
Autobot Stop Hook - Controls the autonomous loop continuation.

This is the heart of Autobot. It intercepts Claude's exit attempts and
determines whether to continue working based on task status and quality gates.

Hook Output Protocol:
  - Print JSON with "decision": "block" to prevent stop and re-inject prompt
  - Print JSON without "decision" or exit code 0 to allow stop
  - Exit code 2 for errors that should be shown to Claude
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

    # Ensure autobot directory exists
    if not autobot_dir.exists():
        # No autobot setup - allow stop
        sys.exit(0)

    # Load state files
    task = load_json(autobot_dir / 'task.json')
    plan = load_json(autobot_dir / 'plan.json')
    metrics = load_json(autobot_dir / 'metrics.json') or {
        'current_iteration': 0,
        'max_iterations': 50,
        'consecutive_test_failures': 0
    }

    # Check if there's an active task
    if not task or task.get('status') == 'idle' or not task.get('id'):
        # No active task - allow stop
        sys.exit(0)

    # Check for pause flag
    if (autobot_dir / '.paused').exists():
        print(json.dumps({
            "continue": False,
            "stopReason": "Task paused. Use /resume to continue."
        }))
        sys.exit(0)

    # Check max iterations (safety limit)
    current_iteration = metrics.get('current_iteration', 0)
    max_iterations = metrics.get('max_iterations', 50)

    if current_iteration >= max_iterations:
        print(json.dumps({
            "continue": False,
            "stopReason": f"Safety limit reached: {max_iterations} iterations. Review progress and use /resume to continue."
        }))
        sys.exit(0)

    # Check for blocking failures (3+ consecutive test failures)
    consecutive_failures = metrics.get('consecutive_test_failures', 0)

    if consecutive_failures >= 3:
        print(json.dumps({
            "decision": "block",
            "reason": f"""PAUSE: {consecutive_failures} consecutive test failures detected.

Please review:
1. .autobot/observations.jsonl for failure patterns
2. .autobot/progress.md for any related learnings
3. The test output to understand the root cause

Options:
- Fix the issue and tests will auto-run
- Use /abort to stop and preserve state
- Use /pause to pause and resume later

What would you like to do?"""
        }))
        sys.exit(0)

    # Check subtask completion
    subtasks = plan.get('subtasks', []) if plan else []
    incomplete = [t for t in subtasks if t.get('status') != 'completed']
    completed = [t for t in subtasks if t.get('status') == 'completed']

    # Check for EXIT_SIGNAL in progress
    progress_path = autobot_dir / 'progress.md'
    progress_content = progress_path.read_text(encoding='utf-8') if progress_path.exists() else ""

    if "EXIT_SIGNAL: COMPLETE" in progress_content and not incomplete:
        # Task fully complete
        task['status'] = 'completed'
        save_json(autobot_dir / 'task.json', task)

        print(json.dumps({
            "continue": False,
            "stopReason": f"Task completed successfully! {len(completed)} subtasks finished."
        }))
        sys.exit(0)

    # If there are incomplete subtasks, continue
    if incomplete:
        next_task = incomplete[0]

        # Increment iteration counter
        metrics['current_iteration'] = current_iteration + 1
        metrics['last_activity'] = datetime.now().isoformat()
        save_json(autobot_dir / 'metrics.json', metrics)

        # Build continuation prompt
        prompt = f"""Continue working on the current task.

PROGRESS: {len(completed)}/{len(subtasks)} subtasks completed
ITERATION: {current_iteration + 1}/{max_iterations}

CURRENT SUBTASK: {next_task.get('title')}
DESCRIPTION: {next_task.get('description', 'No description')}
ACCEPTANCE CRITERIA:
{chr(10).join('- ' + c for c in next_task.get('acceptance_criteria', ['Complete the subtask']))}

INSTRUCTIONS:
1. Review .autobot/progress.md for any learned patterns
2. Write tests FIRST if this involves new functionality
3. Implement the change
4. Tests will auto-run after edits
5. If tests pass, update .autobot/plan.json to mark subtask complete
6. If all subtasks done, write "EXIT_SIGNAL: COMPLETE" to .autobot/progress.md

Quality over speed. Small, verifiable steps."""

        print(json.dumps({
            "decision": "block",
            "reason": prompt
        }))
        sys.exit(0)

    # No more subtasks but no EXIT_SIGNAL - prompt to complete
    print(json.dumps({
        "decision": "block",
        "reason": """All subtasks appear complete but EXIT_SIGNAL not found.

Please:
1. Verify all acceptance criteria are met
2. Run the full test suite one more time
3. If everything passes, append "EXIT_SIGNAL: COMPLETE" to .autobot/progress.md

This ensures proper task completion tracking."""
    }))


if __name__ == "__main__":
    main()
