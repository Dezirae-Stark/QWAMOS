# QWAMOS Linting Infrastructure

Comprehensive code quality, style, and formatting configuration for QWAMOS project.

## Overview

This directory contains configuration files for various linters and formatters used across
the QWAMOS codebase. The linting infrastructure ensures consistent code style, catches
common errors, and enforces security best practices.

## Quick Start

### Run All Linters Locally

```bash
# Python
black --check .
flake8 .
pylint **/*.py

# Kotlin
ktlint "**/*.kt" "**/*.kts"

# Shell
shellcheck **/*.sh
shfmt -d -i 2 **/*.sh

# Markdown
markdownlint "**/*.md"

# YAML
yamllint .

# EditorConfig
editorconfig-checker
```

### Auto-Fix Issues

```bash
# Python formatting
black .
isort .

# Kotlin formatting
ktlint -F "**/*.kt" "**/*.kts"

# Shell formatting
shfmt -w -i 2 **/*.sh
```

## Configuration Files

### Python

| File | Tool | Purpose |
|------|------|---------|
| `.pylintrc` | Pylint | Code quality and style checking |
| `.flake8` | Flake8 | Style guide enforcement (PEP 8) |
| `pyproject.toml` | Black, isort, mypy, pytest | Formatting, import sorting, type checking |

**Python Tools:**

- **Black**: Opinionated code formatter (120 char line length)
- **Pylint**: Comprehensive code quality checker
- **Flake8**: PEP 8 style guide enforcement
- **isort**: Import statement sorter
- **mypy**: Static type checker
- **Bandit**: Security issue scanner

**Installation:**

```bash
pip install black pylint flake8 mypy bandit isort pytest pytest-cov
```

### Kotlin

| File | Tool | Purpose |
|------|------|---------|
| `linting/ktlint-rules.yml` | ktlint | Kotlin style and formatting |
| `.editorconfig` | ktlint | Editor configuration (referenced by ktlint) |

**Kotlin Tools:**

- **ktlint**: Kotlin linter with strict formatting rules
  - No wildcard imports
  - Consistent indentation (4 spaces)
  - Proper naming conventions
  - Trailing commas in multi-line constructs

**Installation:**

```bash
curl -sSLO https://github.com/pinterest/ktlint/releases/download/1.0.1/ktlint
chmod +x ktlint
sudo mv ktlint /usr/local/bin/
```

### Shell Scripts

| File | Tool | Purpose |
|------|------|---------|
| `.shellcheckrc` | ShellCheck | Shell script static analysis |
| `linting/.shfmt.yaml` | shfmt | Shell script formatter |

**Shell Tools:**

- **ShellCheck**: Static analysis for shell scripts
  - Security issue detection
  - Common mistake prevention
  - Best practice enforcement
- **shfmt**: Shell script formatter (2 space indentation)

**Installation:**

```bash
# ShellCheck (Ubuntu/Debian)
sudo apt-get install shellcheck

# shfmt
curl -sSL https://github.com/mvdan/sh/releases/download/v3.7.0/shfmt_v3.7.0_linux_amd64 -o shfmt
chmod +x shfmt
sudo mv shfmt /usr/local/bin/
```

### Markdown

| File | Tool | Purpose |
|------|------|---------|
| `.markdownlint.json` | markdownlint | Markdown style checking |
| `linting/.markdownlintignore` | markdownlint | Files to ignore |

**Markdown Tools:**

- **markdownlint-cli**: Markdown linter and style checker
  - Consistent heading levels
  - Max line width (100 chars)
  - Fenced code blocks
  - Proper list formatting

**Installation:**

```bash
npm install -g markdownlint-cli
```

### YAML

**YAML Tools:**

- **yamllint**: YAML linter for syntax and style

**Installation:**

```bash
pip install yamllint
```

### EditorConfig

| File | Purpose |
|------|---------|
| `.editorconfig` | Consistent coding styles across editors and IDEs |

**EditorConfig** defines:

- Character encoding (UTF-8)
- Line endings (LF)
- Indentation style and size
- Final newline insertion
- Trailing whitespace trimming

Supported by most modern editors (VSCode, IntelliJ, Vim, etc.).

## GitHub Actions Workflow

