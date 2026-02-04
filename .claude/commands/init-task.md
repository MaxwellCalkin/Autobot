# Initialize Autobot Task

Start a new autonomous development task with inline planning, requirement clarification, and execution.

## Arguments

$ARGUMENTS - The task description (required)

## Process

1. **Validate** - Ensure no active task is running
2. **Create Task** - Initialize `.autobot/task.json` with the description
3. **Explore** - Read the codebase to understand architecture and patterns
4. **Clarify** - Identify ambiguities or uncertainties and ask the user using `AskUserQuestion`
5. **Decompose** - Break into subtasks using the clarified understanding
6. **Save Plan** - Write subtasks to `.autobot/plan.json`
7. **Initialize Metrics** - Reset `.autobot/metrics.json`
8. **Begin Work** - Start on the first subtask

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

3. **Explore the codebase yourself** (do NOT delegate to a subagent):
   - Use `Glob` to discover the project structure
   - Use `Read` to understand key files, patterns, and conventions
   - Use `Grep` to find relevant code areas
   - Identify what already exists vs. what needs to be built

4. **Identify uncertainties and clarify with the user:**

   After exploring the codebase and analyzing the task description, determine if there are any:
   - **Ambiguous requirements** - The task description could be interpreted multiple ways
   - **Missing details** - Important decisions that the user hasn't specified
   - **Conflicting constraints** - Requirements that seem to conflict with each other or existing code
   - **Architectural choices** - Multiple valid approaches where user preference matters
   - **Scope boundaries** - Unclear what's in vs. out of scope

   If ANY uncertainties exist, use the `AskUserQuestion` tool to ask the user before proceeding. Structure questions to be specific and actionable - present concrete options where possible rather than open-ended questions.

   **Examples of good clarifying questions:**
   - "The task mentions 'authentication' - should this use JWT tokens or session-based auth?"
   - "I see the codebase uses both REST and GraphQL. Which should the new endpoint use?"
   - "Should error messages be user-facing (friendly) or developer-facing (detailed)?"

   **Do NOT ask about:**
   - Implementation details you can decide yourself (variable names, file organization)
   - Things that are clearly specified in the task description
   - Standard best practices (testing, error handling) unless there's a genuine trade-off

   If the task description is sufficiently clear and unambiguous, skip this step and proceed directly to decomposition.

5. **Decompose into subtasks** using the planning guidelines from `.claude/agents/planner.md`:

   Apply the decomposition guidelines:
   - Maximum 5-7 subtasks per task
   - Each subtask fits within a single context window
   - Each subtask is independently verifiable with tests
   - Order by dependencies (foundational work first)
   - Always include a test-writing phase for new features
   - Final subtask should be integration verification
   - If unsure about scope, err on smaller subtasks

   Generate the plan as a JSON structure:
   ```json
   {
     "task_id": "task-{timestamp}",
     "version": 1,
     "created_at": "ISO timestamp",
     "updated_at": "ISO timestamp",
     "subtasks": [
       {
         "id": "st-001",
         "title": "Short descriptive title",
         "description": "Detailed description of what to implement",
         "files": ["paths/to/files/to/modify"],
         "tests": ["describe what tests to write"],
         "acceptance_criteria": [
           "Specific, verifiable criterion 1",
           "Specific, verifiable criterion 2"
         ],
         "dependencies": [],
         "complexity": "small|medium|large",
         "status": "pending"
       }
     ]
   }
   ```

6. Save the plan to `.autobot/plan.json`

7. Reset metrics:
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

8. Log to progress.md:
   ```markdown
   ## Task Started: {timestamp}
   **Title:** {title}
   **Subtasks:** {count}
   **Clarifications:** {summary of any questions asked and answers received, or "None needed"}

   ---
   ```

9. Begin working on the first subtask immediately

## Notes

- Planning happens inline (NOT via subagent) so the agent can ask the user questions
- The agent should only ask questions when genuinely uncertain - not as a formality
- The autonomous loop (Stop hook) will take over after initialization
- Progress is automatically tracked in `.autobot/`
- Use `/status` to check progress at any time
- Use `/pause` to pause the autonomous loop
- Use `/abort` to cancel and preserve state
