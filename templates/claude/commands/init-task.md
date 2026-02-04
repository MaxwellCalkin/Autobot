# Initialize Autobot Task

Start a new autonomous development task with automatic decomposition and execution.

## Arguments

$ARGUMENTS - The task description (required)

## Process

1. **Validate** - Ensure no active task is running
2. **Create Task** - Initialize `.autobot/task.json` with the description
3. **Decompose** - Use the planner subagent to break into subtasks
4. **Save Plan** - Write subtasks to `.autobot/plan.json`
5. **Initialize Metrics** - Reset `.autobot/metrics.json`
6. **Begin Work** - Start on the first subtask

## Example Usage

```
/init-task Add user authentication with OAuth support for Google and GitHub
```

## Instructions

When this command is invoked:

1. Check if there's already an active task:
   ```javascript
   task = load_json('.autobot/task.json')
   if task.get('status') == 'in_progress':
       # Warn user and ask to /abort first
   ```

2. Create the task definition:
   ```json
   {
     "id": "task-{timestamp}",
     "title": "Short title from description",
     "description": "$ARGUMENTS",
     "created_at": "ISO timestamp",
     "status": "in_progress"
   }
   ```

3. Use the planner subagent to decompose:
   ```
   /task planner "Decompose this task into subtasks: $ARGUMENTS"
   ```

4. Save the plan returned by planner to `.autobot/plan.json`

5. Reset metrics:
   ```json
   {
     "current_iteration": 0,
     "max_iterations": 50,
     "consecutive_test_failures": 0,
     "total_test_runs": 0,
     "total_test_passes": 0,
     "total_test_failures": 0,
     "started_at": "ISO timestamp"
   }
   ```

6. Log to progress.md:
   ```markdown
   ## Task Started: {timestamp}
   **Title:** {title}
   **Subtasks:** {count}

   ---
   ```

7. Begin working on the first subtask immediately

## Notes

- The autonomous loop (Stop hook) will take over after initialization
- Progress is automatically tracked in `.autobot/`
- Use `/status` to check progress at any time
- Use `/pause` to pause the autonomous loop
- Use `/abort` to cancel and preserve state
