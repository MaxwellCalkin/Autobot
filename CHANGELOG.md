# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Migrated from Python to Node.js for easier portability (no Python environment needed)
- Hooks rewritten from Python to JavaScript
- Test suite migrated from pytest to Vitest

## [0.1.0] - 2024

### Added
- CLI commands: `start`, `init`, `status`, `clean`
- Autonomous loop with Stop hook
- Quality gates with automatic test running
- Specialized subagents: planner, builder, reviewer, fixer
- Task decomposition system
- Progress tracking with observations
- TDD skills (red, green, refactor)

### Documentation
- README with installation and usage
- Architecture documentation
- Hooks documentation
- Workflows documentation
