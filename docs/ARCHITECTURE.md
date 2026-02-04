# Autobot Architecture

## Overview

Autobot is a Claude Code customization system that enables autonomous, long-running development tasks with high code quality. It builds on the "Ralph" pattern but adds specialized subagents, structured observations, and deterministic quality gates.

## Core Concepts

### 1. Autonomous Loop

The autonomous loop is powered by the **Stop hook** which intercepts Claude's exit attempts:

```
┌──────────────────────────────────────────────────────────┐
│                    AUTONOMOUS LOOP                        │
│                                                          │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐  │
│  │  Start  │──▶│  Work   │──▶│  Test   │──▶│  Check  │  │
│  │  Task   │   │  on     │   │  Code   │   │  Done?  │  │
│  └─────────┘   │ Subtask │   │         │   └────┬────┘  │
│                └─────────┘   └─────────┘        │       │
│                     ▲                           │       │
│                     │         ┌─────────┐       │       │
│                     │    No   │  Stop   │  Yes  │       │
│                     └─────────│  Hook   │◀──────┘       │
│                               │ Decides │               │
│                               └────┬────┘               │
│                                    │                    │
│                               (Continue)                │
│                                    │                    │
│                                    ▼                    │
│                              Re-inject                  │
│                               Prompt                    │
└──────────────────────────────────────────────────────────┘
```

### 2. State Persistence

All state is persisted in `.autobot/` for cross-iteration memory:

```
.autobot/
├── task.json           # What we're building
├── plan.json           # How we're building it (subtasks)
├── metrics.json        # Quantitative tracking
├── progress.md         # Human-readable learnings
└── observations.jsonl  # Structured, queryable logs
```

### 3. Quality Gates

Hooks enforce quality at multiple points:

```
┌──────────────────────────────────────────────────────────┐
│                    QUALITY GATES                          │
│                                                          │
│  ┌─────────────────┐                                     │
│  │  Write/Edit     │                                     │
│  │  Tool Used      │                                     │
│  └────────┬────────┘                                     │
│           │                                              │
│           ▼                                              │
│  ┌─────────────────┐     ┌─────────────────┐            │
│  │ post-edit-tests │────▶│ Tests Pass?     │            │
│  │     (Hook)      │     └────────┬────────┘            │
│  └─────────────────┘              │                     │
│                           Yes     │     No              │
│                            │      │      │              │
│                            ▼      │      ▼              │
│                       Continue    │  Block until        │
│                                   │  fixed              │
│                                   │                     │
│                                   │  After 3 failures:  │
│                                   └──▶ Pause for review │
└──────────────────────────────────────────────────────────┘
```

### 4. Task Decomposition

Large tasks are broken into context-window-sized subtasks:

