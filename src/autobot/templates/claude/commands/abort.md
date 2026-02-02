# Abort Autobot

Emergency stop - cancel the current task while preserving all state.

## Usage

```
/abort
```

## Instructions

When this command is invoked:

1. **Create Abort Flag:**
   ```bash
   touch .autobot/.aborted
   ```

2. **Update Task Status:**
   ```json
   // In .autobot/task.json
   {
     "status": "aborted",
     "aborted_at": "ISO timestamp"
   }
   ```

3. **Log to Progress:**
   ```markdown
   ## Aborted: {timestamp}
   Reason: User requested abort
   Iteration: {current_iteration}
   Completed subtasks: {completed_count}/{total_count}

   ---
   ```

4. **Archive State (Optional):**
   Copy current state to `.autobot/archive/{timestamp}-{task_slug}/`:
   - task.json
   - plan.json
   - metrics.json
   - progress.md
   - observations.jsonl

5. **Reset for Next Task:**
   ```json
   // Reset .autobot/task.json
   {
     "id": null,
     "title": null,
     "description": null,
     "status": "idle"
   }
   ```

6. **Confirm to User:**
   ```
   Task aborted successfully.

   Final progress:
   - Completed: {x}/{y} subtasks
   - Total iterations: {n}

   State archived to: .autobot/archive/{timestamp}-{task_slug}/

   You can:
   - Review the archived state
   - Start a new task with /init-task
   - Recover and continue manually if needed
   ```

## When to Use

- When the task is fundamentally wrong
- When you need to change approach completely
- When stuck in an unrecoverable state
- When the task definition needs to change

## Notes

- More destructive than /pause
- State is archived, not deleted
- Use /pause if you just need a break
- All code changes remain in the working directory
