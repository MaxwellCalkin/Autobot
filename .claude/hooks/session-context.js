#!/usr/bin/env node
/**
 * Autobot Session Context Hook - Loads state at session start.
 *
 * Triggered on SessionStart to provide Claude with current task context,
 * progress status, and any important learnings from previous iterations.
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

function getProjectDir() {
  return process.env.CLAUDE_PROJECT_DIR || process.cwd();
}

function formatProgressBar(completed, total, width = 10) {
  if (total === 0) {
    return '[' + '-'.repeat(width) + ']';
  }
  const filled = Math.floor(width * completed / total);
  return '[' + '#'.repeat(filled) + '-'.repeat(width - filled) + ']';
}

function main() {
  const projectDir = getProjectDir();
  const autobotDir = path.join(projectDir, '.autobot');
  const contextParts = [];

  if (!fs.existsSync(autobotDir)) {
    console.log(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: 'Autobot: No active task. Use /init-task to start.',
      },
    }));
    process.exit(0);
  }

  // Load current task
  const task = loadJson(path.join(autobotDir, 'task.json'));
  if (task && task.id && task.status !== 'idle') {
    contextParts.push(`ACTIVE TASK: ${task.title || 'Unknown'}`);
    contextParts.push(`STATUS: ${task.status || 'unknown'}`);
  } else {
    console.log(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: 'Autobot: No active task. Use /init-task to start.',
      },
    }));
    process.exit(0);
  }

  // Load plan status
  const plan = loadJson(path.join(autobotDir, 'plan.json'));
  if (plan && plan.subtasks && plan.subtasks.length > 0) {
    const subtasks = plan.subtasks;
    const completed = subtasks.filter(t => t.status === 'completed').length;
    const inProgress = subtasks.filter(t => t.status === 'in_progress');
    const pending = subtasks.filter(t => t.status === 'pending');
    const total = subtasks.length;

    const progressBar = formatProgressBar(completed, total);
    contextParts.push(`PROGRESS: ${progressBar} ${completed}/${total} subtasks`);

    if (inProgress.length > 0) {
      contextParts.push(`CURRENT: ${inProgress[0].title}`);
    } else if (pending.length > 0) {
      contextParts.push(`NEXT: ${pending[0].title}`);
    }
  }

  // Load metrics
  const metrics = loadJson(path.join(autobotDir, 'metrics.json'));
  if (metrics) {
    const iteration = metrics.current_iteration || 0;
    const maxIter = metrics.max_iterations || 50;
    contextParts.push(`ITERATION: ${iteration}/${maxIter}`);

    const failures = metrics.consecutive_test_failures || 0;
    if (failures > 0) {
      contextParts.push(`WARNING: ${failures} consecutive test failures`);
    }
  }

  // Check for pause flag
  if (fs.existsSync(path.join(autobotDir, '.paused'))) {
    contextParts.push('STATUS: PAUSED (use /resume to continue)');
  }

  // Load recent learnings from progress.md
  const progressPath = path.join(autobotDir, 'progress.md');
  if (fs.existsSync(progressPath)) {
    const progress = fs.readFileSync(progressPath, 'utf-8');
    if (progress.includes('---')) {
      let recent = progress.split('---').pop().trim();
      if (recent && recent.length > 10) {
        if (recent.length > 300) {
          recent = '...' + recent.slice(-300);
        }
        contextParts.push(`\nRECENT LEARNINGS:\n${recent}`);
      }
    }
  }

  if (contextParts.length > 0) {
    console.log(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'SessionStart',
        additionalContext: contextParts.join('\n'),
      },
    }));
  }
}

main();
