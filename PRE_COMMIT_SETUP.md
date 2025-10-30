# Pre-Commit Framework: Multi-Language Quality Enforcement

## Overview

This project uses the **pre-commit** framework to automatically enforce code quality standards across multiple programming languages before every commit.

**Pre-commit** is a battle-tested, widely-adopted solution used by 240,000+ projects including Netflix, Google, and major open-source projects.

- **GitHub:** https://github.com/pre-commit/pre-commit
- **Documentation:** https://pre-commit.com
- **Stars:** 14.5k
- **License:** MIT (Open Source)

---

## What Gets Checked

### General Checks (All Files)
- **JSON/YAML/TOML/XML Syntax** - Validates file format integrity
- **Whitespace** - Removes trailing whitespace, fixes line endings
- **Line Endings** - Standardizes to LF (Unix-style)
- **Merge Conflicts** - Detects unresolved merge markers
- **Private Keys** - Prevents committing secrets
- **Large Files** - Blocks files > 100MB
- **Code Quality** - Detects debug statements and breakpoints

### Python
- **Ruff** - Fast linter + formatter (replaces Black, Flake8, isort, etc.)
  - Automatic code formatting
  - Code quality linting
  - Import sorting
  - Complexity checks

- **mypy** - Type checking
  - Validates type hints
  - Catches type errors
  - Strict mode enabled

- **bandit** - Security scanning
  - Detects hardcoded secrets
  - Identifies insecure patterns
  - Finds known vulnerabilities

### Shell Scripts
- **ShellCheck** - Bash/shell linting
  - Detects common errors
  - Suggests improvements
  - Validates syntax

### YAML/Configuration
- **yamllint** - YAML validation
  - Enforces consistent formatting
  - Validates syntax
  - Checks for common mistakes

### Markdown/Documentation
- **markdownlint** - Documentation quality
  - Consistent formatting
  - Proper spacing and indentation
  - Heading structure validation

---

## Installation

### Step 1: Install pre-commit Framework

```bash
pip install pre-commit
```

Or if you already have it installed, ensure you're using the latest version:

```bash
pip install --upgrade pre-commit
```

### Step 2: Install Git Hooks

This project includes a `.pre-commit-config.yaml` file that defines all hooks to run.

```bash
pre-commit install
```

This installs pre-commit hooks into `.git/hooks/pre-commit` and they'll run automatically before every commit.

### Step 3: Verify Installation

```bash
# Check that pre-commit is installed
pre-commit --version

# Check that hooks are installed
ls -la .git/hooks/pre-commit
```

---

## Usage

### Automatic (On Every Commit)

Once installed, hooks run automatically before each commit:

```bash
git commit -m "your commit message"

# Hooks run automatically...
# If any hook fails, commit is blocked
# Fix the issues and try again
```

### Manual Execution

Run hooks manually on all files:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files

# Run hooks on staged files only (normal behavior)
pre-commit run
```

### Bypass Hooks (Not Recommended)

If absolutely necessary, you can bypass hooks:

```bash
git commit --no-verify
```

⚠️ **Warning:** This bypasses all quality checks. Only use if you have a very good reason.

---

## Configuration

The `.pre-commit-config.yaml` file defines all hooks and their settings:

```yaml
---
default_language_version:
  python: python3.14

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    # General checks...

  - repo: https://github.com/astral-sh/ruff-pre-commit
    # Python linting/formatting...

  - repo: https://github.com/pre-commit/mirrors-mypy
    # Python type checking...

  # ... more tools
```

### Adding New Hooks

To add a new hook/tool:

1. Find the hook in the pre-commit registry: https://pre-commit.com/hooks.html
2. Add it to `.pre-commit-config.yaml`
3. Run `pre-commit install` to update hooks

Example: Add ESLint for JavaScript

```yaml
- repo: https://github.com/pre-commit/mirrors-eslint
  rev: v8.54.0
  hooks:
    - id: eslint
      types: [javascript]
```

### Updating Hooks

Keep hooks up-to-date:

```bash
# Update all hooks to latest versions
pre-commit autoupdate

# Verify the changes look good
git diff .pre-commit-config.yaml

# Commit the updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

---

## Common Issues

### Issue: "Pre-commit is not installed"

**Error:**
```
env: pre-commit: No such file or directory
```

**Solution:**
```bash
pip install pre-commit
```

### Issue: "No such file or directory: .git/hooks/pre-commit"

**Error:**
```
hook id: pre-commit
exit code: 127
```

**Solution:**
Run the installation again:
```bash
pre-commit install
```

### Issue: Hook Fails But You Need to Commit

**Option 1:** Fix the issue (recommended)
```bash
# Address the failure and try again
git commit -m "message"
```

