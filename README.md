# Autobot

<p align="center">
  <img src="assets/logo.png" alt="Autobot Logo" width="300"/>
</p>


[![CI](https://github.com/autobot/autobot/actions/workflows/ci.yml/badge.svg)](https://github.com/autobot/autobot/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Autonomous development assistant for Claude Code.

## Installation

```bash
# Using uv (recommended)
uv tool install autobot

# Using pip
pip install autobot

# Using pipx
pipx install autobot
```

## Usage

```bash
# Start an autonomous task
cd your-project
autobot "Build a login system with OAuth support"

# Initialize without starting a task
autobot init

# Check status
autobot status

# Clean up
autobot clean
```

## How It Works

Autobot scaffolds your project with:

- `.claude/` - Claude Code configuration (hooks, agents, commands, skills)
- `.autobot/` - Runtime state (task, progress, observations)
- `CLAUDE.md` - Project guidance for Claude

Then it launches Claude Code to work autonomously on your task.

## Features

- **Autonomous Loop** - Claude continues working until the task is complete
- **Test-First Development** - Tests run automatically after every code change
- **Quality Gates** - 3 consecutive test failures triggers a pause for review
- **Specialized Subagents** - Planner, Builder, Reviewer, Fixer
- **Progress Tracking** - Metrics and observations persisted across iterations

## Commands

| Command | Description |
|---------|-------------|
| `autobot "task"` | Scaffold and start autonomous task |
| `autobot init` | Scaffold without starting task |
| `autobot status` | Show project status |
| `autobot clean` | Remove .autobot/ directory |
| `autobot clean --all` | Remove both .autobot/ and .claude/ |

## Options

| Option | Description |
|--------|-------------|
| `--force`, `-f` | Overwrite existing configuration |
| `--no-launch` | Scaffold only, don't launch Claude |
| `--dry-run` | Preview what would be created |
| `--version`, `-v` | Show version |

## License

MIT
