import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import fs from 'fs';
import path from 'path';
import { createTempProject, createMockAutobotDir, cleanupTemp } from './helpers.js';
import { checkExistingState, scaffoldProject } from '../src/scaffolder.js';

let tmpDir, projectDir;

beforeEach(() => {
  ({ tmpDir, projectDir } = createTempProject());
});

afterEach(() => {
  cleanupTemp(tmpDir);
});

describe('checkExistingState', () => {
  it('returns false/false/null when nothing exists', () => {
    const { claudeExists, autobotExists, activeTask } = checkExistingState(projectDir);
    expect(claudeExists).toBe(false);
    expect(autobotExists).toBe(false);
    expect(activeTask).toBeNull();
  });

  it('detects .claude directory without .autobot', () => {
    fs.mkdirSync(path.join(projectDir, '.claude'));
    const { claudeExists, autobotExists } = checkExistingState(projectDir);
    expect(claudeExists).toBe(true);
    expect(autobotExists).toBe(false);
  });

  it('detects .autobot directory without .claude', () => {
    fs.mkdirSync(path.join(projectDir, '.autobot'));
    const { claudeExists, autobotExists } = checkExistingState(projectDir);
    expect(claudeExists).toBe(false);
    expect(autobotExists).toBe(true);
  });

  it('detects both directories', () => {
    fs.mkdirSync(path.join(projectDir, '.claude'));
    fs.mkdirSync(path.join(projectDir, '.autobot'));
    const { claudeExists, autobotExists } = checkExistingState(projectDir);
    expect(claudeExists).toBe(true);
    expect(autobotExists).toBe(true);
  });

  it('returns null for idle task', () => {
    const autobotDir = createMockAutobotDir(projectDir);
    fs.writeFileSync(
      path.join(autobotDir, 'task.json'),
      JSON.stringify({ id: 'task-1', status: 'idle' }),
      'utf-8'
    );
    const { activeTask } = checkExistingState(projectDir);
    expect(activeTask).toBeNull();
  });

  it('returns task dict for in_progress task', () => {
    const autobotDir = createMockAutobotDir(projectDir);
    const taskData = { id: 'task-1', title: 'Test Task', status: 'in_progress' };
    fs.writeFileSync(
      path.join(autobotDir, 'task.json'),
      JSON.stringify(taskData),
      'utf-8'
    );
    const { activeTask } = checkExistingState(projectDir);
    expect(activeTask).not.toBeNull();
    expect(activeTask.status).toBe('in_progress');
    expect(activeTask.title).toBe('Test Task');
  });

  it('returns task dict for paused task', () => {
    const autobotDir = createMockAutobotDir(projectDir);
    const taskData = { id: 'task-2', title: 'Paused Task', status: 'paused' };
    fs.writeFileSync(
      path.join(autobotDir, 'task.json'),
      JSON.stringify(taskData),
      'utf-8'
    );
    const { activeTask } = checkExistingState(projectDir);
    expect(activeTask).not.toBeNull();
    expect(activeTask.status).toBe('paused');
  });

  it('returns null for completed task', () => {
    const autobotDir = createMockAutobotDir(projectDir);
    fs.writeFileSync(
      path.join(autobotDir, 'task.json'),
      JSON.stringify({ id: 'task-1', status: 'completed' }),
      'utf-8'
    );
    const { activeTask } = checkExistingState(projectDir);
    expect(activeTask).toBeNull();
  });

  it('handles invalid JSON gracefully', () => {
    const autobotDir = createMockAutobotDir(projectDir);
    fs.writeFileSync(path.join(autobotDir, 'task.json'), 'not valid json', 'utf-8');
    const { activeTask } = checkExistingState(projectDir);
    expect(activeTask).toBeNull();
  });
});

describe('scaffoldProject', () => {
  it('creates .claude directory', () => {
    scaffoldProject(projectDir);
    expect(fs.existsSync(path.join(projectDir, '.claude'))).toBe(true);
  });

  it('creates .autobot directory', () => {
    scaffoldProject(projectDir);
    expect(fs.existsSync(path.join(projectDir, '.autobot'))).toBe(true);
  });

  it('creates CLAUDE.md in project root', () => {
    scaffoldProject(projectDir);
    expect(fs.existsSync(path.join(projectDir, 'CLAUDE.md'))).toBe(true);
  });

  it('creates settings.json', () => {
    scaffoldProject(projectDir);
    const settingsFile = path.join(projectDir, '.claude', 'settings.json');
    expect(fs.existsSync(settingsFile)).toBe(true);
    const settings = JSON.parse(fs.readFileSync(settingsFile, 'utf-8'));
    expect(settings).toHaveProperty('hooks');
  });

  it('creates hooks directory with JS files', () => {
    scaffoldProject(projectDir);
    const hooksDir = path.join(projectDir, '.claude', 'hooks');
    expect(fs.existsSync(hooksDir)).toBe(true);
    const jsFiles = fs.readdirSync(hooksDir).filter(f => f.endsWith('.js'));
    expect(jsFiles.length).toBeGreaterThan(0);
  });

  it('returns created files list', () => {
    const created = scaffoldProject(projectDir);
    expect(Array.isArray(created)).toBe(true);
    expect(created.length).toBeGreaterThan(0);
    expect(created.some(f => f.includes('settings.json'))).toBe(true);
  });

  it('does not overwrite without force', () => {
    const claudeDir = path.join(projectDir, '.claude');
    fs.mkdirSync(claudeDir);
    const settingsFile = path.join(claudeDir, 'settings.json');
    fs.writeFileSync(settingsFile, '{"custom": "data"}', 'utf-8');

    scaffoldProject(projectDir, { force: false });

    const settings = JSON.parse(fs.readFileSync(settingsFile, 'utf-8'));
    expect(settings.custom).toBe('data');
  });

  it('overwrites with force', () => {
    const claudeDir = path.join(projectDir, '.claude');
    fs.mkdirSync(claudeDir);
    const settingsFile = path.join(claudeDir, 'settings.json');
    fs.writeFileSync(settingsFile, '{"custom": "data"}', 'utf-8');

    scaffoldProject(projectDir, { force: true });

    const settings = JSON.parse(fs.readFileSync(settingsFile, 'utf-8'));
    expect(settings).not.toHaveProperty('custom');
  });

  it('settings.json uses node for hooks, not python', () => {
    scaffoldProject(projectDir);
    const settingsFile = path.join(projectDir, '.claude', 'settings.json');
    const content = fs.readFileSync(settingsFile, 'utf-8');
    expect(content).toContain('node .claude/hooks/');
    expect(content).not.toContain('python');
    expect(content).not.toContain('uv run');
  });
});
