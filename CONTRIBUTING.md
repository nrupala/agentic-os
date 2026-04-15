# Contributing to agentic-OS

Thank you for your interest in contributing to agentic-OS! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- GitHub account

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentic-OS.git
   cd agentic-OS
   ```

3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/nrupala/agentic-OS.git
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov ruff black isort bandit
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
# Format code
black .

# Check formatting
black --check .

# Sort imports
isort .
```

## Making Changes

1. **Write code** following the existing style
2. **Add tests** for new functionality
3. **Update documentation** as needed
4. **Run linting** to ensure code quality:
   ```bash
   ruff check .
   ```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```
feat(engine): add parallel execution support

Added parallel task execution with configurable workers and
circuit breaker pattern for fault tolerance.

Closes #123
```

```
fix(api): resolve async/sync execution mismatch

The run_in_executor was returning coroutine objects instead
of actual results. Fixed by creating synchronous wrapper.
```

## Pull Request Process

1. **Keep PRs focused** - One feature or fix per PR
2. **Update documentation** - Add docstrings and update README if needed
3. **Add tests** - Include tests for new functionality
4. **Ensure CI passes** - All checks must pass before merging

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CI passes
```

## Project Structure

```
agentic-OS/
├── engine/           # OMEGA execution engine
├── tools/           # Tool implementations
├── api/             # API server
├── dashboard/       # Web dashboard
├── security/        # Security modules
├── cognition/       # Cognitive subsystems
├── references/      # Reference documentation
├── tests/           # Test suite
└── docs/           # Documentation
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions
- Join the community!

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub profile linked in commit history

---

**Thank you for contributing to agentic-OS!**
