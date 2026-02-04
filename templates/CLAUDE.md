# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is Autobot?

Autobot enables Claude Code to autonomously complete long-running development tasks by:
1. **Decomposing** large tasks into context-window-sized subtasks
2. **Persisting** state and learnings across iterations
3. **Enforcing** quality gates through hooks (tests must pass before continuing)
4. **Recovering** gracefully from failures (pause after 3 consecutive failures)

## Philosophy

- **Tests are first-class citizens** - Write tests before implementation (TDD)
- **Small, verifiable steps** - Each subtask must fit in one context window
- **Quality gates are mandatory** - All tests must pass before marking complete
- **Learn and adapt** - Observations persist in `.autobot/progress.md`
- **Fail fast, recover gracefully** - Stop on blocking issues, not minor failures

## Architecture

```
.autobot/           # Runtime state (preserved across iterations)
├── task.json       # Current task definition
├── plan.json       # Decomposed subtasks with status
├── progress.md     # Append-only learning log
├── observations.jsonl  # Structured queryable logs
└── metrics.json    # Quantitative tracking

.claude/            # Claude Code customization
├── settings.json   # Hooks, permissions
├── hooks/          # Node.js scripts for automation
├── agents/         # Specialized subagent definitions
├── commands/       # User-invoked slash commands
└── skills/         # Auto-invoked capabilities
```

## Commands

| Command | Description |
|---------|-------------|
| `/init-task <description>` | Start new autonomous task |
| `/status` | View progress dashboard |
| `/pause` | Pause autonomous loop |
| `/resume` | Resume paused loop |
| `/abort` | Emergency stop with state preservation |

## Hooks (Automatic)

- **Stop** - Checks for incomplete subtasks, re-injects prompt to continue
- **PostToolUse (Edit/Write)** - Runs tests after code changes
- **SessionStart** - Loads `.autobot/` state into context

## Quality Standards

1. Run tests after every code change (automatic via hooks)
2. All tests must pass before marking subtask complete
3. No linting errors before commits
4. Public APIs require documentation
5. Follow existing code patterns in the codebase

## Test Commands

Auto-detected by project type:
- **Node.js**: `npm test`
- **Python**: `pytest -x --tb=short`
- **Rust**: `cargo test`
- **Go**: `go test ./...`

## State Files

### task.json
```json
{
  "id": "task-{timestamp}",
  "title": "Short title",
  "description": "Full description",
  "status": "in_progress"
}
```

### plan.json
```json
{
  "subtasks": [
    {
      "id": "st-001",
      "title": "Subtask title",
      "status": "pending|in_progress|completed",
      "acceptance_criteria": ["..."]
    }
  ]
}
```

### metrics.json
```json
{
  "current_iteration": 5,
  "max_iterations": 50,
  "consecutive_test_failures": 0
}
```

## Key Gotchas

- Never edit `.autobot/` files directly - use the provided commands
- Always check `.autobot/progress.md` for learned patterns before starting
- If tests fail 3 times consecutively, the loop pauses for human review
- Max 50 iterations by default (configurable in metrics.json)
- Each subtask should be completable in ~30 minutes of focused work

## Exit Conditions

The autonomous loop stops when:
1. All subtasks in `plan.json` are marked `completed`
2. `progress.md` contains `EXIT_SIGNAL: COMPLETE`
3. Max iterations reached (safety limit)
4. 3+ consecutive test failures (requests human review)
5. User runs `/pause` or `/abort`

## Subagents

| Agent | Model | Purpose |
|-------|-------|---------|
| planner | Opus | Task decomposition |
| builder | Sonnet | Implementation with TDD |
| reviewer | Sonnet | Code review |
| fixer | Sonnet | Debug test failures |

## Quick Start

```bash
# Start a new task
/init-task "Add user authentication with OAuth support"

# Check progress at any time
/status

# Pause if needed
/pause

# Resume when ready
/resume
```

@.autobot/progress.md for learned patterns
@.autobot/plan.json for current subtask status
