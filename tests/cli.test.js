import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import { createTempProject, createMockAutobotDir, createMockClaudeDir, cleanupTemp } from './helpers.js';
import { preprocessArgs } from '../src/cli.js';
import { VERSION } from '../src/index.js';

const BIN = path.resolve('bin/autobot.js');

function runCLI(args, { cwd, input } = {}) {
  try {
    const result = execFileSync('node', [BIN, ...args], {
      cwd,
      input,
      encoding: 'utf-8',
      timeout: 10000,
      env: { ...process.env, FORCE_COLOR: '0' },
    });
    return { stdout: result, exitCode: 0 };
  } catch (err) {
    return {
      stdout: (err.stdout || '') + (err.stderr || ''),
      exitCode: err.status ?? 1,
    };
  }
}

describe('version', () => {
  it('--version shows version and exits', () => {
    const { stdout, exitCode } = runCLI(['--version']);
    expect(exitCode).toBe(0);
    expect(stdout).toContain(VERSION);
  });

  it('-v shows version', () => {
    const { stdout, exitCode } = runCLI(['-v']);
    expect(exitCode).toBe(0);
    expect(stdout).toContain(VERSION);
  });
});

describe('no args', () => {
  it('no arguments shows help text', () => {
    const { stdout } = runCLI([]);
    expect(stdout.toLowerCase()).toContain('autobot');
  });
});

describe('preprocessArgs', () => {
  it('inserts start for unknown first arg', () => {
    const originalArgv = [...process.argv];
    try {
      process.argv = ['node', 'autobot', 'Build a feature'];
      preprocessArgs();
      expect(process.argv).toEqual(['node', 'autobot', 'start', 'Build a feature']);

      process.argv = ['node', 'autobot', 'status'];
      preprocessArgs();
      expect(process.argv).toEqual(['node', 'autobot', 'status']);

      process.argv = ['node', 'autobot', '--version'];
      preprocessArgs();
      expect(process.argv).toEqual(['node', 'autobot', '--version']);
    } finally {
      process.argv = originalArgv;
    }
  });
});

describe('status', () => {
  let tmpDir, projectDir;

  beforeEach(() => {
    ({ tmpDir, projectDir } = createTempProject());
  });
  afterEach(() => cleanupTemp(tmpDir));

  it('shows not initialized when no .claude or .autobot', () => {
    const { stdout } = runCLI(['status'], { cwd: projectDir });
    expect(stdout.toLowerCase()).toContain('not initialized');
  });

  it('shows status when .claude exists', () => {
    createMockClaudeDir(projectDir);
    const { stdout } = runCLI(['status'], { cwd: projectDir });
    expect(stdout).toContain('.claude/');
  });

  it('shows active task details', () => {
    createMockClaudeDir(projectDir);
    const autobotDir = createMockAutobotDir(projectDir);
    const taskData = { id: 'task-1', title: 'Test Task', status: 'in_progress' };
    fs.writeFileSync(path.join(autobotDir, 'task.json'), JSON.stringify(taskData), 'utf-8');

    const { stdout } = runCLI(['status'], { cwd: projectDir });
    expect(stdout).toContain('Test Task');
    expect(stdout).toContain('in_progress');
  });
});

describe('clean', () => {
  let tmpDir, projectDir;

  beforeEach(() => {
    ({ tmpDir, projectDir } = createTempProject());
  });
  afterEach(() => cleanupTemp(tmpDir));

  it('shows message when nothing to clean', () => {
    const { stdout } = runCLI(['clean'], { cwd: projectDir });
    expect(stdout).toContain('No Autobot files found');
  });

  it('removes .autobot directory with --yes', () => {
    createMockAutobotDir(projectDir);
    const { stdout } = runCLI(['clean', '--yes'], { cwd: projectDir });
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(false);
    expect(stdout).toContain('Removed .autobot/');
  });

  it('--all removes both .claude and .autobot', () => {
    createMockClaudeDir(projectDir);
    createMockAutobotDir(projectDir);
    fs.writeFileSync(path.join(projectDir, 'CLAUDE.md'), '# Test', 'utf-8');

    runCLI(['clean', '--all', '--yes'], { cwd: projectDir });
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(false);
    expect(fs.existsSync(path.join(projectDir, '.claude'))).toBe(false);
    expect(fs.existsSync(path.join(projectDir, 'CLAUDE.md'))).toBe(false);
  });
});

describe('init', () => {
  let tmpDir, projectDir;

  beforeEach(() => {
    ({ tmpDir, projectDir } = createTempProject());
  });
  afterEach(() => cleanupTemp(tmpDir));

  it('creates directories', () => {
    const { stdout } = runCLI(['init'], { cwd: projectDir });
    expect(fs.existsSync(path.join(projectDir, '.claude'))).toBe(true);
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(true);
    expect(stdout).toContain('Autobot initialized');
  });
});

describe('start', () => {
  let tmpDir, projectDir;

  beforeEach(() => {
    ({ tmpDir, projectDir } = createTempProject());
  });
  afterEach(() => cleanupTemp(tmpDir));

  it('--dry-run shows what would be created without changes', () => {
    const { stdout } = runCLI(['start', 'Test task', '--dry-run'], { cwd: projectDir });
    expect(stdout).toContain('Dry run');
    expect(stdout).toContain('Would create');
    expect(fs.existsSync(path.join(projectDir, '.claude'))).toBe(false);
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(false);
  });

  it('--no-launch scaffolds but does not launch Claude', () => {
    const { stdout } = runCLI(['start', 'Test task', '--no-launch'], { cwd: projectDir });
    expect(fs.existsSync(path.join(projectDir, '.claude'))).toBe(true);
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(true);
    expect(stdout).toContain('--no-launch specified');
  });

  it('--force skips prompts', () => {
    createMockAutobotDir(projectDir);
    fs.writeFileSync(
      path.join(projectDir, '.autobot', 'task.json'),
      '{"id": "old-task", "status": "idle"}',
      'utf-8'
    );

    const { exitCode } = runCLI(['start', 'New task', '--no-launch', '--force'], { cwd: projectDir });
    expect(exitCode).toBe(0);

    const taskContent = fs.readFileSync(path.join(projectDir, '.autobot', 'task.json'), 'utf-8');
    expect(taskContent).not.toContain('old-task');
  });
});
