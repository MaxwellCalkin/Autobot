import fs from 'fs';
import path from 'path';
import os from 'os';

export function createTempProject() {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'autobot-test-'));
  const projectDir = path.join(tmpDir, 'test_project');
  fs.mkdirSync(projectDir);
  return { tmpDir, projectDir };
}

export function createMockClaudeDir(projectDir) {
  const claudeDir = path.join(projectDir, '.claude');
  fs.mkdirSync(claudeDir);
  return claudeDir;
}

export function createMockAutobotDir(projectDir) {
  const autobotDir = path.join(projectDir, '.autobot');
  fs.mkdirSync(autobotDir);

  fs.writeFileSync(
    path.join(autobotDir, 'task.json'),
    JSON.stringify({ id: null, status: 'idle' }),
    'utf-8'
  );
  fs.writeFileSync(
    path.join(autobotDir, 'plan.json'),
    JSON.stringify({ subtasks: [] }),
    'utf-8'
  );
  fs.writeFileSync(
    path.join(autobotDir, 'metrics.json'),
    JSON.stringify({ current_iteration: 0, max_iterations: 50 }),
    'utf-8'
  );

  return autobotDir;
}

export function cleanupTemp(tmpDir) {
  fs.rmSync(tmpDir, { recursive: true, force: true });
}
