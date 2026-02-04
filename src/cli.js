import fs from 'fs';
import path from 'path';
import { Command } from 'commander';
import chalk from 'chalk';
import { VERSION } from './index.js';
import { printPanel, CHECK, CROSS, confirm } from './ui.js';
import { checkExistingState, scaffoldProject } from './scaffolder.js';
import { launchClaudeCode } from './launcher.js';

const program = new Command();

program
  .name('autobot')
  .description('Autonomous development assistant for Claude Code')
  .version(`${chalk.bold.blue('autobot')} version ${VERSION}`, '-v, --version');

async function startAction(task, options) {
  const projectDir = process.cwd();

  printPanel([
    `${chalk.bold.blue('Autobot')} v${VERSION}`,
    `${chalk.dim('Task:')} ${task.length > 70 ? task.slice(0, 70) + '...' : task}`,
  ]);

  // Check for existing state
  const { claudeExists, autobotExists, activeTask } = checkExistingState(projectDir);

  // Handle existing active task
  if (activeTask && !options.force) {
    console.log(`${chalk.red('Active task found:')} ${activeTask.title || 'Unknown'}`);
    console.log(`Status: ${activeTask.status}`);
    console.log();
    console.log('Options:');
    console.log(`  - Use ${chalk.bold('/resume')} in Claude Code to continue this task`);
    console.log(`  - Use ${chalk.bold('/abort')} in Claude Code to cancel it`);
    console.log(`  - Run ${chalk.bold('autobot clean')} to remove state`);
    console.log(`  - Run with ${chalk.bold('--force')} to overwrite`);
    process.exit(1);
  }

  let resetAutobot = false;

  // If .autobot/ exists (but no active task), prompt to reset state
  if (autobotExists && !options.force && !options.dryRun) {
    console.log(chalk.yellow('Existing .autobot/ state found.'));
    if (!await confirm('Reset state for new task?')) {
      process.exit(1);
    }
    resetAutobot = true;
  }

  // If only .claude/ exists, ask about merging
  if (claudeExists && !autobotExists && !options.force && !options.dryRun) {
    console.log(chalk.yellow('Existing .claude/ configuration found.'));
    if (!await confirm('Merge Autobot into existing project?')) {
      process.exit(1);
    }
  }

  // Dry run
  if (options.dryRun) {
    console.log(chalk.yellow('Dry run - no files will be created'));
    console.log();
    console.log('Would create:');
    console.log('  .claude/settings.json');
    console.log('  .claude/hooks/ (5 hook scripts)');
    console.log('  .claude/agents/ (4 subagent definitions)');
    console.log('  .claude/commands/ (5 slash commands)');
    console.log('  .claude/skills/ (3 skill definitions)');
    console.log('  .autobot/ (runtime state)');
    console.log('  CLAUDE.md');
    process.exit(0);
  }

  // Scaffold the project
  console.log(chalk.bold('Scaffolding project...'));
  try {
    const createdFiles = scaffoldProject(projectDir, { force: options.force, resetAutobot });
    console.log(`${CHECK} Created ${createdFiles.length} files`);
  } catch (err) {
    console.log(`${chalk.red('Error scaffolding project:')} ${err.message}`);
    process.exit(1);
  }

  console.log();

  if (options.launch === false) {
    console.log(chalk.yellow('--no-launch specified.'));
    console.log(`Run ${chalk.bold('claude')} to start working.`);
    process.exit(0);
  }

  // Launch Claude Code
  console.log(chalk.bold('Launching Claude Code...'));
  console.log();

  const exitCode = launchClaudeCode(projectDir, task);
  process.exit(exitCode);
}

const startCmd = program
  .command('start')
  .description('Start an autonomous development task with Claude Code')
  .argument('<task>', 'The task description for Claude to work on autonomously')
  .option('-f, --force', 'Overwrite existing .claude and .autobot directories')
  .option('--no-launch', 'Scaffold only, don\'t launch Claude Code')
  .option('--dry-run', 'Show what would be created without making changes')
  .action(startAction);

// Hidden "run" alias
program
  .command('run', { hidden: true })
  .argument('<task>')
  .option('-f, --force')
  .option('--no-launch')
  .option('--dry-run')
  .action(startAction);

