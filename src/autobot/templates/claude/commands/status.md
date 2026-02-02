# Autobot Status Dashboard

Display current task progress, metrics, and recent activity.

## Usage

```
/status
```

## Instructions

When this command is invoked, read the state files and display a comprehensive dashboard:

1. **Load State Files:**
   - `.autobot/task.json` - Current task
   - `.autobot/plan.json` - Subtask breakdown
   - `.autobot/metrics.json` - Quantitative metrics
   - `.autobot/observations.jsonl` - Recent observations (last 5)
   - `.autobot/progress.md` - Recent learnings

2. **Display Dashboard:**

```
╔═══════════════════════════════════════════════════════════════╗
║  AUTOBOT STATUS                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  Task: {task.title}                                           ║
║  Status: {task.status}                                        ║
║                                                               ║
║  Progress: {progress_bar} {completed}/{total} ({percent}%)    ║
║  Iteration: {current}/{max}                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  SUBTASKS                                                     ║
║  ✓ {completed_subtask_1}                                      ║
║  ✓ {completed_subtask_2}                                      ║
║  → {current_subtask}  [IN PROGRESS]                           ║
║  ○ {pending_subtask_1}                                        ║
║  ○ {pending_subtask_2}                                        ║
╠═══════════════════════════════════════════════════════════════╣
║  QUALITY METRICS                                              ║
║  Tests: ✓ {passes} passed | ✗ {failures} failed               ║
║  Consecutive Failures: {consecutive}/3                        ║
╠═══════════════════════════════════════════════════════════════╣
║  RECENT ACTIVITY                                              ║
║  • [{time}] {observation_1}                                   ║
║  • [{time}] {observation_2}                                   ║
║  • [{time}] {observation_3}                                   ║
╚═══════════════════════════════════════════════════════════════╝
```

3. **Progress Bar:**
   ```
   Completed 3/5: [######----] 60%
   ```

4. **Status Indicators:**
   - ✓ = completed
   - → = in_progress
   - ○ = pending
   - ⚠ = blocked (3+ failures)
   - ⏸ = paused

5. **If No Active Task:**
   ```
   No active task. Use /init-task to start a new task.
   ```

6. **If Paused:**
   Show "(PAUSED)" and remind about /resume

7. **If at Max Iterations:**
   Show warning about safety limit reached

## Notes

- This is a read-only command - it doesn't modify any state
- Use to check progress at any point during autonomous execution
- Useful for debugging when things seem stuck
