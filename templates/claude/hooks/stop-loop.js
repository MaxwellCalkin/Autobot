#!/usr/bin/env node
/**
 * Autobot Stop Hook - Controls the autonomous loop continuation.
 *
 * This is the heart of Autobot. It intercepts Claude's exit attempts and
 * determines whether to continue working based on task status and quality gates.
 *
 * Hook Output Protocol:
 *   - Print JSON with "decision": "block" to prevent stop and re-inject prompt
 *   - Print JSON without "decision" or exit code 0 to allow stop
 */
import fs from 'fs';
import path from 'path';

function loadJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

function saveJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8');
}

function getProjectDir() {
  return process.env.CLAUDE_PROJECT_DIR || process.cwd();
}

function main() {
  // Drain stdin
  try {
    fs.readFileSync(0, 'utf-8');
  } catch {
    // No input
  }

  const projectDir = getProjectDir();
  const autobotDir = path.join(projectDir, '.autobot');

  if (!fs.existsSync(autobotDir)) {
    process.exit(0);
  }

  // Load state files
  const task = loadJson(path.join(autobotDir, 'task.json'));
  const plan = loadJson(path.join(autobotDir, 'plan.json'));
  const metrics = loadJson(path.join(autobotDir, 'metrics.json')) || {
    current_iteration: 0,
    max_iterations: 50,
    consecutive_test_failures: 0,
  };

  // Check if there's an active task
  if (!task || task.status === 'idle' || !task.id) {
    process.exit(0);
  }

  // Check for pause flag
  if (fs.existsSync(path.join(autobotDir, '.paused'))) {
    console.log(JSON.stringify({
      continue: false,
      stopReason: 'Task paused. Use /resume to continue.',
    }));
    process.exit(0);
  }

  // Check max iterations
  const currentIteration = metrics.current_iteration || 0;
  const maxIterations = metrics.max_iterations || 50;

  if (currentIteration >= maxIterations) {
    console.log(JSON.stringify({
      continue: false,
      stopReason: `Safety limit reached: ${maxIterations} iterations. Review progress and use /resume to continue.`,
    }));
    process.exit(0);
  }

  // Check for blocking failures
  const consecutiveFailures = metrics.consecutive_test_failures || 0;

  if (consecutiveFailures >= 3) {
    console.log(JSON.stringify({
      decision: 'block',
      reason: `PAUSE: ${consecutiveFailures} consecutive test failures detected.\n\nPlease review:\n1. .autobot/observations.jsonl for failure patterns\n2. .autobot/progress.md for any related learnings\n3. The test output to understand the root cause\n\nOptions:\n- Fix the issue and tests will auto-run\n- Use /abort to stop and preserve state\n- Use /pause to pause and resume later\n\nWhat would you like to do?`,
    }));
    process.exit(0);
  }

  // Check subtask completion
  const subtasks = (plan && plan.subtasks) ? plan.subtasks : [];
  const incomplete = subtasks.filter(t => t.status !== 'completed');
  const completed = subtasks.filter(t => t.status === 'completed');

  // Check for EXIT_SIGNAL in progress
  const progressPath = path.join(autobotDir, 'progress.md');
  let progressContent = '';
  if (fs.existsSync(progressPath)) {
    progressContent = fs.readFileSync(progressPath, 'utf-8');
  }

  if (progressContent.includes('EXIT_SIGNAL: COMPLETE') && incomplete.length === 0) {
    task.status = 'completed';
    saveJson(path.join(autobotDir, 'task.json'), task);

    console.log(JSON.stringify({
      continue: false,
      stopReason: `Task completed successfully! ${completed.length} subtasks finished.`,
    }));
    process.exit(0);
  }

  // If there are incomplete subtasks, continue
  if (incomplete.length > 0) {
    const nextTask = incomplete[0];

    // Increment iteration counter
    metrics.current_iteration = currentIteration + 1;
    metrics.last_activity = new Date().toISOString();
    saveJson(path.join(autobotDir, 'metrics.json'), metrics);

    const criteria = (nextTask.acceptance_criteria || ['Complete the subtask'])
      .map(c => `- ${c}`)
      .join('\n');

    const prompt = `Continue working on the current task.\n\nPROGRESS: ${completed.length}/${subtasks.length} subtasks completed\nITERATION: ${currentIteration + 1}/${maxIterations}\n\nCURRENT SUBTASK: ${nextTask.title}\nDESCRIPTION: ${nextTask.description || 'No description'}\nACCEPTANCE CRITERIA:\n${criteria}\n\nINSTRUCTIONS:\n1. Review .autobot/progress.md for any learned patterns\n2. Write tests FIRST if this involves new functionality\n3. Implement the change\n4. Tests will auto-run after edits\n5. If tests pass, update .autobot/plan.json to mark subtask complete\n6. If all subtasks done, write "EXIT_SIGNAL: COMPLETE" to .autobot/progress.md\n\nQuality over speed. Small, verifiable steps.`;

    console.log(JSON.stringify({
      decision: 'block',
      reason: prompt,
    }));
    process.exit(0);
  }

  // No more subtasks but no EXIT_SIGNAL
  console.log(JSON.stringify({
    decision: 'block',
    reason: 'All subtasks appear complete but EXIT_SIGNAL not found.\n\nPlease:\n1. Verify all acceptance criteria are met\n2. Run the full test suite one more time\n3. If everything passes, append "EXIT_SIGNAL: COMPLETE" to .autobot/progress.md\n\nThis ensures proper task completion tracking.',
  }));
}

main();
