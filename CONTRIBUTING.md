# Contributing to AI Release Automation

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/orchestrate-solutions/ai-release-automation.git
   cd ai-release-automation
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Code Style

- Use Black for code formatting: `black release_system/`
- Use isort for import sorting: `isort release_system/`
- Use flake8 for linting: `flake8 release_system/`
- Use mypy for type checking: `mypy release_system/`

## Testing

- Run tests: `pytest`
- Run with coverage: `pytest --cov=release_system`
- Run specific tests: `pytest tests/test_git_analyzer.py`

## ModuLink Chain Patterns

This project uses ModuLink-py for workflow orchestration. Follow these patterns:

- **Pure Functions**: Each link should be a pure async function
- **Context Flow**: Use context dictionary for data flow between links
- **Middleware**: Use middleware for cross-cutting concerns (logging, timing)
- **Error Handling**: Use explicit branching for error conditions

## Submitting Changes

1. Create a feature branch: `git checkout -b feat-new-feature`
2. Make your changes following the code style guidelines
3. Add tests for new functionality
4. Update documentation if needed
5. Run the test suite: `pytest`
6. Submit a pull request

## Release Process

This project uses its own AI release automation! Releases are managed through:

1. Automated commit message generation
2. AI-powered release note creation
3. Semantic version bumping
4. Automated changelog updates

## Questions?

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Check the documentation in the `docs/` directory
