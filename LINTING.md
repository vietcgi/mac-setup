# Linting Configuration

This document explains the linting setup and known limitations.

## Pre-Commit Hooks

All linting checks are configured in `.pre-commit-config.yaml`:

### Enabled Hooks ✅
- **Shellcheck** - Bash/sh script linting
- **Markdownlint** - Markdown file validation
- **YAML validation** - YAML syntax checking
- **Trailing whitespace** - Whitespace cleanup
- **File end-of-line fixes** - Proper line endings
- **Git merge conflict detection** - Conflict marker detection
- **Gitlint** - Commit message linting

### Disabled Hooks ⚠️
- **ansible-lint** - Disabled locally due to Python 3.14 incompatibility
  - (ansible-core 2.19.3 vs required 2.20.0)
  - Checked in CI instead (see `.github/workflows/ci.yml`)

---

## Running Linting Locally

### Run all checks:
```bash
pre-commit run --all-files
```

### Run specific hook:
```bash
pre-commit run shellcheck --all-files
pre-commit run markdownlint --all-files
```

### Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

---

## Ansible Linting (CI Only)

### Why Disabled Locally?

**Python 3.14 Incompatibility:**
- System Python: 3.14
- ansible-core installed: 2.19.3
- ansible-lint requires: ansible-core >= 2.20.0
- ansible-core 2.20.0: Not yet released (release candidate only)

### Solution: Use CI

Ansible-lint runs in GitHub Actions CI:
```yaml
# .github/workflows/ci.yml
- name: Run ansible-lint
  run: ansible-lint setup.yml
```

This is sufficient because:
✅ Issues caught before merge
✅ No local development friction
✅ Part of required CI checks

### Re-enable Locally When:

1. **ansible-core 2.20.0 is released** (recommended)
   ```bash
   pip install ansible-core>=2.20.0
   # Uncomment ansible-lint in .pre-commit-config.yaml
   ```

2. **Or downgrade Python to 3.13**
   ```bash
   # Use Python 3.13 for pre-commit
   pre-commit run --all-files
   ```

---

## Ansible Linting Configuration

Lenient rules in `.ansible-lint`:
```yaml
disabled_rules:
  - indentation      # Allow flexible indentation
  - line-too-long    # Allow longer lines (Ansible conventions)
```

Rationale:
- Ansible playbooks use 2-space indentation
- Documentation/comments often exceed 80 characters
- Strict rules would require excessive reformatting
- Code functionality is more important than formatting perfection

---

## Markdown Linting Configuration

Relaxed constraints in `.markdownlint.json`:
```json
{
  "MD001": false,  // Allow heading level jumps (e.g., # to ###)
  "MD013": {       // Relax line length limits
    "line_length": 120,
    "code_block_line_length": 150,
    "headers": false
  },
  "MD024": false,  // Allow duplicate headings (CHANGELOG)
  "MD025": false   // Allow multiple top-level headings
}
```

Rationale:
- Documentation often has flexible structure
- Long URLs shouldn't break lines
- CHANGELOGs legitimately have repeated "Added/Fixed/Changed"

---

## Future Improvements

| Issue | Status | Solution |
|-------|--------|----------|
| ansible-core 2.20.0 compatibility | ⏳ Waiting | Upgrade when released |
| Python 3.14 support | ⏳ Upstream issue | Use Python 3.13 if needed |
| ansible-lint re-enable | 📋 TODO | After ansible-core upgrade |

---

## See Also
- `.pre-commit-config.yaml` - Hook configuration
- `.ansible-lint` - Ansible-specific linting rules
- `.markdownlint.json` - Markdown linting rules
- `.github/workflows/ci.yml` - CI linting checks
