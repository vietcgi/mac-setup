# Contributing to Devkit

Thank you for your interest in contributing to Devkit! This guide explains how to contribute effectively.

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/devkit.git
cd devkit
```

### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Development Setup

```bash
# Install dependencies
./bootstrap.sh --python-only

# Install pre-commit hooks
pre-commit install

# Run tests
python3 -m unittest discover tests -v
```

## Code Standards

### Bash/Shell

- Use `shellcheck` for linting
- Follow Google Shell Style Guide
- Use `set -euo pipefail` for error handling
- Quote all variables: `"$VAR"` not `$VAR`
- Add comments for complex logic

### Python

- Use Python 3.9+
- Follow PEP 8 style guide
- Add type hints to all functions
- Include docstrings
- Use meaningful variable names

### Ansible

- Use `ansible-lint` for validation
- Write descriptive task names
- Add proper error handling
- Tag all tasks appropriately
- Use variables instead of hardcoding

### YAML

- Use 2-space indentation
- Keep line length under 100 characters
- Add comments for non-obvious configuration

## Testing

### Run Tests Locally

```bash
# All tests
python3 -m unittest discover tests -v

# Specific test file
python3 -m unittest tests.test_config_security -v

# Specific test
python3 -m unittest tests.test_config_security.TestConfigSecurityPermissions.test_secure_config_created_with_0600 -v
```

### Security Tests

```bash
# Config security tests
python3 -m unittest tests.test_config_security -v

# Plugin security tests
python3 -m unittest tests.test_plugin_security -v
```

### Pre-commit Checks

```bash
# Run all checks
pre-commit run --all-files

# Run specific hook
pre-commit run shellcheck --all-files
```

## Commit Messages

Follow this format (from CLAUDE.md):

```
<type>: <brief description (50 chars max)>

Fixes #<issue-number>
```

**Types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance
- `security:` - Security fixes

**Examples:**

- `feat: add health check script`
- `fix: resolve config permission issue`
- `docs: update CONTRIBUTING guide`
- `security: add checksum verification`

## Pull Request Process

1. **Create PR with descriptive title**
   - Use imperative mood: "Add feature" not "Added feature"
   - Reference issues: Fixes #123

2. **Fill PR template**
   - Describe changes
   - Add testing steps
   - Link related issues

3. **Ensure CI passes**
   - All tests must pass
   - shellcheck must pass
   - ansible-lint must pass
   - No new security issues

4. **Request review**
   - Tag relevant reviewers
   - Address feedback promptly

5. **Merge**
   - Squash small commits if needed
   - Use descriptive merge message

## Security Reporting

**DO NOT create public issues for security vulnerabilities.**

Instead:

1. Email security details to the maintainer
2. Include affected versions
3. Describe impact
4. Provide proof-of-concept if possible

See [SECURITY.md](SECURITY.md) for detailed policy.

## Documentation

- Update README.md for user-facing changes
- Update relevant docs in /docs directory
- Keep CHANGELOG.md updated
- Add docstrings to Python code
- Comment complex bash logic

## Performance

- Minimize shell invocations in loops
- Use built-in bash features when possible
- Profile slow operations
- Document performance characteristics

## Versioning

We follow [Semantic Versioning](https://semver.org/):

- MAJOR: Breaking changes
- MINOR: New features (backward-compatible)
- PATCH: Bug fixes

## Questions?

- Check existing [issues](https://github.com/vietcgi/devkit/issues)
- Review [documentation](README.md)
- See [SECURITY.md](SECURITY.md) for security info
- Check [SUPPORT.md](SUPPORT.md) for support options

## Code of Conduct

Be respectful, inclusive, and professional. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License

By contributing, you agree your code is licensed under Apache 2.0.

---

Happy contributing! 🎉
