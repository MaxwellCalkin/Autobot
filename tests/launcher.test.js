import { describe, it, expect, vi, beforeEach } from 'vitest';
import { spawnSync } from 'child_process';
import { launchClaudeCode } from '../src/launcher.js';

vi.mock('child_process', () => ({
  spawnSync: vi.fn(),
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.spyOn(console, 'log').mockImplementation(() => {});
});

describe('launchClaudeCode', () => {
  it('calls claude with init-task command', () => {
    spawnSync.mockReturnValue({ status: 0, error: null });

    const result = launchClaudeCode('/tmp/project', 'Build something');

    expect(result).toBe(0);
    expect(spawnSync).toHaveBeenCalledOnce();
    const [cmd, args] = spawnSync.mock.calls[0];
    expect(cmd).toBe('claude');
    expect(args[0]).toBe('--dangerously-skip-permissions');
    expect(args[1]).toContain('/init-task');
    expect(args[1]).toContain('Build something');
  });

  it('returns claude exit code', () => {
    spawnSync.mockReturnValue({ status: 42, error: null });
    const result = launchClaudeCode('/tmp/project', 'task');
    expect(result).toBe(42);
  });

  it('returns zero on success', () => {
    spawnSync.mockReturnValue({ status: 0, error: null });
    const result = launchClaudeCode('/tmp/project', 'task');
    expect(result).toBe(0);
  });

  it('uses correct working directory', () => {
    spawnSync.mockReturnValue({ status: 0, error: null });
    launchClaudeCode('/tmp/my-project', 'task');
    const options = spawnSync.mock.calls[0][2];
    expect(options.cwd).toBe('/tmp/my-project');
  });

  it('uses stdio inherit for terminal passthrough', () => {
    spawnSync.mockReturnValue({ status: 0, error: null });
    launchClaudeCode('/tmp/project', 'task');
    const options = spawnSync.mock.calls[0][2];
    expect(options.stdio).toBe('inherit');
  });

  it('returns 1 when claude is not found', () => {
    const err = new Error('ENOENT');
    err.code = 'ENOENT';
    spawnSync.mockReturnValue({ status: null, error: err });

    // Mock platform to non-windows so it doesn't retry
    const originalPlatform = Object.getOwnPropertyDescriptor(process, 'platform');
    Object.defineProperty(process, 'platform', { value: 'linux' });

    const result = launchClaudeCode('/tmp/project', 'task');
    expect(result).toBe(1);

    Object.defineProperty(process, 'platform', originalPlatform);
  });

  it('prompt includes the full task description', () => {
    spawnSync.mockReturnValue({ status: 0, error: null });
    const task = 'Build a login system with OAuth support';
    launchClaudeCode('/tmp/project', task);
    const args = spawnSync.mock.calls[0][1];
    expect(args[1]).toContain(task);
  });
});
