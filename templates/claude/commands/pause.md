# Pause Autobot

Pause the autonomous development loop without losing progress.

## Usage

```
/pause
```

## Instructions

When this command is invoked:

1. **Create Pause Flag:**
   ```bash
   touch .autobot/.paused
   ```

2. **Update Task Status:**
   ```json
   // In .autobot/task.json
   {
     "status": "paused",
     "paused_at": "ISO timestamp"
   }
   ```

3. **Log to Progress:**
   ```markdown
   ## Paused: {timestamp}
   Iteration: {current_iteration}
   Last subtask: {current_subtask_title}

   ---
   ```

4. **Confirm to User:**
   ```
   Task paused successfully.

   Current progress:
   - Completed: {x}/{y} subtasks
   - Iteration: {n}/{max}

   Use /resume to continue when ready.
   Use /status to check current state.
   ```

## Behavior

- The Stop hook checks for `.autobot/.paused` and respects it
- All progress is preserved
- Metrics are not reset
- Can resume at any time with /resume

## Notes

- Use this when you need to step away
- Use this when you want to review progress before continuing
- Safer than /abort - preserves all state
