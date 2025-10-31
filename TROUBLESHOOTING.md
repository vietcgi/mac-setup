# Troubleshooting Guide

## Common Issues and Solutions

### Installation & Setup

#### Issue: Setup script hangs or times out

**Symptoms:** The `bootstrap.sh` script hangs during Homebrew installation.

**Solutions:**

1. Check internet connectivity: `ping google.com`
2. Ensure Homebrew isn't already running: `ps aux | grep brew`
3. Try installing Homebrew manually:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

4. Clear Homebrew cache: `brew cleanup && brew update`
5. Try the setup again: `ansible-playbook setup.yml`

#### Issue: Permission denied on bootstrap.sh

**Symptoms:** `Permission denied: ./bootstrap.sh`

**Solution:**

```bash
chmod +x bootstrap.sh
./bootstrap.sh
```

#### Issue: Python version mismatch

**Symptoms:** `Python 3.9+ required` or similar version errors.

**Solutions:**

1. Check installed Python: `python3 --version`
2. Install via Homebrew (macOS):

   ```bash
   brew install python@3.13
   ```

3. Install via package manager (Linux):

   ```bash
   sudo apt update && sudo apt install python3.13  # Ubuntu/Debian
   sudo dnf install python3.13  # Fedora/RHEL
   ```

4. Use `mise` for version management:

   ```bash
   mise install python@3.13
   mise use python@3.13
   ```

---

### Pre-Commit Hooks

#### Issue: Pre-commit hooks are not running

**Symptoms:** Git commits succeed without running pre-commit checks.

**Solutions:**

1. Verify pre-commit is installed:

   ```bash
   which pre-commit
   pre-commit --version
   ```

2. Install if missing:

   ```bash
   pipx install pre-commit
   ```

3. Initialize hooks in repository:

   ```bash
   cd /path/to/devkit
   pre-commit install
   ```

4. Verify hook is installed:

   ```bash
   cat .git/hooks/pre-commit
   ```

5. Run hooks manually to test:

   ```bash
   pre-commit run --all-files
   ```

#### Issue: Pre-commit hook failures blocking commits

**Symptoms:** `pre-commit hook failed` when committing.

**Solutions:**

1. Review the specific failure:

   ```bash
   pre-commit run --all-files
   ```

2. Fix issues in your code (most auto-fixable by pre-commit)
3. Re-stage fixed files:

   ```bash
   git add .
   git commit -m "message"
   ```

4. For mypy type errors:
   - Add type annotations to your code
   - Or add type ignores: `# type: ignore[error-code]`
5. For formatting issues:
   - Let pre-commit auto-fix: `pre-commit run --all-files --fix`
   - Or manually run: `ruff format .`

#### Issue: Pre-commit cache issues

**Symptoms:** Hooks behave inconsistently or report stale errors.

**Solution:**

```bash
# Clear pre-commit cache
rm -rf ~/.cache/pre-commit
# Reinitialize hooks
pre-commit clean
pre-commit install
```

#### Issue: Running pre-commit on specific files

**Symptoms:** Want to check only changed files or specific paths.

**Solutions:**

```bash
# Run on changed files only
pre-commit run --from-ref origin/main --to-ref HEAD

# Run on specific file
pre-commit run --files cli/main.py

# Run only specific hooks
pre-commit run ruff --all-files
pre-commit run mypy --all-files
```

---

### Type Checking (mypy)

#### Issue: mypy STRICT mode too strict

**Symptoms:** `error: Function is missing a return type annotation` or similar strict errors.

**Solutions:**

1. Add type annotations:

   ```python
   def greet(name: str) -> str:
       return f"Hello, {name}"
   ```

2. Use type ignores for third-party libraries:

   ```python
   import untyped_module  # type: ignore[no-redef]
   ```

3. Update mypy.ini to exclude specific files:

   ```ini
   [mypy]
   exclude = ^tests/
   ```

#### Issue: Import errors in type checking

**Symptoms:** `error: Cannot find implementation or library stub for module named "xyz"`

**Solutions:**

1. Install type stubs:

   ```bash
   pip install types-<package-name>
   ```

2. Add to mypy.ini:

   ```ini
   [mypy]
   ignore_missing_imports = True
   ```

3. Use TYPE_CHECKING import guard:

   ```python
   from typing import TYPE_CHECKING
   if TYPE_CHECKING:
       from some_module import SomeClass
   ```

---

### Git & GitHub

#### Issue: Cannot push to repository (authentication)

**Symptoms:** `fatal: Authentication failed` or `Permission denied (publickey)`

**Solutions:**

1. Check SSH key setup:

   ```bash
   ls ~/.ssh/id_rsa  # or id_ed25519
   ssh -T git@github.com
   ```

2. Generate SSH key if missing:

   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   # Add public key to GitHub: https://github.com/settings/keys
   ```

3. Configure SSH URL rewrite (for this repo only):

   ```bash
   cd /path/to/devkit
   git config --local url."git@github.com:".insteadOf "https://github.com/"
   ```

#### Issue: Commit message validation failing

**Symptoms:** `pre-commit hook failed: commit-msg` or similar.

**Solution:** Follow commit message format from CONTRIBUTING.md:

```bash
<type>: <brief description>

