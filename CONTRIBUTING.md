# Contributing to RAM Optimizer

Thanks for your interest in contributing! This document outlines the process for contributing code, reporting bugs, and suggesting features.

## Code of Conduct

Be respectful, constructive, and collaborative. Assume good intent.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/RAM_Optimizer-for-Mac.git
   cd RAM_Optimizer-for-Mac
   ```
3. **Install dependencies and hooks:**
   ```bash
   make install
   ```
   This installs Python packages (`requirements.txt`), `pytest`, `pre-commit`, and sets up pre-commit hooks.

4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Running Tests

```bash
make test
```

All tests must pass before submitting a PR. We have 21 unit tests covering settings, formatting, logs, memory history, cache paths, and toggles.

### Linting and Formatting

```bash
make lint     # Check for issues
make format   # Auto-fix lint issues and format code
```

We use **ruff** for linting and formatting. Configuration is in `pyproject.toml`. Pre-commit hooks run automatically on every commit.

### Full CI Check

```bash
make check    # Runs lint + test
```

This is the same check that runs in CI on every push and PR.

### Cleaning Up

```bash
make clean    # Remove Python cache files
```

## Code Style

- Follow existing patterns in the codebase
- **Python:** 4-space indentation, 120-char line limit, double quotes
- **Docstrings:** Use triple-double-quotes for all methods
- **Naming:** `snake_case` for variables/functions, `CamelCase` for classes, `_private` prefix for non-public methods
- **Imports:** Sorted alphabetically (handled by ruff)
- **Error handling:** Use `except Exception` sparingly; prefer specific exceptions when possible

## Pull Request Guidelines

1. **Keep PRs focused** — one feature or fix per PR
2. **Update tests** — add or update tests for your changes
3. **Run `make check`** — ensure lint and tests pass locally
4. **Update CHANGELOG.md** — add your changes under an `[Unreleased]` section
5. **Write a clear description** — explain what you changed and why
6. **Reference issues** — link to any related issues

## Reporting Bugs

Use the **Bug Report** issue template when filing bugs. Include:
- Steps to reproduce
- Expected vs actual behavior
- macOS version and Python version (`python --version`)
- Any relevant logs (`~/.ram_optimizer.log`)

## Feature Requests

Open an issue with:
- A clear description of the feature
- Why it would be useful
- Any implementation ideas you have

## Security

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities. Do not open public issues for security problems.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thanks for helping improve RAM Optimizer!
