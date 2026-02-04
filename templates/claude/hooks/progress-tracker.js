#!/usr/bin/env node
/**
 * Autobot Progress Tracker Hook - Updates metrics after Bash commands.
 *
 * Triggered after Bash tool use to track activity and detect patterns.
 * Silent operation (no output unless significant).
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
  let inputData = {};
  try {
    inputData = JSON.parse(fs.readFileSync(0, 'utf-8'));
  } catch {
    // No input or invalid JSON
  }

  const projectDir = getProjectDir();
  const autobotDir = path.join(projectDir, '.autobot');

  if (!fs.existsSync(autobotDir)) {
    process.exit(0);
  }

  const metricsPath = path.join(autobotDir, 'metrics.json');
  const metrics = loadJson(metricsPath);

  if (!metrics) {
    process.exit(0);
  }

  metrics.last_activity = new Date().toISOString();

  // Track git commits if detected
  const toolInput = inputData.tool_input || {};
  const command = toolInput.command || '';
  const exitCode = (inputData.tool_result || {}).exit_code;

  if (command.includes('git commit') && exitCode === 0) {
    metrics.commits = (metrics.commits || 0) + 1;
  }

  saveJson(metricsPath, metrics);
}

main();
