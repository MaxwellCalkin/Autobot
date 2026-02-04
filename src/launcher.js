import { spawnSync } from 'child_process';
import chalk from 'chalk';

const IS_WINDOWS = process.platform === 'win32';

export function launchClaudeCode(projectDir, task) {
  const prompt = `/init-task ${task}`;

  console.log(chalk.dim(`Working dir: ${projectDir}`));
  console.log();

  try {
    if (IS_WINDOWS) {
      // On Windows, claude is a .cmd wrapper requiring shell execution.
      // Wrap the prompt in quotes so shell argument joining keeps it as one token.
      const escaped = prompt.replace(/"/g, '""');
      const result = spawnSync('claude', ['--dangerously-skip-permissions', `"${escaped}"`], {
        cwd: projectDir,
        stdio: 'inherit',
        shell: true,
      });

      if (result.error) {
        if (result.error.code === 'ENOENT') {
          printNotFoundError();
          return 1;
        }
        throw result.error;
      }
      return result.status ?? 0;
    }

    const result = spawnSync('claude', ['--dangerously-skip-permissions', prompt], {
      cwd: projectDir,
      stdio: 'inherit',
      shell: false,
    });

    if (result.error) {
      if (result.error.code === 'ENOENT') {
        printNotFoundError();
        return 1;
      }
      throw result.error;
    }

    return result.status ?? 0;
  } catch (err) {
    if (err.code === 'ENOENT') {
      printNotFoundError();
      return 1;
    }
    console.log();
    console.log(chalk.red('Error:'), err.message);
    return 1;
  }
}

function printNotFoundError() {
  console.log();
  console.log(chalk.red('Error:'), "'claude' command not found.");
  console.log();
  console.log('Claude Code must be installed to use Autobot.');
  console.log(`Install with: ${chalk.bold('npm install -g @anthropic-ai/claude-code')}`);
  console.log();
  console.log('Or visit: https://claude.ai/code');
}
