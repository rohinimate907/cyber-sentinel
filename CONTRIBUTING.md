# Contributing to PentestX

Thank you for your interest in contributing to PentestX! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please treat all community members with respect and kindness.

## Getting Started

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pentestx.git
   cd pentestx
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements/requirements-dev.txt
   pip install -e .
   ```

4. **Setup Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Run Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/pentestx

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/pentestx --cov-report=html
```

### 4. Commit Your Changes

Use conventional commit messages:

```bash
git commit -m "feat: add new enumeration feature"
git commit -m "fix: resolve rate limiting issue"
git commit -m "docs: update API documentation"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Contribution Types

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to reproduce the bug
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, dependency versions
- **Logs**: Relevant error messages or logs

### Feature Requests

For feature requests, please provide:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should this be implemented?
- **Use Cases**: Real-world scenarios where this would be useful
- **Alternatives**: Other ways to solve the problem

### Code Contributions

#### Adding New Tool Integrations

To add a new third-party tool:

1. Create a new class in `src/pentestx/integrations/`
2. Inherit from `BaseToolIntegration`
3. Implement required methods
4. Add tests in `tests/test_integrations.py`
5. Update documentation

Example:

```python
from .base import BaseToolIntegration
from ..models import SubdomainResult

class NewToolIntegration(BaseToolIntegration):
    name = "newtool"
    
    async def run(self, target: str, **kwargs) -> List[SubdomainResult]:
        # Implementation here
        pass
    
    def is_available(self) -> bool:
        # Check if tool is installed
        pass
```

#### Adding New Output Formats

1. Create a new formatter in `src/pentestx/output.py`
2. Inherit from `BaseFormatter`
3. Implement the `format` method
4. Add tests
5. Update the CLI to support the new format

#### Adding New Netlas Queries

1. Add new methods to `NetlasClient` in `src/pentestx/netlas_client.py`
2. Create appropriate data models in `src/pentestx/models.py`
3. Update the pipeline to use new queries
4. Add comprehensive tests

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function parameters and return values
- Use dataclasses or Pydantic models for structured data
- Prefer async/await for I/O operations
- Use descriptive variable and function names

### Documentation Style

- Use Google-style docstrings
- Include examples in docstrings when helpful
- Keep line length under 100 characters
- Use Markdown for all documentation files

### Testing Guidelines

- Write tests for all new functionality
- Use pytest fixtures for common test data
- Mock external dependencies
- Aim for high test coverage (>90%)
- Include both unit and integration tests

Example test structure:

```python
import pytest
from unittest.mock import AsyncMock, patch

from pentestx.models import SubdomainResult
from pentestx.integrations.subfinder import SubfinderIntegration

class TestSubfinderIntegration:
    @pytest.fixture
    def integration(self):
        return SubfinderIntegration()
    
    @pytest.mark.asyncio
    async def test_run_success(self, integration):
        # Test implementation
        pass
    
    def test_is_available(self, integration):
        # Test implementation
        pass
```

## Project Structure

```
pentestx/
├── src/pentestx/           # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI interface
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   ├── netlas_client.py   # Netlas integration
│   ├── pipeline.py        # Core pipeline
│   ├── output.py          # Output formatters
│   ├── integrations/      # Tool integrations
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── subfinder.py
│   │   └── amass.py
│   └── utils/             # Utility functions
├── tests/                 # Test suite
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_netlas_client.py
│   ├── test_pipeline.py
│   ├── test_output.py
│   └── test_integrations.py
├── docs/                  # Documentation
├── configs/               # Configuration templates
├── requirements/          # Dependencies
└── scripts/               # Utility scripts
```

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `src/pentestx/__init__.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Update documentation
5. Create release PR
6. Tag release after merge
7. Publish to PyPI (maintainers only)

## Review Process

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Detailed description of changes
- **Testing**: Confirmation that tests pass
- **Documentation**: Updated documentation if needed
- **Breaking Changes**: Clear indication of any breaking changes

### Review Criteria

Reviewers will check for:

- **Functionality**: Does the code work as intended?
- **Style**: Follows project coding standards
- **Tests**: Adequate test coverage
- **Documentation**: Clear and up-to-date
- **Performance**: No significant performance regressions
- **Security**: No security vulnerabilities introduced

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code review and collaboration

### Getting Help

If you need help:

1. Check existing issues and documentation
2. Search previous discussions
3. Create a new issue with detailed information
4. Be patient and respectful in communications

## Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to PentestX!
