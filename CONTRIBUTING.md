# Contributing to Autobot

Thank you for your interest in contributing to Autobot!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/autobot/autobot.git
   cd autobot
   ```

2. **Install uv** (recommended package manager)

   See https://docs.astral.sh/uv/getting-started/installation/ for installation instructions.

3. **Create virtual environment and install dependencies**
   ```bash
   uv sync --all-extras
   ```

4. **Verify installation**
   ```bash
   uv run autobot --version
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/autobot

# Run specific test file
uv run pytest tests/test_cli.py
```

### Code Quality

```bash
# Lint code
uv run ruff check src tests

# Auto-fix linting issues
uv run ruff check src tests --fix

# Format code
uv run ruff format src tests

# Type check
uv run mypy src
```

### Before Submitting

1. Ensure all tests pass
2. Run linting and fix any issues
3. Add tests for new functionality
4. Update documentation if needed

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove)
- Reference issues when applicable (`Fix #123`)

## Code Style

- Follow existing code patterns in the codebase
- Use type hints for function signatures
- Write docstrings for public functions
- Keep functions focused and small

## Testing Guidelines

- Write tests for new functionality
- Follow TDD when possible (test first)
- Use descriptive test names
- Group related tests in classes
- Use fixtures for common setup

## Questions?

Feel free to open an issue for discussion or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
