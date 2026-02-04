# Resume Autobot

Resume a paused autonomous development loop.

## Usage

```
/resume
```

## Instructions

When this command is invoked:

1. **Check for Paused State:**
   ```javascript
   if not Path('.autobot/.paused').exists():
       print("No paused task found. Use /init-task to start a new task.")
       return
   ```

2. **Remove Pause Flag:**
   ```bash
   rm .autobot/.paused
   ```

3. **Update Task Status:**
   ```json
   // In .autobot/task.json
   {
     "status": "in_progress",
     "resumed_at": "ISO timestamp"
   }
   ```

4. **Log to Progress:**
   ```markdown
   ## Resumed: {timestamp}

   ---
   ```

5. **Load Current State:**
   - Read plan.json to find current subtask
   - Read metrics.json for iteration count
   - Read progress.md for recent learnings

6. **Continue Working:**
   Display the current subtask and begin working on it immediately.

## Behavior

- Picks up exactly where it left off
- Iteration counter continues (not reset)
- All previous learnings are preserved
- Stop hook will take over autonomous continuation

## Notes

- Safe to use multiple times
- If task was completed while paused, will detect and report
- If max iterations was reached, will warn and ask for confirmation
