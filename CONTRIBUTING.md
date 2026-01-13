# Contributing to HD Logging

Thank you for your interest in contributing to HD Logging! This document provides guidelines and information for contributors.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). By participating, you agree to uphold this code.

## Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/hd-logging.git
   cd hd-logging
   ```

3. **Set up the development environment**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

### Development Tools

The project uses several tools for code quality:

- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing

Run all tools:
```bash
uv run black src/
uv run flake8 src/
uv run mypy src/
uv run pytest
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-async-logging`
- `bugfix/fix-rotation-issue`
- `docs/update-readme`

### Commit Messages

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(logger): add async logging support`
- `fix(rotation): resolve file handle leak`
- `docs(readme): update installation instructions`

### Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with appropriate tests
3. **Run the test suite** to ensure nothing breaks
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Examples updated if applicable

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Code Style

### Python Style

Follow PEP 8 with these additions:
- Use type hints for all function parameters and return values
- Use descriptive variable and function names
- Keep functions focused and small
- Add docstrings for all public functions

### Example

```python
def setup_logger(
    logger_name: str,
    log_file_path: Optional[str] = None,
    log_level_console: Optional[int] = None
) -> logging.Logger:
    """
    Set up a standardized logger with colorized console output.
    
    Args:
        logger_name: Name of the logger
        log_file_path: Path to the log file
        log_level_console: Console log level
        
    Returns:
        Configured logger instance
    """
    # Implementation here
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Include edge cases and error conditions

### Test Structure

```python
def test_setup_logger_basic():
    """Test basic logger setup."""
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO

def test_setup_logger_with_file():
    """Test logger setup with file output."""
    logger = setup_logger("test_logger", log_file_path="test.log")
    # Test file handler exists
    assert any(isinstance(h, SizeAndTimeLoggingHandler) for h in logger.handlers)
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=hd_logging

# Run specific test file
uv run pytest tests/test_logger.py

# Run with verbose output
uv run pytest -v
```

## Documentation

### Code Documentation

- Use docstrings for all public functions
- Include parameter descriptions and return values
- Add examples for complex functions
- Use type hints consistently

### User Documentation

- Update README.md for new features
- Add examples to the `examples/` directory
- Update API reference as needed
- Keep installation instructions current

## Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Update `__version__` in `__init__.py`
4. Create release notes
5. Tag the release
6. Publish to PyPI

## Reporting Issues

### Bug Reports

When reporting bugs, include:
- Python version
- Operating system
- HD Logging version
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

### Feature Requests

For feature requests, include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Implementation complexity estimate

## Getting Help

- 📧 Email: support@hackerdogs.ai
- 🐛 Issues: [GitHub Issues](https://github.com/tejaswiredkar/hd-logging/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/tejaswiredkar/hd-logging/discussions)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to HD Logging! 🎉