Fixes #<issue>
```

Examples:

- ✅ `feat: add structured logging module`
- ✅ `fix: resolve memory leak in cache`
- ❌ `updated stuff` (too vague)
- ❌ `Fix stuff` (missing type prefix)

---

### Development Environment

#### Issue: Shell not activating virtual environment

**Symptoms:** Python packages not found after setup.

**Solutions:**

1. Reload shell configuration:

   ```bash
   source ~/.zshrc  # or ~/.bashrc for bash
   ```

2. Install direnv (if using .envrc):

   ```bash
   brew install direnv  # macOS
   sudo apt install direnv  # Ubuntu/Debian
   ```

3. Configure shell for direnv:

   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   eval "$(direnv hook zsh)"
   ```

4. Trust .envrc file:

   ```bash
   direnv allow
   ```

#### Issue: Python imports failing in development

**Symptoms:** `ModuleNotFoundError: No module named 'cli'`

**Solutions:**

1. Install package in development mode:

   ```bash
   pip install -e .
   ```

2. Set PYTHONPATH:

   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/devkit"
   ```

3. Run scripts from repo root:

   ```bash
   cd /path/to/devkit
   python -m cli.main  # instead of just cli.main
   ```

#### Issue: Tool not found in PATH

**Symptoms:** `command not found: ruff` or similar for development tools.

**Solutions:**

1. Verify installation:

   ```bash
   which ruff
   pip list | grep ruff
   ```

2. Reinstall if needed:

   ```bash
   pip install --upgrade ruff mypy pylint
   ```

3. Use python module syntax:

   ```bash
   python -m ruff check .
   python -m mypy cli/
   ```

---

### Testing

#### Issue: Tests fail locally but pass in CI

**Symptoms:** `pytest` passes locally but GitHub Actions fails.

**Solutions:**

1. Run with same Python version as CI:

   ```bash
   python --version  # Check your version
   # Install matching version via Homebrew or mise
   ```

2. Run all test commands from CI:

   ```bash
   pytest -v --cov=cli tests/
   ```

3. Check for file path assumptions:
   - Use `pathlib.Path` instead of string paths
   - Avoid hardcoding absolute paths

#### Issue: Coverage report discrepancies

**Symptoms:** Local coverage differs from CI coverage.

**Solution:**

```bash
# Clear coverage cache and rerun
rm -rf .coverage htmlcov
pytest --cov=cli --cov-report=html tests/
```

---

### Performance Issues

#### Issue: Pre-commit is slow

**Symptoms:** Pre-commit hooks take >10 seconds to run.

**Solutions:**

1. Run only changed files:

   ```bash
   pre-commit run --from-ref origin/main --to-ref HEAD
   ```

2. Skip certain hooks for development:

   ```bash
   SKIP=mypy,pylint git commit -m "message"
   ```

3. Check which hook is slowest:

   ```bash
   pre-commit run --all-files --verbose
   ```

4. Consider using `git commit --no-verify` sparingly for debugging:

   ```bash
   # Only when necessary - still test before PR
   git commit --no-verify -m "WIP: testing"
   ```

#### Issue: mypy type checking is slow

**Symptoms:** `pre-commit` hangs at mypy hook.

**Solutions:**

1. Check for circular imports or complex types
2. Use `# type: ignore` strategically for slow type checks
3. Run mypy incrementally:

   ```bash
   mypy cli/ --incremental
   ```

---

### Documentation & Help

#### Issue: Can't find documentation for feature

**Solutions:**

1. Check README.md: `Main project overview`
2. Check /docs: `Architecture, API, guides`
3. Check inline help:

   ```bash
   python -m cli --help
   ```

4. Check CONTRIBUTING.md: `Development workflow`
5. Check this file: `TROUBLESHOOTING.md`

---

## Getting Help

If you can't find a solution here:

1. **Search existing issues:** <https://github.com/vietcgi/devkit/issues>
2. **Check recent commits:** Changes may have fixed the issue
3. **Review documentation:** /docs directory has detailed guides
4. **Open an issue:** <https://github.com/vietcgi/devkit/issues/new>
   - Include: Python version, OS, error message, reproduction steps

---

## System Information for Debugging

When reporting issues, provide:

```bash
# System info
uname -a
python3 --version
pip --version
ansible --version

# Installation info
which pre-commit
pre-commit --version
git --version
git config --list

# Environment
echo $SHELL
echo $PATH
```

---

## Quick Reference Commands

```bash
# Setup & installation
ansible-playbook setup.yml
pre-commit install
pip install -e .

# Run checks
pre-commit run --all-files
pytest -v tests/
mypy cli/
ruff check .

# Fix issues automatically
ruff format .
ruff check . --fix
pre-commit run --all-files --fix

# Debug
pre-commit run --all-files --verbose
pytest -v --pdb tests/  # Drop into debugger on failure
python -m pdb cli/main.py  # Debug script
```

---

**Last Updated:** 2025-10-31
**Maintained by:** @vietcgi