program
  .command('init')
  .description('Initialize Autobot in the current directory without starting a task')
  .option('-f, --force', 'Overwrite existing configuration')
  .action(async (options) => {
    const projectDir = process.cwd();

    printPanel([
      `${chalk.bold.blue('Autobot Init')}`,
      `${chalk.dim('Directory:')} ${projectDir}`,
    ]);

    const { claudeExists, autobotExists } = checkExistingState(projectDir);

    if ((claudeExists || autobotExists) && !options.force) {
      console.log(chalk.yellow('Existing configuration found.'));
      if (!await confirm('Overwrite?')) {
        process.exit(1);
      }
    }

    console.log(chalk.bold('Scaffolding...'));
    try {
      const createdFiles = scaffoldProject(projectDir, { force: options.force });
      console.log(`${CHECK} Created ${createdFiles.length} files`);
    } catch (err) {
      console.log(`${chalk.red('Error:')} ${err.message}`);
      process.exit(1);
    }

    console.log();
    console.log(chalk.green('Autobot initialized!'));
    console.log();
    console.log('Next steps:');
    console.log(`  - Run ${chalk.bold('autobot "your task"')} to start a task`);
    console.log(`  - Or run ${chalk.bold('claude')} and use ${chalk.bold('/init-task')}`);
  });

program
  .command('status')
  .description('Show Autobot status for the current project')
  .action(() => {
    const projectDir = process.cwd();
    const { claudeExists, autobotExists, activeTask } = checkExistingState(projectDir);

    if (!claudeExists && !autobotExists) {
      console.log(chalk.yellow('Autobot not initialized in this directory.'));
      console.log(`Run ${chalk.bold('autobot init')} to set up.`);
      process.exit(0);
    }

    printPanel([
      `${chalk.bold.blue('Autobot Status')}`,
      `${chalk.dim('Directory:')} ${projectDir}`,
    ]);

    console.log(claudeExists ? `${CHECK} .claude/ exists` : `${CROSS} .claude/ missing`);
    console.log(autobotExists ? `${CHECK} .autobot/ exists` : `${CROSS} .autobot/ missing`);

    if (activeTask) {
      console.log();
      console.log(`${chalk.bold('Active Task:')} ${activeTask.title || 'Unknown'}`);
      console.log(`${chalk.bold('Status:')} ${activeTask.status || 'unknown'}`);

      // Try to load plan for progress
      const planFile = path.join(projectDir, '.autobot', 'plan.json');
      if (fs.existsSync(planFile)) {
        try {
          const plan = JSON.parse(fs.readFileSync(planFile, 'utf-8'));
          const subtasks = plan.subtasks || [];
          const completed = subtasks.filter(t => t.status === 'completed').length;
          const total = subtasks.length;
          if (total > 0) {
            console.log(`${chalk.bold('Progress:')} ${completed}/${total} subtasks`);
          }
        } catch {
          // Invalid plan file
        }
      }
    } else {
      console.log();
      console.log(chalk.dim('No active task.'));
    }
  });

program
  .command('clean')
  .description('Remove Autobot files from the current project')
  .option('--all', 'Also remove .claude/ directory (not just .autobot/)')
  .option('-y, --yes', 'Skip confirmation prompt')
  .action(async (options) => {
    const projectDir = process.cwd();
    const autobotDir = path.join(projectDir, '.autobot');
    const claudeDir = path.join(projectDir, '.claude');
    const claudeMd = path.join(projectDir, 'CLAUDE.md');

    console.log();

    if (!fs.existsSync(autobotDir) && !fs.existsSync(claudeDir)) {
      console.log(chalk.yellow('No Autobot files found.'));
      process.exit(0);
    }

    console.log(chalk.bold('Will remove:'));
    if (fs.existsSync(autobotDir)) {
      console.log('  - .autobot/');
    }
    if (options.all) {
      if (fs.existsSync(claudeDir)) {
        console.log('  - .claude/');
      }
      if (fs.existsSync(claudeMd)) {
        console.log('  - CLAUDE.md');
      }
    }

    console.log();

    if (!options.yes) {
      if (!await confirm('Continue?')) {
        process.exit(0);
      }
    }

    if (fs.existsSync(autobotDir)) {
      fs.rmSync(autobotDir, { recursive: true });
      console.log(`${CHECK} Removed .autobot/`);
    }

    if (options.all) {
      if (fs.existsSync(claudeDir)) {
        fs.rmSync(claudeDir, { recursive: true });
        console.log(`${CHECK} Removed .claude/`);
      }
      if (fs.existsSync(claudeMd)) {
        fs.unlinkSync(claudeMd);
        console.log(`${CHECK} Removed CLAUDE.md`);
      }
    }

    console.log();
    console.log(chalk.green('Cleanup complete.'));
  });

function preprocessArgs() {
  const knownCommands = new Set(['start', 'run', 'init', 'status', 'clean', 'help']);
  if (process.argv.length > 2) {
    const firstArg = process.argv[2];
    if (!firstArg.startsWith('-') && !knownCommands.has(firstArg)) {
      process.argv.splice(2, 0, 'start');
    }
  }
}

export { preprocessArgs };

export function cli() {
  preprocessArgs();
  program.parseAsync(process.argv);
}