The `.github/workflows/lint.yml` workflow automatically runs all linters on:

- Push to master
- Pull requests
- Manual trigger

**Jobs:**

1. **Python Lint**: Black, Flake8, Pylint, mypy, Bandit, isort
2. **Kotlin Lint**: ktlint
3. **Shell Lint**: ShellCheck, shfmt
4. **Markdown Lint**: markdownlint
5. **YAML Lint**: yamllint
6. **EditorConfig Check**: editorconfig-checker
7. **Summary**: Aggregate results

All jobs use `continue-on-error: true` to show warnings without failing the build.

## IDE Integration

### VSCode

Install extensions:

- Python: `ms-python.python`, `ms-python.black-formatter`
- Kotlin: `mathiasfrohlich.Kotlin`
- Shell: `timonwong.shellcheck`
- Markdown: `DavidAnson.vscode-markdownlint`
- EditorConfig: `EditorConfig.EditorConfig`

Settings will be automatically applied from configuration files.

### IntelliJ IDEA / Android Studio

1. Enable EditorConfig support (Settings → Editor → Code Style)
2. Install ktlint plugin
3. Configure Python inspections to use `.pylintrc`

### Vim/Neovim

Use ALE (Asynchronous Lint Engine) or CoC (Conquer of Completion):

```vim
" ALE configuration
let g:ale_linters = {
\   'python': ['black', 'flake8', 'pylint', 'mypy'],
\   'kotlin': ['ktlint'],
\   'sh': ['shellcheck'],
\   'markdown': ['markdownlint'],
\}

let g:ale_fixers = {
\   'python': ['black', 'isort'],
\   'kotlin': ['ktlint'],
\   'sh': ['shfmt'],
\}
```

## Pre-commit Hooks

To run linters before each commit, install pre-commit:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8

  - repo: https://github.com/PyCQA/pylint
    rev: v3.0.2
    hooks:
      - id: pylint

  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.9.0
    hooks:
      - id: shellcheck

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.37.0
    hooks:
      - id: markdownlint
```

Then install hooks:

```bash
pre-commit install
```

## Troubleshooting

### Black and Flake8 Conflicts

Black and Flake8 may disagree on line length and formatting. Our configuration:

- Line length: 120 characters (both)
- Flake8 ignores: E203, E501, W503, W504 (Black compatibility)

### Pylint Too Strict

Disable specific checks in `.pylintrc` or use inline comments:

```python
# pylint: disable=too-many-arguments
def my_function(arg1, arg2, arg3, arg4, arg5, arg6):
    pass
```

### ShellCheck False Positives

Disable specific checks inline:

```bash
# shellcheck disable=SC2086
echo $variable
```

Or in `.shellcheckrc` for project-wide disables.

### ktlint Errors

Auto-fix most ktlint issues:

```bash
ktlint -F "**/*.kt" "**/*.kts"
```

### Markdownlint Line Length

Code blocks have 120 char limit, regular text has 100 char limit.
Configure in `.markdownlint.json`:

```json
{
  "MD013": {
    "line_length": 100,
    "code_block_line_length": 120
  }
}
```

## Customization

### Adding New Rules

1. Edit the relevant configuration file
2. Test locally
3. Update this README
4. Submit PR with changes

### Disabling Rules

Only disable rules when absolutely necessary and document the reason:

```python
# Disable due to compatibility with legacy code
# pylint: disable=broad-except
```

## Best Practices

1. **Run linters before committing**: Catch issues early
2. **Fix warnings**: Don't accumulate technical debt
3. **Document exceptions**: Explain why rules are disabled
4. **Keep configs updated**: Review and update configurations regularly
5. **Use auto-formatters**: Let tools handle formatting

## Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Pylint Documentation](https://pylint.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [ktlint Documentation](https://pinterest.github.io/ktlint/)
- [ShellCheck Wiki](https://www.shellcheck.net/)
- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint)
- [EditorConfig Specification](https://editorconfig.org/)

## Contributing

When contributing to QWAMOS:

1. Ensure all linters pass locally
2. Fix any issues flagged by CI/CD
3. Follow the coding standards defined in these configs
4. Update linting configs if introducing new languages/tools

## License

See [LICENSE](../LICENSE) file.
