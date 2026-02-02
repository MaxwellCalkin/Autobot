# Autobot Hooks Reference

## Overview

Hooks are Python scripts that execute automatically at specific points in the Claude Code workflow. They enable automation, quality enforcement, and the autonomous loop.

## Hook Events

| Event | When Triggered | Use Case |
|-------|----------------|----------|
| `SessionStart` | New session begins | Load context, display status |
| `PreToolUse` | Before a tool runs | Validation, blocking |
| `PostToolUse` | After a tool completes | Testing, formatting, tracking |
| `Stop` | Claude finishes response | Autonomous continuation |

## Hook Protocol

### Input

Hooks receive JSON on stdin:

```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/file.ts",
    "content": "..."
  },
  "tool_result": {
    "exit_code": 0,
    "output": "..."
  }
}
```

### Output

Hooks communicate via stdout JSON:

```json
// Allow operation, provide context
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "Tests passed!"
  }
}

// Block operation, re-inject prompt
{
  "decision": "block",
  "reason": "Tests failed. Please fix before continuing."
}

// Allow stop
{
  "continue": false,
  "stopReason": "Task completed successfully."
}
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (check stdout for decision) |
| 1 | Error (logged but continues) |
| 2 | Deny/block operation |

## Autobot Hooks

### stop-loop.py

**Event:** Stop

**Purpose:** Controls the autonomous continuation loop.

**Logic:**
1. Check for active task in `.autobot/task.json`
2. Check for `.paused` flag
3. Check max iterations limit
4. Check for blocking failures (3+ consecutive)
5. Check subtask completion
6. If incomplete: re-inject prompt for next subtask
7. If complete: allow exit

**Configuration:**
- `max_iterations`: Safety limit (default: 50)
- Failure threshold: 3 consecutive test failures

### post-edit-tests.py

**Event:** PostToolUse (matcher: Edit|Write)

**Purpose:** Automatically run tests after code changes.

**Logic:**
1. Check if file is a source file
2. Detect test framework (npm/pytest/cargo/go)
3. Run test suite
4. Update metrics in `.autobot/metrics.json`
5. If pass: provide positive feedback
6. If fail: block and log observation

**Supported Frameworks:**
- Node.js: `npm test -- --passWithNoTests`
- Python: `pytest -x --tb=short -q`
- Rust: `cargo test`
- Go: `go test ./...`

### session-context.py

**Event:** SessionStart

**Purpose:** Load Autobot state at session start.

**Logic:**
1. Load task, plan, metrics from `.autobot/`
2. Format progress summary
3. Include warnings (failures, pause state)
4. Display recent learnings from progress.md

**Output Example:**
```
ACTIVE TASK: Add user authentication
STATUS: in_progress
PROGRESS: [######----] 3/5 subtasks
ITERATION: 12/50
CURRENT: Implement OAuth providers
```

### progress-tracker.py

**Event:** PostToolUse (matcher: Bash)

**Purpose:** Track activity metrics.

**Logic:**
1. Update last_activity timestamp
2. Track git commits if detected
3. Minimal overhead (silent operation)

## Configuration in settings.json

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-context.py\"",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/post-edit-tests.py\"",
            "timeout": 300
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/stop-loop.py\"",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Customizing Hooks

### Change Test Command

Edit `post-edit-tests.py`:

```python
def detect_test_command(project_dir: Path) -> list[str] | None:
    # Add your custom detection logic
    if (project_dir / 'custom-test-config.json').exists():
        return ['custom-test-runner', '--fast']
    # ... existing logic
```

### Change Failure Threshold

Edit `stop-loop.py`:

```python
# Change from 3 to 5 consecutive failures
if consecutive_failures >= 5:
    # ... pause logic
```

### Add Pre-Commit Hook

Add to `settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/validate-command.py\"",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

## Debugging Hooks

### Enable Debug Output

Run Claude Code with `--debug` flag to see hook execution.

### Manual Testing

Test hooks directly:

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "test.ts"}}' | python .claude/hooks/post-edit-tests.py
```

### Check Hook Logs

Hooks write observations to `.autobot/observations.jsonl`:

```bash
python .claude/hooks/analyze-observations.py --recent 10
```

## Troubleshooting

### Hook Not Running

1. Check `settings.json` syntax
2. Verify Python is available in PATH
3. Check file permissions
4. Look for errors in Claude Code output

### Tests Not Running

1. Verify test framework is installed
2. Check `detect_test_command()` logic
3. Test command manually first

### Loop Not Continuing

1. Check `.autobot/task.json` status
2. Check for `.paused` flag
3. Check iteration count vs max
4. Check consecutive failure count
