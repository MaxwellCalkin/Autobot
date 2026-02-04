#!/usr/bin/env node
/**
 * Autobot Post-Edit Test Hook - Automatically runs tests after file edits.
 *
 * Triggered after Write/Edit tool use. Detects project type and runs appropriate
 * test command. Updates metrics and logs observations for failures.
 *
 * Hook Output Protocol:
 *   - Print JSON with "decision": "block" to prevent continuation until fixed
 *   - Print JSON with "hookSpecificOutput" for informational feedback
 */
import fs from 'fs';
import path from 'path';
import { spawnSync } from 'child_process';

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

function appendJsonl(filePath, entry) {
  fs.appendFileSync(filePath, JSON.stringify(entry) + '\n', 'utf-8');
}

function getProjectDir() {
  return process.env.CLAUDE_PROJECT_DIR || process.cwd();
}

function detectTestCommand(projectDir) {
  // Node.js
  const pkgPath = path.join(projectDir, 'package.json');
  if (fs.existsSync(pkgPath)) {
    const pkg = loadJson(pkgPath) || {};
    const scripts = pkg.scripts || {};
    if (scripts.test) {
      return ['npm', 'test', '--', '--passWithNoTests'];
    }
  }

  // Python
  if (fs.existsSync(path.join(projectDir, 'pyproject.toml')) ||
      fs.existsSync(path.join(projectDir, 'setup.py'))) {
    return ['pytest', '-x', '--tb=short', '-q'];
  }

  // Rust
  if (fs.existsSync(path.join(projectDir, 'Cargo.toml'))) {
    return ['cargo', 'test', '--', '--test-threads=1'];
  }

  // Go
  if (fs.existsSync(path.join(projectDir, 'go.mod'))) {
    return ['go', 'test', './...', '-v'];
  }

  return null;
}

const SOURCE_EXTENSIONS = new Set([
  '.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs',
  '.py', '.pyw',
  '.rs',
  '.go',
  '.java', '.kt', '.kts',
  '.c', '.cpp', '.cc', '.h', '.hpp',
  '.cs',
  '.rb',
  '.php',
  '.swift',
]);

function isSourceFile(filePath) {
  return SOURCE_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function main() {
  let inputData = {};
  try {
    inputData = JSON.parse(fs.readFileSync(0, 'utf-8'));
  } catch {
    // No input or invalid JSON
  }

  const toolInput = inputData.tool_input || {};
  const filePath = toolInput.file_path || '';

  if (!filePath || !isSourceFile(filePath)) {
    process.exit(0);
  }

  const projectDir = getProjectDir();
  const autobotDir = path.join(projectDir, '.autobot');

  if (!fs.existsSync(autobotDir)) {
    process.exit(0);
  }

  const testCmd = detectTestCommand(projectDir);

  if (!testCmd) {
    console.log(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: `Edited ${path.basename(filePath)}. No test framework detected.`,
      },
    }));
    process.exit(0);
  }

  // Load metrics
  const metricsPath = path.join(autobotDir, 'metrics.json');
  const metrics = loadJson(metricsPath) || {
    current_iteration: 0,
    max_iterations: 50,
    consecutive_test_failures: 0,
    total_test_runs: 0,
    total_test_passes: 0,
    total_test_failures: 0,
  };

  // Run tests
  let testPassed = false;
  let testOutput = '';

  try {
    const result = spawnSync(testCmd[0], testCmd.slice(1), {
      cwd: projectDir,
      timeout: 120000,
      shell: process.platform === 'win32',
      encoding: 'utf-8',
    });

    if (result.error) {
      if (result.error.code === 'ENOENT') {
        console.log(JSON.stringify({
          hookSpecificOutput: {
            hookEventName: 'PostToolUse',
            additionalContext: `Edited ${path.basename(filePath)}. Test command not available: ${testCmd[0]}`,
          },
        }));
        process.exit(0);
      }
      if (result.error.code === 'ETIMEDOUT') {
        testPassed = false;
        testOutput = 'Test execution timed out after 120 seconds';
      } else {
        throw result.error;
      }
    } else {
      testPassed = result.status === 0;
      testOutput = (result.stdout || '') + (result.stderr || '');
    }
  } catch (err) {
    testPassed = false;
    testOutput = err.message || 'Unknown error running tests';
  }

  // Update metrics
  metrics.total_test_runs = (metrics.total_test_runs || 0) + 1;
  metrics.last_activity = new Date().toISOString();

  if (testPassed) {
    metrics.consecutive_test_failures = 0;
    metrics.total_test_passes = (metrics.total_test_passes || 0) + 1;
    saveJson(metricsPath, metrics);

    console.log(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: `Tests passed after editing ${path.basename(filePath)}. Continue with confidence.`,
      },
    }));
  } else {
    metrics.consecutive_test_failures = (metrics.consecutive_test_failures || 0) + 1;
    metrics.total_test_failures = (metrics.total_test_failures || 0) + 1;
    saveJson(metricsPath, metrics);

    // Log observation
    const observation = {
      timestamp: new Date().toISOString(),
      type: 'test_failure',
      file: filePath,
      iteration: metrics.current_iteration || 0,
      consecutive_failures: metrics.consecutive_test_failures,
      output_snippet: testOutput ? testOutput.slice(0, 500) : 'No output',
    };
    appendJsonl(path.join(autobotDir, 'observations.jsonl'), observation);

    const displayOutput = testOutput.length > 1000 ? testOutput.slice(0, 1000) : testOutput;

    console.log(JSON.stringify({
      decision: 'block',
      reason: `Tests failed after editing ${path.basename(filePath)}.\n\nFAILURE OUTPUT:\n${displayOutput}\n\nCONSECUTIVE FAILURES: ${metrics.consecutive_test_failures}/3 (pauses at 3)\n\nPlease analyze the failure and fix the issue before continuing.\nThe test output has been logged to .autobot/observations.jsonl for reference.`,
    }));
  }
}

main();