**Option 2:** Bypass hooks (only if necessary)
```bash
git commit --no-verify -m "message"
```

### Issue: Ruff Auto-fixes Aren't Being Applied

Ruff can auto-fix some issues. If it's not working:

```bash
# Run ruff fix manually
ruff check --fix

# Then stage and commit
git add .
git commit -m "fix: ruff auto-fixes"
```

### Issue: mypy Complains About Missing Types

Some third-party packages don't have type stubs. You can:

**Option 1:** Ignore missing imports globally
- Already configured in `.pre-commit-config.yaml` with `--ignore-missing-imports`

**Option 2:** Ignore specific imports in code
```python
from some_package import something  # type: ignore
```

---

## Benefits Over Our Previous System

| Aspect | Old System (Bash) | Pre-commit Framework |
|--------|------------------|-------------------|
| **Languages Supported** | Python only | 20+ languages |
| **Setup** | Manual tool installation | Automatic dependency management |
| **Maintenance** | Update bash script | Update YAML config |
| **Community** | Custom (237 commits) | 240,000+ projects, active |
| **Dependencies** | Must pre-install all tools | Automatic installation |
| **Configuration** | Bash logic | YAML (simple, declarative) |
| **New Tools** | Write bash code | Add YAML entry |
| **CI/CD Integration** | Manual | pre-commit.ci (free for public repos) |

---

## Pre-Commit.ci (Optional)

For GitHub repositories, you can enable **pre-commit.ci** for automatic checks on pull requests:

https://pre-commit.ci

1. Visit https://pre-commit.ci and authorize GitHub
2. Enable this repository
3. Pre-commit hooks will automatically run on every PR
4. PRs won't merge until hooks pass

### Enable pre-commit.ci

Add `.pre-commit-ci.yaml`:

```yaml
# Optional: override default settings
ci:
  autofix_commit_msg: 'chore: pre-commit autofixes'
  autofix_prs: true
  autoupdate_branch: ''
```

---

## Advanced: Custom Hooks

You can create custom hooks in addition to pre-built ones:

```yaml
- repo: local
  hooks:
    - id: custom-check
      name: "My Custom Check"
      entry: ./scripts/my-check.sh
      language: script
      types: [python]
```

---

## Comparison with Other Solutions

### vs SonarQube
- **SonarQube:** Heavy, server-based, expensive for large teams
- **Pre-commit:** Lightweight, runs locally, free and open-source

### vs GitHub Actions
- **GitHub Actions:** Runs after push (slower feedback)
- **Pre-commit:** Runs before commit (immediate feedback)
- Use both: pre-commit for local development, GitHub Actions for CI

### vs Husky (Node.js)
- **Husky:** Limited to JavaScript/Node projects
- **Pre-commit:** Language-agnostic, supports 20+ languages

---

## Troubleshooting

### Performance Issues

If hooks are slow:

1. **Check what's slow:**
   ```bash
   time pre-commit run --all-files
   ```

2. **Disable slow hooks temporarily:**
   - Comment out in `.pre-commit-config.yaml`
   - Re-enable after fixing issues

3. **Use hook stages:**
   ```yaml
   stages: [commit, push]  # Only run on certain stages
   ```

### Cache Issues

Pre-commit caches virtual environments:

```bash
# Clear cache if stuck
rm -rf ~/.cache/pre-commit

# Reinstall
pre-commit install --install-hooks
```

---

## Quality Standards Summary

With pre-commit, devkit enforces:

✅ **Syntax validity** across all file types
✅ **Automatic formatting** (Ruff for Python)
✅ **Type safety** (mypy strict mode)
✅ **Security scanning** (bandit for Python, detect-private-key)
✅ **Code quality** (Ruff linting)
✅ **Shell script validation** (ShellCheck)
✅ **Configuration validation** (YAML linting)
✅ **Documentation quality** (markdownlint)

All checks happen **before commit**, ensuring only quality code reaches the repository.

---

## Next Steps

1. **Install pre-commit:**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Verify it works:**
   ```bash
   pre-commit run --all-files
   ```

3. **Fix any issues found:**
   ```bash
   # Most tools auto-fix, check with git diff
   git diff
   git add .
   git commit -m "fix: pre-commit issues"
   ```

4. **Make commits as normal:**
   ```bash
   git commit -m "your message"  # Hooks run automatically
   ```

---

## Resources

- **Pre-commit Documentation:** https://pre-commit.com
- **Available Hooks:** https://pre-commit.com/hooks.html
- **Pre-commit.ci:** https://pre-commit.ci
- **Ruff Documentation:** https://github.com/astral-sh/ruff
- **mypy Handbook:** https://mypy.readthedocs.io

---

## Questions?

This document explains everything needed to use the pre-commit framework in this project. For questions about specific tools or hooks, consult the documentation links above.
