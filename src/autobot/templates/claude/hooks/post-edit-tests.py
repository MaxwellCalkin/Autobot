#!/usr/bin/env python3
"""
Autobot Post-Edit Test Hook - Automatically runs tests after file edits.

Triggered after Write/Edit tool use. Detects project type and runs appropriate
test command. Updates metrics and logs observations for failures.

Hook Output Protocol:
  - Print JSON with "decision": "block" to prevent continuation until fixed
  - Print JSON with "hookSpecificOutput" for informational feedback
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def load_json(path: Path) -> dict | None:
    """Load JSON file if it exists."""
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return None
    return None


def save_json(path: Path, data: dict) -> None:
    """Save data as JSON."""
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def append_jsonl(path: Path, entry: dict) -> None:
    """Append entry to JSONL file."""
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def get_project_dir() -> Path:
    """Get the project directory from environment or cwd."""
    return Path(os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd()))


def detect_test_command(project_dir: Path) -> list[str] | None:
    """Detect the appropriate test command based on project files."""
    # Node.js
    if (project_dir / 'package.json').exists():
        pkg = load_json(project_dir / 'package.json') or {}
        scripts = pkg.get('scripts', {})
        if 'test' in scripts:
            return ['npm', 'test', '--', '--passWithNoTests']

    # Python
    if (project_dir / 'pyproject.toml').exists() or (project_dir / 'setup.py').exists():
        return ['pytest', '-x', '--tb=short', '-q']

    # Rust
    if (project_dir / 'Cargo.toml').exists():
        return ['cargo', 'test', '--', '--test-threads=1']

    # Go
    if (project_dir / 'go.mod').exists():
        return ['go', 'test', './...', '-v']

    return None


def is_source_file(file_path: str) -> bool:
    """Check if file is a source code file worth testing for."""
    source_extensions = {
        '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs',  # JavaScript/TypeScript
        '.py', '.pyw',  # Python
        '.rs',  # Rust
        '.go',  # Go
        '.java', '.kt', '.kts',  # JVM
        '.c', '.cpp', '.cc', '.h', '.hpp',  # C/C++
        '.cs',  # C#
        '.rb',  # Ruby
        '.php',  # PHP
        '.swift',  # Swift
    }
    return Path(file_path).suffix.lower() in source_extensions


def main():
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError):
        input_data = {}

    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')

    # Skip non-source files
    if not file_path or not is_source_file(file_path):
        sys.exit(0)

    project_dir = get_project_dir()
    autobot_dir = project_dir / '.autobot'

    # Skip if no autobot setup
    if not autobot_dir.exists():
        sys.exit(0)

    # Detect test command
    test_cmd = detect_test_command(project_dir)

    if not test_cmd:
        # No test framework detected
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Edited {Path(file_path).name}. No test framework detected."
            }
        }))
        sys.exit(0)

    # Load metrics
    metrics_path = autobot_dir / 'metrics.json'
    metrics = load_json(metrics_path) or {
        'current_iteration': 0,
        'max_iterations': 50,
        'consecutive_test_failures': 0,
        'total_test_runs': 0,
        'total_test_passes': 0,
        'total_test_failures': 0
    }

    # Run tests
    try:
        result = subprocess.run(
            test_cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=120,
            shell=(os.name == 'nt')  # Use shell on Windows
        )
        test_passed = result.returncode == 0
        test_output = result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        test_passed = False
        test_output = "Test execution timed out after 120 seconds"

    except FileNotFoundError:
        # Test command not found - skip gracefully
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Edited {Path(file_path).name}. Test command not available: {test_cmd[0]}"
            }
        }))
        sys.exit(0)

    # Update metrics
    metrics['total_test_runs'] = metrics.get('total_test_runs', 0) + 1
    metrics['last_activity'] = datetime.now().isoformat()

    if test_passed:
        metrics['consecutive_test_failures'] = 0
        metrics['total_test_passes'] = metrics.get('total_test_passes', 0) + 1
        save_json(metrics_path, metrics)

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": f"Tests passed after editing {Path(file_path).name}. Continue with confidence."
            }
        }))

    else:
        metrics['consecutive_test_failures'] = metrics.get('consecutive_test_failures', 0) + 1
        metrics['total_test_failures'] = metrics.get('total_test_failures', 0) + 1
        save_json(metrics_path, metrics)

        # Log observation
        observation = {
            "timestamp": datetime.now().isoformat(),
            "type": "test_failure",
            "file": file_path,
            "iteration": metrics.get('current_iteration', 0),
            "consecutive_failures": metrics['consecutive_test_failures'],
            "output_snippet": test_output[:500] if test_output else "No output"
        }
        append_jsonl(autobot_dir / 'observations.jsonl', observation)

        # Truncate output for display
        display_output = test_output[:1000] if len(test_output) > 1000 else test_output

        print(json.dumps({
            "decision": "block",
            "reason": f"""Tests failed after editing {Path(file_path).name}.

FAILURE OUTPUT:
{display_output}

CONSECUTIVE FAILURES: {metrics['consecutive_test_failures']}/3 (pauses at 3)

Please analyze the failure and fix the issue before continuing.
The test output has been logged to .autobot/observations.jsonl for reference."""
        }))


if __name__ == "__main__":
    main()