```
┌─────────────────────────────────────────────────────────┐
│                  TASK DECOMPOSITION                      │
│                                                         │
│  "Add OAuth Authentication"                             │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐                                    │
│  │    Planner      │  (Opus model)                      │
│  │   Subagent      │                                    │
│  └────────┬────────┘                                    │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────────────────────────────────┐       │
│  │  Subtask 1: Set up OAuth config      [small]│       │
│  │  Subtask 2: Create provider interface [small]│       │
│  │  Subtask 3: Implement Google provider [medium]│      │
│  │  Subtask 4: Implement GitHub provider [medium]│      │
│  │  Subtask 5: Add session management   [medium]│       │
│  │  Subtask 6: Integration tests        [small]│       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### Hooks

| Hook | Trigger | Purpose |
|------|---------|---------|
| `stop-loop.js` | Stop event | Autonomous continuation |
| `post-edit-tests.js` | After Edit/Write | Run tests, track failures |
| `session-context.js` | Session start | Load current state |
| `progress-tracker.js` | After Bash | Track activity |

### Subagents

| Agent | Model | Purpose |
|-------|-------|---------|
| `planner` | Opus | Task decomposition |
| `builder` | Sonnet | Implementation with TDD |
| `reviewer` | Sonnet | Code quality review |
| `fixer` | Sonnet | Debug test failures |

### Skills

| Skill | Auto-Invoked | Purpose |
|-------|--------------|---------|
| `task-decomposition` | By planner | Sizing and ordering strategies |
| `test-first` | By builder | TDD patterns |
| `quality-gates` | By all | Quality checkpoint reference |

### Commands

| Command | User Action | Effect |
|---------|-------------|--------|
| `/init-task` | Start new task | Initialize and begin loop |
| `/status` | Check progress | Display dashboard |
| `/pause` | Pause loop | Create .paused flag |
| `/resume` | Resume loop | Remove .paused flag |
| `/abort` | Stop task | Archive and reset |

## Data Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                         DATA FLOW                                 │
│                                                                  │
│  User                                                            │
│    │                                                             │
│    │  /init-task "Add feature X"                                │
│    ▼                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Planner   │───▶│  plan.json  │───▶│   Builder   │          │
│  │  (decompse) │    │  (subtasks) │    │ (implement) │          │
│  └─────────────┘    └─────────────┘    └──────┬──────┘          │
│                                               │                  │
│                                               ▼                  │
│                                        Write/Edit files          │
│                                               │                  │
│                                               ▼                  │
│                     ┌─────────────┐    ┌─────────────┐          │
│                     │  post-edit  │◀───│   Hook      │          │
│                     │   -tests    │    │  Triggered  │          │
│                     └──────┬──────┘    └─────────────┘          │
│                            │                                     │
│                            ▼                                     │
│                     ┌─────────────┐                              │
│                     │ Run Tests   │                              │
│                     └──────┬──────┘                              │
│                            │                                     │
│              ┌─────────────┴─────────────┐                      │
│              │                           │                      │
│         Tests Pass              Tests Fail                      │
│              │                           │                      │
│              ▼                           ▼                      │
│       Update metrics            Update metrics                  │
│       Continue work             Log observation                 │
│              │                  Block until fixed               │
│              │                           │                      │
│              └───────────┬───────────────┘                      │
│                          │                                      │
│                          ▼                                      │
│                   ┌─────────────┐                               │
│                   │  stop-loop  │                               │
│                   │    Hook     │                               │
│                   └──────┬──────┘                               │
│                          │                                      │
│           ┌──────────────┴──────────────┐                      │
│           │                             │                      │
│    More subtasks?                All done?                     │
│           │                             │                      │
│           ▼                             ▼                      │
│    Re-inject prompt              Allow exit                    │
│    for next subtask              Task complete                 │
│                                                                │
└──────────────────────────────────────────────────────────────────┘
```

## Exit Conditions

The loop terminates when any of these conditions are met:

1. **Completion** - All subtasks done + EXIT_SIGNAL in progress.md
2. **Safety Limit** - Max iterations reached (default: 50)
3. **Blocking Failure** - 3+ consecutive test failures
4. **User Action** - /pause or /abort command

## Improvements Over Ralph

| Aspect | Ralph | Autobot |
|--------|-------|---------|
| Continuation Signal | Iteration count | Test results + subtask status |
| Agent Model | Single prompt | Specialized subagents |
| Observations | Append-only text | Structured JSONL |
| Quality Gates | Prompt-based | Hook-enforced |
| Failure Handling | Manual | Auto-pause at 3 failures |

## Configuration

### settings.json Structure

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep", "Bash(npm test:*)"],
    "deny": ["Bash(rm -rf:*)"]
  },
  "hooks": {
    "Stop": [{ "hooks": [{ "type": "command", "command": "..." }] }],
    "PostToolUse": [{ "matcher": "Edit|Write", "hooks": [...] }]
  }
}
```

### Customization Points

1. **Max Iterations** - `.autobot/metrics.json` → `max_iterations`
2. **Test Command** - Auto-detected, or customize hooks
3. **Subagent Models** - Edit agent .md files
4. **Quality Thresholds** - Edit hook scripts
