# Contributing to LAPA

Thank you for your interest in contributing to LAPA! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/username/lapa.git
cd lapa
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -e ".[dev]"
```

## Code Style

- We follow PEP 8 style guidelines
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [mypy](http://mypy-lang.org/) for static type checking
- Maximum line length is 88 characters (Black default)

## Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Run tests before submitting:

```bash
pytest
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your fork (`git push origin feature/amazing-feature`)
8. Create a Pull Request

### Pull Request Guidelines

- Use a clear, descriptive title
- Include relevant issue numbers in the description
- Update CHANGELOG.md if applicable
- Ensure all tests pass
- Add tests for new functionality
- Update documentation as needed

## Code Review Process

- All submissions require review
- Changes must be approved by at least one maintainer
- Address review feedback promptly
- Keep pull requests focused and atomic

## Documentation

- Update documentation for any changed functionality
- Include docstrings for all public functions/methods/classes
- Follow Google-style docstring format
- Keep README.md up to date

## Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use pytest fixtures when appropriate
- Write both unit and integration tests
- Aim for high test coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=lapa

# Run specific test file
pytest tests/test_specific.py

# Run tests matching pattern
pytest -k "test_pattern"
```

## Plugin Development

When developing plugins for LAPA:

1. Inherit from the base `Plugin` class
2. Implement required methods
3. Include comprehensive tests
4. Document plugin functionality
5. Follow plugin naming conventions

## IR System Development

When working with the Intermediate Representation system:

1. Maintain language-agnostic design
2. Document IR node types thoroughly
3. Include validation methods
4. Consider performance implications
5. Add appropriate test cases

## LLM Integration Development

When working on LLM integration:

1. Ensure proper error handling
2. Implement rate limiting
3. Add validation for LLM responses
4. Document API usage
5. Consider security implications

## Commit Guidelines

- Use clear, descriptive commit messages
- Follow conventional commits format:
  - feat: New feature
  - fix: Bug fix
  - docs: Documentation changes
  - style: Code style changes
  - refactor: Code refactoring
  - test: Test updates
  - chore: Maintenance tasks

## Branch Strategy

- `main`: Stable release branch
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

## Release Process

1. Update version number
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build and verify documentation
6. Create release tag
7. Merge to main branch

## Getting Help

- Check existing issues and documentation
- Join the community discussion
- Contact maintainers
- Follow the code of conduct

## Code of Conduct

Please note that LAPA has a Code of Conduct. By participating in this project, you agree to abide by its terms.

## License

By contributing to LAPA, you agree that your contributions will be licensed under the project's MIT license.
