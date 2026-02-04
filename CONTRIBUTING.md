# Contributing to Autobot

Thank you for your interest in contributing to Autobot!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/autobot/autobot.git
   cd autobot
   ```

2. **Install Node.js** (18+ required)

   See https://nodejs.org/ for installation instructions.

3. **Install dependencies**
   ```bash
   npm install
   ```

4. **Verify installation**
   ```bash
   node bin/autobot.js --version
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

### Before Submitting

1. Ensure all tests pass
2. Add tests for new functionality
3. Update documentation if needed

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
- Use ESM imports (`import`/`export`)
- Keep functions focused and small

## Testing Guidelines

- Write tests for new functionality
- Follow TDD when possible (test first)
- Use descriptive test names
- Use Vitest for testing
- Use setup/teardown helpers for common setup

## Questions?

Feel free to open an issue for discussion or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
