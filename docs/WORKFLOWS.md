# Autobot Workflows

## Quick Start

### Starting a New Task

```bash
# Initialize a task with description
/init-task Add user authentication with OAuth support for Google and GitHub

# Autobot will:
# 1. Create task definition
# 2. Use planner subagent to decompose into subtasks
# 3. Begin working on first subtask
# 4. Continue autonomously until complete
```

### Monitoring Progress

```bash
# Check status at any time
/status

# Output:
# ╔═════════════════════════════════════════════════════╗
# ║  Task: Add user authentication                      ║
# ║  Progress: [######----] 3/5 subtasks (60%)         ║
# ║  Tests: ✓ 23 passed | ✗ 0 failed                   ║
# ╚═════════════════════════════════════════════════════╝
```

### Pausing and Resuming

```bash
# Need to step away?
/pause

# Come back later
/resume
```

### Emergency Stop

```bash
# Something went wrong?
/abort

# State is archived, can review and restart
```

## Common Workflows

### 1. Feature Development

```
User: /init-task Add dark mode toggle to settings page

Autobot:
├── Subtask 1: Add theme context and provider
│   ├── Write tests for theme toggle
│   ├── Implement ThemeProvider
│   └── ✓ Tests pass
├── Subtask 2: Create DarkModeToggle component
│   ├── Write component tests
│   ├── Implement component
│   └── ✓ Tests pass
├── Subtask 3: Add CSS variables for themes
│   ├── Define light/dark tokens
│   ├── Apply to existing styles
│   └── ✓ Tests pass
├── Subtask 4: Persist theme preference
│   ├── Add localStorage persistence
│   ├── Test persistence
│   └── ✓ Tests pass
└── Subtask 5: Integration testing
    ├── E2E tests for toggle
    └── ✓ All tests pass

EXIT_SIGNAL: COMPLETE
```

### 2. Bug Fix

```
User: /init-task Fix login redirect loop when session expires

Autobot:
├── Subtask 1: Reproduce and write failing test
│   ├── Write test that demonstrates bug
│   └── ✓ Test fails (expected)
├── Subtask 2: Fix session expiry handling
│   ├── Identify root cause in auth middleware
│   ├── Implement fix
│   └── ✓ Test passes
└── Subtask 3: Add regression tests
    ├── Additional edge case tests
    └── ✓ All tests pass

EXIT_SIGNAL: COMPLETE
```

### 3. Refactoring

```
User: /init-task Migrate from Redux to Zustand for state management

Autobot:
├── Subtask 1: Set up Zustand and create store structure
├── Subtask 2: Migrate user slice
├── Subtask 3: Migrate cart slice
├── Subtask 4: Migrate UI slice
├── Subtask 5: Remove Redux dependencies
└── Subtask 6: Verify all existing tests pass

EXIT_SIGNAL: COMPLETE
```

## Handling Failures

### Test Failures

When tests fail, Autobot:
1. Blocks until fixed (won't continue with failing tests)
2. Provides error output
3. Logs observation for pattern detection
4. After 3 consecutive failures: pauses for review

```
Tests failed after editing auth.service.ts.

FAILURE OUTPUT:
Expected: "authenticated"
Received: "pending"

CONSECUTIVE FAILURES: 2/3 (pauses at 3)

Please analyze the failure and fix the issue.
```

### Stuck on a Subtask

If progress stalls:
1. Check `.autobot/observations.jsonl` for patterns
2. Review `.autobot/progress.md` for learnings
3. Use `/pause` to stop and investigate
4. Consider `/abort` if approach is wrong

### Human Review Requested

When Autobot pauses for review:

```
PAUSE: 3 consecutive test failures detected.

Please review:
1. .autobot/observations.jsonl for failure patterns
2. .autobot/progress.md for any related learnings
3. The test output to understand the root cause

Options:
- Fix the issue and tests will auto-run
- Use /abort to stop and preserve state
- Use /pause to pause and resume later
```

## Best Practices

### Writing Good Task Descriptions

**Good:**
```
/init-task Add user authentication with email/password login,
including signup, login, logout, and password reset flows.
Use bcrypt for password hashing and JWT for sessions.
```

**Bad:**
```
/init-task Add auth
```

### Checking Progress Regularly

- Use `/status` periodically
- Watch for consecutive failures building up
- Review observations for emerging patterns

### Knowing When to Pause

Pause when:
- Consecutive failures reach 2
- You need to clarify requirements
- You want to review code before continuing
- Something seems fundamentally wrong

### Reviewing Completed Work

After task completion:
1. Review `.autobot/progress.md` for learnings
2. Run full test suite manually
3. Check code quality with reviewer subagent
4. Archive observations for future reference

## Integration with TDD

Autobot works best with test-driven development:

```
Subtask Workflow:
1. Write failing test (RED)
   └── post-edit-tests hook runs
   └── Test fails (expected at this stage)

2. Write implementation (GREEN)
   └── post-edit-tests hook runs
   └── Test passes ✓

3. Refactor if needed
   └── post-edit-tests hook runs
   └── Tests still pass ✓

4. Mark subtask complete
```

## Using Subagents

### Planner (Automatic)

Used automatically by `/init-task`:
```
/init-task Complex feature description

# Planner subagent decomposes into subtasks
# Returns structured plan to .autobot/plan.json
```

### Reviewer (Manual)

Use after completing work:
```
# Review specific subtask
Ask the reviewer subagent to review the authentication implementation

# Reviewer provides structured feedback:
# - Critical issues
# - Warnings
# - Suggestions
# - Observations
```

### Fixer (Automatic)

Used when tests fail repeatedly:
```
# After 2 failures, builder may invoke fixer:
# - Analyzes test output
# - Identifies root cause
# - Attempts fix
# - Documents pattern
```

## Observability

### Metrics Dashboard

```bash
/status

# Shows:
# - Subtask progress
# - Iteration count
# - Test statistics
# - Consecutive failures
# - Recent activity
```

### Observation Mining

```bash
# Find test failure patterns
python .claude/hooks/analyze-observations.py --type test_failure

# Find learned patterns
python .claude/hooks/analyze-observations.py --type pattern

# Get summary
python .claude/hooks/analyze-observations.py --summary
```

### Progress Log

`.autobot/progress.md` contains human-readable learnings:

```markdown
## Task Started: 2024-01-30T10:00:00Z
**Title:** Add user authentication
**Subtasks:** 5

---

## Learned: 2024-01-30T10:30:00Z
This codebase uses factory functions instead of classes for services.
Applied pattern to AuthService implementation.

---

## Completed Subtask: OAuth config
Tests: 5 passed
Files: src/config/oauth.ts, src/config/oauth.test.ts

---
```
