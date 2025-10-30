# Devkit Remediation & Improvement Plan

## Executive Summary

This document outlines a comprehensive plan to address all audit findings and improve Devkit's security, performance, maintainability, and feature completeness. The plan is organized into phases with clear deliverables, dependencies, and effort estimates.

**Total Estimated Effort:** 6-8 weeks (one developer working full-time)
**Risk Level:** Low (all changes backward-compatible)
**Target Completion:** Q4 2025

---

## Table of Contents

1. [Phase 1: Critical Security Fixes](#phase-1-critical-security-fixes) - Week 1
2. [Phase 2: Release Management & Versioning](#phase-2-release-management--versioning) - Week 2
3. [Phase 3: Governance & Documentation](#phase-3-governance--documentation) - Week 2-3
4. [Phase 4: Quality Improvements](#phase-4-quality-improvements) - Week 3-4
5. [Phase 5: Performance Optimization](#phase-5-performance-optimization) - Week 4-5
6. [Phase 6: Monitoring & Observability](#phase-6-monitoring--observability) - Week 5-6
7. [Phase 7: Enterprise Features](#phase-7-enterprise-features) - Week 6-8

---

## Phase 1: Critical Security Fixes

**Duration:** Week 1 (5 days)
**Priority:** 🔴 CRITICAL
**Impact:** Prevents supply chain attacks, secures sensitive data
**Blockers:** None
**Depends On:** Nothing

### Task 1.1: Bootstrap Script Checksum Verification

**Objective:** Prevent malicious bootstrap script injection via MITM attacks

**Deliverables:**
- Checksum verification in bootstrap script
- CI/CD pipeline generates checksums on release
- Documentation updated with verification steps
- Backward compatibility for existing installations

**Files to Modify:**
```
bootstrap.sh                          # Add checksum verification
.github/workflows/release.yml         # Add checksum generation
README.md                             # Update installation instructions
docs/SECURITY.md                      # Document checksum verification
```

**Implementation Details:**

1. **Generate Checksums on Release**
```bash
# In CI/CD (release.yml)
- name: Generate bootstrap checksum
  run: |
    sha256sum bootstrap.sh > bootstrap.sha256
    cat bootstrap.sha256
    git add bootstrap.sha256
    git commit -m "chore: generate bootstrap checksum"
```

2. **Add Checksum Verification to Bootstrap**
```bash
# bootstrap.sh - Add at start
BOOTSTRAP_CHECKSUM="<SHA256>"  # Injected by CI on release

verify_bootstrap_integrity() {
    local expected="$BOOTSTRAP_CHECKSUM"
    if [ -z "$expected" ]; then
        log_warning "Bootstrap integrity check skipped (development mode)"
        return 0
    fi

    local actual=$(sha256sum "$0" | awk '{print $1}')
    if [ "$actual" != "$expected" ]; then
        log_error "Bootstrap script integrity check failed!"
        log_error "Expected: $expected"
        log_error "Got:      $actual"
        log_error "Script may be compromised. Aborting."
        return 1
    fi
    log_success "Bootstrap integrity verified"
}

# Call early
verify_bootstrap_integrity || exit 1
```

3. **Wrapper Script for Piped Installation**
```bash
# scripts/install.sh (new wrapper)
#!/bin/bash
set -euo pipefail

REPO="https://github.com/vietcgi/devkit"
BOOTSTRAP_URL="${REPO}/releases/download/v{VERSION}/bootstrap.sh"
CHECKSUM_URL="${REPO}/releases/download/v{VERSION}/bootstrap.sha256"

# Download checksum
EXPECTED=$(curl -fsSL "$CHECKSUM_URL" | awk '{print $1}')
SCRIPT=$(mktemp)
trap "rm -f $SCRIPT" EXIT

# Download script
curl -fsSL "$BOOTSTRAP_URL" -o "$SCRIPT"

# Verify
ACTUAL=$(sha256sum "$SCRIPT" | awk '{print $1}')
if [ "$ACTUAL" != "$EXPECTED" ]; then
    echo "ERROR: Checksum mismatch!"
    exit 1
fi

# Execute
bash "$SCRIPT" "$@"
```

**Acceptance Criteria:**
- ✅ Checksum generated on every release
- ✅ Bootstrap verifies checksum before execution
- ✅ Wrapper script available for piped installation
- ✅ Installation instructions updated
- ✅ All tests pass
- ✅ Backward compatibility maintained

**Effort:** 4 hours
**Owner:** DevOps / Security lead

---

### Task 1.2: Configuration Permission Validation

**Objective:** Ensure sensitive config files have secure file permissions

**Deliverables:**
- Permission validation in config_engine.py
- Automatic permission fixing
- Security warnings in logs
- Unit tests for permission validation

**Files to Modify:**
```
cli/config_engine.py                 # Add permission checks
tests/test_suite.py                  # Add permission tests
tests/ultra_test_suite.py           # Add edge case tests
docs/SECURITY.md                     # Document permissions
```

**Implementation:**

```python
# cli/config_engine.py - Add this method to ConfigurationEngine class

import os
import stat

def validate_and_secure_config_file(self, config_path: Path) -> None:
    """
    Validate and secure configuration file permissions.

    Raises:
        PermissionError: If file is owned by different user
        OSError: If unable to fix permissions
    """
    if not config_path.exists():
        # Create with secure permissions
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.touch(mode=0o600)
        self.logger.info(f"Created {config_path} with secure permissions (0600)")
        return

    # Get file stats
    try:
        stat_info = config_path.stat()
    except OSError as e:
        self.logger.error(f"Cannot access config file: {e}")
        raise

    # Check ownership
    current_uid = os.getuid()
    if stat_info.st_uid != current_uid:
        raise PermissionError(
            f"Config file {config_path} is owned by different user "
            f"(uid: {stat_info.st_uid}, current: {current_uid})"
        )

    # Check permissions
    mode = stat_info.st_mode & 0o777
    if mode != 0o600:
        self.logger.warning(
            f"Config file has insecure permissions: {oct(mode)}"
        )
        try:
            config_path.chmod(0o600)
            self.logger.info(f"Fixed config permissions to 0600")
        except OSError as e:
            self.logger.error(f"Cannot fix permissions: {e}")
            raise

def load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration with security validation."""
    config_path = config_path or self.get_default_config_path()

    # Validate and secure
    self.validate_and_secure_config_file(config_path)

    # Load (rest of existing code)
    ...
```

**Tests:**

```python
# tests/test_suite.py - Add these tests

import os
import tempfile
from pathlib import Path

class TestConfigSecurity(unittest.TestCase):
    def test_insecure_permissions_are_fixed(self):
        """Test that insecure config permissions are fixed."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            config_path = Path(tmp.name)
            # Create with insecure permissions (644)
            os.chmod(config_path, 0o644)

            engine = ConfigurationEngine()
            engine.validate_and_secure_config_file(config_path)

            # Verify fixed
            mode = os.stat(config_path).st_mode & 0o777
            self.assertEqual(mode, 0o600)

            config_path.unlink()

    def test_secure_permissions_unchanged(self):
        """Test that secure permissions are not changed."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            config_path = Path(tmp.name)
            os.chmod(config_path, 0o600)

            engine = ConfigurationEngine()
            engine.validate_and_secure_config_file(config_path)

            # Verify unchanged
            mode = os.stat(config_path).st_mode & 0o777
            self.assertEqual(mode, 0o600)

            config_path.unlink()

    def test_missing_config_created_secure(self):
        """Test that missing config is created with 0600."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"

            engine = ConfigurationEngine()
            engine.validate_and_secure_config_file(config_path)

            # Verify created and secure
            self.assertTrue(config_path.exists())
            mode = os.stat(config_path).st_mode & 0o777
            self.assertEqual(mode, 0o600)
```

**Acceptance Criteria:**
- ✅ Config permissions validated on load
- ✅ Insecure permissions automatically fixed
- ✅ Ownership verified
- ✅ Tests cover all scenarios
- ✅ Logging shows security actions

**Effort:** 3 hours
**Owner:** Security/Backend developer

---

### Task 1.3: Plugin System Hardening

**Objective:** Validate plugins before loading them

**Deliverables:**
- Plugin manifest validation
- Signature verification system
- Secure plugin loading
- Plugin development guidelines

**Files to Create/Modify:**
```
cli/plugin_validator.py               # New - validation logic
cli/plugin_system.py                  # Modify - integrate validator
plugins/.manifest.json                # New - plugin registry
docs/PLUGIN_DEVELOPMENT_GUIDE.md      # Update - security section
```

**Implementation:**

```python
# cli/plugin_validator.py (NEW FILE)

"""Plugin validation and security."""

import json
import hashlib
from pathlib import Path
from typing import Dict, Tuple, List
import logging

class PluginManifest:
    """Plugin manifest validation."""

    REQUIRED_FIELDS = {
        "name": str,
        "version": str,
        "author": str,
        "description": str,
    }

    OPTIONAL_FIELDS = {
        "homepage": str,
        "repository": str,
        "license": str,
        "requires": dict,
        "permissions": list,
    }

    def __init__(self, manifest_path: Path):
        self.path = manifest_path
        self.data = self._load()

    def _load(self) -> Dict:
        """Load manifest JSON."""
        if not self.path.exists():
            raise FileNotFoundError(f"Manifest not found: {self.path}")

        try:
            with open(self.path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid manifest JSON: {e}")

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate manifest against schema."""
        errors = []

        # Check required fields
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in self.data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(self.data[field], field_type):
                errors.append(f"Invalid type for {field}: expected {field_type.__name__}")

        # Validate version format (semantic)
        if "version" in self.data:
            if not self._is_valid_semver(self.data["version"]):
                errors.append(f"Invalid version format: {self.data['version']}")

        # Validate permissions (if specified)
        if "permissions" in self.data:
            valid_perms = {"filesystem", "network", "system", "environment"}
            invalid = set(self.data["permissions"]) - valid_perms
            if invalid:
                errors.append(f"Invalid permissions: {invalid}")

        return len(errors) == 0, errors

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Validate semantic version (X.Y.Z)."""
        import re
        return bool(re.match(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$', version))

class PluginValidator:
    """Comprehensive plugin validation."""

    def __init__(self, plugins_dir: Path, logger: logging.Logger = None):
        self.plugins_dir = plugins_dir
        self.logger = logger or self._setup_logger()
        self.manifest_registry = plugins_dir / ".manifest.json"

    def validate_plugin(self, plugin_name: str) -> Tuple[bool, str]:
        """
        Validate plugin before loading.

        Args:
            plugin_name: Name of plugin directory

        Returns:
            Tuple of (is_valid, message)
        """
        plugin_dir = self.plugins_dir / plugin_name

        # Check directory exists
        if not plugin_dir.is_dir():
            return False, f"Plugin directory not found: {plugin_dir}"

        # Load and validate manifest
        manifest_path = plugin_dir / "manifest.json"
        try:
            manifest = PluginManifest(manifest_path)
            is_valid, errors = manifest.validate()
            if not is_valid:
                return False, f"Manifest validation failed: {'; '.join(errors)}"
        except (FileNotFoundError, ValueError) as e:
            return False, str(e)

        # Check for required files
        init_file = plugin_dir / "__init__.py"
        if not init_file.exists():
            return False, f"Missing {init_file}"

        # Verify plugin class exists
        try:
            self._verify_plugin_class(plugin_dir)
        except Exception as e:
            return False, f"Cannot load plugin class: {e}"

        self.logger.info(f"✓ Plugin validated: {plugin_name}")
        return True, "Plugin validation passed"

    def _verify_plugin_class(self, plugin_dir: Path) -> None:
        """Verify plugin implements PluginInterface."""
        import importlib.util
        init_file = plugin_dir / "__init__.py"

        spec = importlib.util.spec_from_file_location(
            f"plugin_{plugin_dir.name}", init_file
        )
        module = importlib.util.module_from_spec(spec)

        # Don't execute yet - just check structure
        source = init_file.read_text()
        if "class Plugin" not in source:
            raise ValueError("No Plugin class found")

    def _setup_logger(self) -> logging.Logger:
        """Setup logger."""
        logger = logging.getLogger("devkit.plugin_validator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(levelname)s: %(message)s")
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
```

**Update plugin_system.py:**

```python
# cli/plugin_system.py - Modify load_plugin method

from plugin_validator import PluginValidator

class PluginLoader:
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.validator = PluginValidator(plugins_dir)

    def load_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Load plugin with validation."""
        # Validate first
        is_valid, message = self.validator.validate_plugin(plugin_name)
        if not is_valid:
            logging.error(f"Cannot load plugin {plugin_name}: {message}")
            return None

        # Now load
        plugin_dir = self.plugins_dir / plugin_name
        spec = importlib.util.spec_from_file_location(
            f"plugin_{plugin_name}",
            plugin_dir / "__init__.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module.Plugin()
```

**Plugin Development Guide Update:**

```markdown
# Section: Plugin Security Requirements

## Manifest Requirements

Every plugin must have a `manifest.json`:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "author": "Your Name <email@example.com>",
  "description": "What this plugin does",
  "homepage": "https://github.com/...",
  "license": "Apache-2.0",
  "permissions": ["filesystem", "environment"],
  "requires": {
    "devkit": ">=3.0.0"
  }
}
```

## Plugin Class Implementation

```python
# plugins/my_plugin/__init__.py

from cli.plugin_system import PluginInterface, HookInterface, HookContext

class Plugin(PluginInterface):
    name = "my-plugin"
    version = "1.0.0"
    description = "My plugin description"

    def initialize(self) -> None:
        """Initialize plugin - called on load."""
        pass

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles."""
        return {}

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hook implementations."""
        return {}

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate plugin integrity."""
        return True, []
```

## Security Best Practices

1. **Request minimal permissions** - Only request needed permissions
2. **No hardcoded secrets** - Use environment variables
3. **Validate inputs** - Sanitize all user input
4. **No external downloads** - Should not fetch from internet
5. **Version constraints** - Specify minimum Devkit version
```

**Acceptance Criteria:**
- ✅ Plugin manifest validated on load
- ✅ Plugin class implementation verified
- ✅ Semantic version validation
- ✅ Permission declaration system
- ✅ Loading fails safely on validation errors
- ✅ Documentation updated with security guidelines
- ✅ Tests cover validation scenarios

**Effort:** 6 hours
**Owner:** Backend/Architecture lead

---

**Phase 1 Summary:**
- **Total Duration:** 5 days
- **Total Effort:** 13 hours
- **Deliverables:** 3 critical security fixes
- **Test Coverage:** 100%
- **Status Tracking:** Use pull requests with security label

---

## Phase 2: Release Management & Versioning

**Duration:** Week 2 (4 days)
**Priority:** 🟠 HIGH
**Impact:** Enables trackable releases, enables upgrade path
**Depends On:** Phase 1 (partial - can start in parallel)

### Task 2.1: Implement Semantic Versioning

**Objective:** Establish clear versioning scheme and process

**Deliverables:**
- VERSION file
- Git tag strategy
- Version bumping automation
- Release notes template

**Files to Create/Modify:**
```
VERSION                               # New - current version
.github/workflows/version-check.yml   # New - version validation
scripts/bump-version.sh               # New - version bumping
CHANGELOG.md                          # New - change log
docs/RELEASE_PROCESS.md              # New - release guide
```

**Implementation:**

```bash
# VERSION file (NEW)
3.1.0

# scripts/bump-version.sh (NEW)
#!/bin/bash
# Bump semantic version

set -euo pipefail

CURRENT=$(cat VERSION)
MAJOR=$(echo $CURRENT | cut -d. -f1)
MINOR=$(echo $CURRENT | cut -d. -f2)
PATCH=$(echo $CURRENT | cut -d. -f3)

case "${1:-patch}" in
  major)
    MAJOR=$((MAJOR + 1))
    MINOR=0
    PATCH=0
    ;;
  minor)
    MINOR=$((MINOR + 1))
    PATCH=0
    ;;
  patch)
    PATCH=$((PATCH + 1))
    ;;
  *)
    echo "Usage: $0 [major|minor|patch]"
    exit 1
    ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
echo "$NEW_VERSION" > VERSION
echo "Bumped version: $CURRENT → $NEW_VERSION"
```

**CHANGELOG.md:**

```markdown
# Changelog

All notable changes to Devkit are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Configuration permission validation
- Plugin manifest validation system
- Bootstrap script checksum verification
- Health check script

### Fixed
- Ansible-lint compatibility issues

### Security
- Added checksum verification for downloads
- Implemented config file permission checks
- Hardened plugin system

## [3.1.0] - 2025-10-30

### Added
- Initial security audit implementation
- Enhanced error messages
- Retry logic with exponential backoff

### Fixed
- Configuration loading edge cases

## [3.0.0] - 2025-09-15

### Breaking Changes
- Changed config directory from ~/.mac-setup to ~/.devkit
- Dropped support for Python < 3.9

[Unreleased]: https://github.com/vietcgi/devkit/compare/v3.1.0...HEAD
[3.1.0]: https://github.com/vietcgi/devkit/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/vietcgi/devkit/releases/tag/v3.0.0
```

**Version Check CI:**

```yaml
# .github/workflows/version-check.yml (NEW)

name: Version Check

on:
  pull_request:
    paths: [VERSION, CHANGELOG.md]

jobs:
  version-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check version format
        run: |
          VERSION=$(cat VERSION)
          if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            echo "ERROR: Invalid version format: $VERSION"
            echo "Expected format: X.Y.Z (semantic versioning)"
            exit 1
          fi
          echo "✓ Version format valid: $VERSION"

      - name: Verify changelog updated
        run: |
          VERSION=$(cat VERSION)
          if ! grep -q "## \[$VERSION\]" CHANGELOG.md; then
            echo "ERROR: CHANGELOG.md not updated for version $VERSION"
            exit 1
          fi
          echo "✓ Changelog updated"

      - name: Check git tags
        run: |
          VERSION=$(cat VERSION)
          TAG="v$VERSION"
          if git rev-parse "$TAG" >/dev/null 2>&1; then
            echo "ERROR: Git tag already exists: $TAG"
            exit 1
          fi
          echo "✓ Tag not yet created: $TAG"
```

**Release Process Doc:**

```markdown
# Release Process

## Version Management

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backward-compatible)
- PATCH: Bug fixes

## Release Checklist

1. **Create Release Branch**
```bash
git checkout -b release/v3.2.0
```

2. **Update Version**
```bash
scripts/bump-version.sh minor  # or major/patch
git add VERSION
```

3. **Update CHANGELOG.md**
```markdown
## [3.2.0] - 2025-11-15

### Added
- New feature description

### Fixed
- Bug fix description

### Security
- Security improvement description
```

4. **Create Pull Request**
- Title: "chore: release v3.2.0"
- Label: "release"
- Wait for all checks to pass

5. **Merge PR**
```bash
git checkout main
git pull origin main
```

6. **Create Git Tag**
```bash
git tag -a v3.2.0 -m "Release version 3.2.0"
git push origin v3.2.0
```

7. **Create GitHub Release**
- GitHub Actions automatically creates release from tag
- Release notes generated from CHANGELOG.md

## Supported Versions

| Version | Status | Support Until |
|---------|--------|---------------|
| 3.1.x   | Active | Nov 2026      |
| 3.0.x   | LTS    | Nov 2027      |
| 2.x     | EOL    | Nov 2024      |

## Version Compatibility

- Python: 3.9+
- Ansible: 2.15+
- macOS: 13.0+
- Linux: Ubuntu 20.04+
```

**Acceptance Criteria:**
- ✅ VERSION file created and updated
- ✅ Semantic versioning enforced
- ✅ CHANGELOG.md maintained
- ✅ CI validates version format
- ✅ Release process documented
- ✅ Git tags auto-created on release

**Effort:** 4 hours
**Owner:** Release Manager

---

### Task 2.2: Automated Release Pipeline

**Objective:** Automate release creation and distribution

**Deliverables:**
- GitHub Actions release workflow
- Automated changelog generation
- Release asset creation (checksums, SBOM)
- GitHub release publishing

**Files to Create/Modify:**
```
.github/workflows/release.yml         # Update - full automation
.github/workflows/publish.yml         # New - publish to releases
cliff.toml                            # New - changelog generation config
```

**Implementation:**

```yaml
# .github/workflows/release.yml (UPDATED)

name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  # Verify tag matches VERSION file
  verify:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - uses: actions/checkout@v4

      - name: Extract version from tag
        id: version
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          VERSION=${TAG#v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          FILE_VERSION=$(cat VERSION)
          if [ "$VERSION" != "$FILE_VERSION" ]; then
            echo "ERROR: Tag version ($VERSION) doesn't match VERSION file ($FILE_VERSION)"
            exit 1
          fi
          echo "✓ Version verified: $VERSION"

  # Run security checks before release
  security:
    needs: verify
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run security scans
        run: |
          shellcheck bootstrap.sh
          ansible-lint setup.yml
          pre-commit run --all-files

  # Build release assets
  build:
    needs: [verify, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate checksums
        run: |
          sha256sum bootstrap.sh > bootstrap.sha256
          sha256sum bootstrap-ansible.sh > bootstrap-ansible.sha256
          sha256sum verify-setup.sh > verify-setup.sha256

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          path: ./
          format: spdx-json
          output-file: sbom.spdx.json

      - name: Create release notes
        run: |
          VERSION=${{ needs.verify.outputs.version }}
          cat CHANGELOG.md | sed -n "/## \[$VERSION\]/,/## \[/p" | head -n -1 > RELEASE_NOTES.md

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-assets
          path: |
            bootstrap.sha256
            bootstrap-ansible.sha256
            verify-setup.sha256
            sbom.spdx.json
            RELEASE_NOTES.md

  # Create GitHub release
  publish:
    needs: [verify, build]
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v4
        with:
          name: release-assets

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v${{ needs.verify.outputs.version }}
          body_path: RELEASE_NOTES.md
          files: |
            bootstrap.sha256
            bootstrap-ansible.sha256
            verify-setup.sha256
            sbom.spdx.json
          draft: false
          prerelease: false
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Announce release
        run: |
          echo "✅ Release published: v${{ needs.verify.outputs.version }}"
          echo "GitHub: https://github.com/vietcgi/devkit/releases/v${{ needs.verify.outputs.version }}"
```

**Changelog Generation Config:**

```toml
# cliff.toml (NEW - if using git-cliff)

[changelog]
# changelog header
header = """
# Changelog\n
All notable changes to this project are documented in this file.
"""

# template for the changelog body
body = """
{% if version %}\
    ## [{{ version }}] - {{ timestamp | date(format="%Y-%m-%d") }}
{% else %}\
    ## [Unreleased]
{% endif %}\
{% for group, commits in commits | group_by(attribute="group") %}
    ### {{ group | upper }}
    {% for commit in commits %}
        - {% if commit.breaking %}[BREAKING] {% endif %}{{ commit.message | upper_first }} ([`{{ commit.id | truncate(length=7, end="") }}`](https://github.com/vietcgi/devkit/commit/{{ commit.id }}))\
        {% if commit.body %}\
         \
            {{ commit.body | indent(prefix="  ") }}\
        {% endif %}\
    {% endfor %}
{% endfor %}
"""

# Commit groups
[[changelog.transformer]]
pattern = "^feat"
group = "Added"

[[changelog.transformer]]
pattern = "^fix"
group = "Fixed"

[[changelog.transformer]]
pattern = "^doc"
group = "Documentation"

[[changelog.transformer]]
pattern = "^perf"
group = "Performance"

[[changelog.transformer]]
pattern = "^refactor"
group = "Changed"

[[changelog.transformer]]
pattern = "^test"
group = "Testing"

[[changelog.transformer]]
pattern = "^chore"
group = "Miscellaneous"
```

**Acceptance Criteria:**
- ✅ Tag triggers automated release
- ✅ Security checks run before release
- ✅ Checksums generated and included
- ✅ SBOM generated and included
- ✅ Release notes created from CHANGELOG.md
- ✅ GitHub release published automatically
- ✅ All artifacts included in release

**Effort:** 5 hours
**Owner:** DevOps/Release Manager

---

**Phase 2 Summary:**
- **Total Duration:** 4 days
- **Total Effort:** 9 hours
- **Deliverables:** Versioning system + automated releases
- **Status Tracking:** Use GitHub releases

---

## Phase 3: Governance & Documentation

**Duration:** Week 2-3 (5 days)
**Priority:** 🟠 HIGH
**Impact:** Clear contribution process, security incident handling
**Depends On:** Phase 1, Phase 2

### Task 3.1: Create CONTRIBUTING.md

**Objective:** Establish clear contribution guidelines

**Deliverables:**
- CONTRIBUTING.md file
- Issue and PR templates
- Code of conduct
- Commit message guidelines

**Files to Create/Modify:**
```
CONTRIBUTING.md                      # New
CODE_OF_CONDUCT.md                   # New
.github/ISSUE_TEMPLATE/bug.yml       # New
.github/ISSUE_TEMPLATE/feature.yml   # New
.github/pull_request_template.md     # New
```

**Implementation:**

See detailed CONTRIBUTING.md in Audit Report section 21.

**PR Template:**

```markdown
# Pull Request

## Description

Brief description of changes

## Type

- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation
- [ ] Security fix
- [ ] Refactoring

## Related Issues

Fixes #<issue-number>

## Changes Made

- [ ] Change 1
- [ ] Change 2

## Testing

How was this tested?

- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing on macOS
- [ ] Manual testing on Linux
- [ ] All CI checks pass

## Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added/updated
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Commit messages follow guidelines
- [ ] Branch is up to date with main

## Screenshots (if applicable)

<!-- Add screenshots for UI changes -->
```

**Issue Templates:**

```yaml
# bug.yml
name: Bug Report
description: Report a bug

body:
  - type: textarea
    attributes:
      label: Describe the bug
      description: Clear description of the issue
    validations:
      required: true

  - type: input
    attributes:
      label: Devkit version
      description: Version where bug occurs (e.g., 3.1.0)
    validations:
      required: true

  - type: input
    attributes:
      label: OS/Version
      description: e.g., macOS 14.6, Ubuntu 22.04
    validations:
      required: true

  - type: textarea
    attributes:
      label: Steps to reproduce
      description: |
        1. Run ...
        2. ...
    validations:
      required: true

  - type: textarea
    attributes:
      label: Expected behavior
      description: What should happen
    validations:
      required: true

  - type: textarea
    attributes:
      label: Actual behavior
      description: What actually happens
    validations:
      required: true

  - type: textarea
    attributes:
      label: Error messages/logs
      description: |
        ```
        Paste error output here
        ```
```

**CODE_OF_CONDUCT.md:**

```markdown
# Code of Conduct

## Our Commitment

We are committed to providing a welcoming and inspiring community for all.

## Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing opinions
- Accepting constructive criticism gracefully
- Focusing on what is best for the community
- Showing empathy towards other community members

## Enforcement

Violations may be reported to devkit@example.com. All reports will be reviewed.

Consequences:
1. Verbal warning
2. Temporary suspension
3. Permanent ban from project

For full policy, see our [Security Policy](SECURITY.md).
```

**Acceptance Criteria:**
- ✅ CONTRIBUTING.md complete and detailed
- ✅ Issue templates created
- ✅ PR template created
- ✅ CODE_OF_CONDUCT.md created
- ✅ Commit message guidelines documented

**Effort:** 3 hours
**Owner:** Community Lead

---

### Task 3.2: Create Upgrade Guide

**Objective:** Document how to upgrade between versions

**Deliverables:**
- UPGRADE.md with migration instructions
- Backward compatibility information
- Breaking change documentation
- Rollback procedures

**Files to Create:**
```
UPGRADE.md                            # New
docs/MIGRATION_GUIDES.md              # New
```

**Implementation:**

```markdown
# Upgrade Guide

## Overview

Devkit follows [Semantic Versioning](https://semver.org/).
- **PATCH**: No breaking changes
- **MINOR**: New features (backward-compatible)
- **MAJOR**: Breaking changes

## Quick Upgrade

```bash
# Backup your setup
cp -r ~/.devkit ~/.devkit.backup

# Update Devkit
cd devkit
git fetch origin
git checkout main
git pull origin main

# Re-run setup
./bootstrap.sh
```

## Version-Specific Upgrades

### Upgrading from 3.0.x to 3.1.x

**What changed:**
- Configuration directory: `~/.mac-setup` → `~/.devkit`
- New security features: config permission validation
- Plugin system hardened

**Migration:**

```bash
# Backup old config
cp -r ~/.mac-setup ~/.mac-setup.backup

# New bootstrap will create ~/.devkit
./bootstrap.sh

# Optional: Copy custom plugins (if any)
cp ~/.mac-setup/plugins/* ~/.devkit/plugins/
```

**Backward compatibility:** ✅ Full (auto-migrates on first run)

### Upgrading from 2.x to 3.x

⚠️ **Major breaking changes - manual migration required**

**What changed:**
- Config directory moved
- Python requirements upgraded to 3.9+
- Ansible 2.15+ required

**Migration Steps:**

```bash
# 1. Backup everything
cp -r ~/.mac-setup ~/.mac-setup.v2.backup

# 2. Update to 3.x
git checkout main
git fetch origin
./bootstrap.sh

# 3. Reconfigure custom settings
# Edit ~/.devkit/config.yaml with your preferences

# 4. Verify installation
./verify-setup.sh
```

**Known issues:**
- Old casks may not be installed (re-run Brewfile)
- Custom roles need updating to new paths

## Rollback Procedure

If something goes wrong:

```bash
# Restore from backup
rm -rf ~/.devkit
cp -r ~/.devkit.backup ~/.devkit

# Revert code
git checkout <previous-tag>
./bootstrap.sh
```

## Getting Help

- Check [CHANGELOG.md](CHANGELOG.md) for all changes
- See [SECURITY.md](SECURITY.md) for security updates
- [Open an issue](https://github.com/vietcgi/devkit/issues) if stuck
- See [SUPPORT.md](SUPPORT.md) for support options
```

**Acceptance Criteria:**
- ✅ Upgrade path documented for all versions
- ✅ Migration scripts provided
- ✅ Rollback procedure clear
- ✅ Breaking changes clearly marked

**Effort:** 2 hours
**Owner:** Documentation lead

---

**Phase 3 Summary:**
- **Total Duration:** 5 days
- **Total Effort:** 5 hours
- **Deliverables:** Governance docs + contribution guidelines + upgrade guide

---

## Phase 4: Quality Improvements

**Duration:** Week 3-4 (6 days)
**Priority:** 🟡 MEDIUM
**Impact:** Better error messages, consistent code quality

### Task 4.1: Enhanced Error Messages

**Objective:** Provide helpful error messages with suggested fixes

**Deliverables:**
- Error message standardization
- Suggested fixes in errors
- Error logging/reporting
- Error documentation

**Files to Modify:**
```
bootstrap.sh                          # Update all errors
setup.yml                             # Add handlers
cli/*.py                              # Improve exceptions
docs/TROUBLESHOOTING.md               # New
```

**Implementation:**

```bash
# bootstrap.sh - Error handler pattern

error_homebrew_not_found() {
    log_error "Homebrew is not installed"
    log_info "To fix this:"
    log_info "  1. Run: /bin/bash -c \"\$(curl -fsSL https://brew.sh/install.sh)\""
    log_info "  2. Then run this script again"
    log_info ""
    log_info "For more help: https://docs.brew.sh/Installation"
    return 1
}

error_insufficient_disk_space() {
    local required=$1
    local available=$2
    log_error "Insufficient disk space!"
    log_error "  Required: ${required}GB"
    log_error "  Available: ${available}GB"
    log_info "To fix this:"
    log_info "  1. Free up disk space (use \`du -sh /*\`)"
    log_info "  2. Run this script again"
    return 1
}

# Usage
if ! check_disk_space 10; then
    error_insufficient_disk_space 10 5
    exit 1
fi
```

**Python Error Classes:**

```python
# cli/exceptions.py (new)

class DevkitError(Exception):
    """Base exception for Devkit."""

    def __init__(self, message: str, suggestion: str = None, exit_code: int = 1):
        self.message = message
        self.suggestion = suggestion
        self.exit_code = exit_code
        super().__init__(self.format_message())

    def format_message(self) -> str:
        msg = f"❌ {self.message}"
        if self.suggestion:
            msg += f"\n💡 Suggestion: {self.suggestion}"
        return msg

class ConfigError(DevkitError):
    """Configuration-related error."""
    pass

class ToolNotFoundError(DevkitError):
    """Required tool not found."""

    def __init__(self, tool: str, install_cmd: str = None):
        message = f"Required tool not found: {tool}"
        suggestion = f"Install with: {install_cmd}" if install_cmd else None
        super().__init__(message, suggestion)

class PermissionError(DevkitError):
    """Permission-related error."""
    pass

# Usage
try:
    load_config()
except ConfigError as e:
    logger.error(e)
    sys.exit(e.exit_code)
```

**Troubleshooting Documentation:**

```markdown
# Troubleshooting Guide

## Common Issues

### "Homebrew is required but not installed"

**Cause:** Homebrew not found in PATH

**Solutions:**
1. Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://brew.sh/install.sh)"
```

2. Add Homebrew to PATH:
```bash
# For macOS M1/M2/M3
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"

# For Linux
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

3. Restart terminal and try again

### "Insufficient disk space"

**Cause:** Not enough free disk space for packages

**Solutions:**
1. Check disk usage:
```bash
df -h                     # Overall usage
du -sh ~/                 # Home directory
du -sh /opt/homebrew      # Homebrew cache
```

2. Free up space:
```bash
# Remove Homebrew cache
brew cleanup --all

# Remove old downloads
rm -rf ~/Downloads/*

# Remove Docker images (if using Docker)
docker system prune
```

3. Try installation again

### "Configuration file not found"

**Cause:** Config directory doesn't exist or is corrupted

**Solutions:**
```bash
# Recreate config directory
mkdir -p ~/.devkit

# Bootstrap will create default config
./bootstrap.sh
```

## Getting Help

- Check [FAQ](FAQ.md)
- See [SECURITY.md](SECURITY.md) for security issues
- Open an [issue on GitHub](https://github.com/vietcgi/devkit/issues)
- See [SUPPORT.md](SUPPORT.md) for support options
```

**Acceptance Criteria:**
- ✅ All errors have helpful messages
- ✅ Suggestions provided for common issues
- ✅ Troubleshooting guide comprehensive
- ✅ Error messages consistent across codebase

**Effort:** 4 hours
**Owner:** Documentation/QA lead

---

### Task 4.2: Comprehensive Testing Enhancements

**Objective:** Improve test coverage and add edge case tests

**Deliverables:**
- pytest configuration
- Coverage reporting
- Integration tests
- Edge case tests

**Files to Create/Modify:**
```
pytest.ini                            # New
setup.cfg                             # New
tests/conftest.py                     # New
tests/test_config_edge_cases.py      # New
tests/test_performance.py             # New
.github/workflows/coverage.yml        # New
```

**Implementation:**

```ini
# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py ultra_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=cli
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80

markers =
    integration: Integration tests (deselect with '-m "not integration"')
    slow: Slow tests (deselect with '-m "not slow"')
    edge_case: Edge case tests
    security: Security-focused tests
    performance: Performance tests
```

```python
# tests/conftest.py (new)

import pytest
import tempfile
from pathlib import Path
from cli.config_engine import ConfigurationEngine

@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def config_engine(temp_config_dir):
    """Create ConfigurationEngine with temp directory."""
    return ConfigurationEngine(project_root=temp_config_dir)

@pytest.fixture
def sample_config(temp_config_dir):
    """Create sample configuration file."""
    config_file = temp_config_dir / "config.yaml"
    config_file.write_text("""
global:
  setup_name: Test Setup
  setup_environment: development
  enabled_roles: [core, shell]
""")
    return config_file
```

```python
# tests/test_config_edge_cases.py (new)

import pytest
import os
from pathlib import Path

class TestConfigEdgeCases:
    """Test configuration handling edge cases."""

    @pytest.mark.edge_case
    def test_config_with_special_characters(self, config_engine, temp_config_dir):
        """Test config with special characters in values."""
        config_file = temp_config_dir / "config.yaml"
        config_file.write_text("""
global:
  setup_name: "Test: Setup (2025) & Beyond!"
  setup_environment: development
""")
        config = config_engine.load(config_file)
        assert config['global']['setup_name'] == "Test: Setup (2025) & Beyond!"

    @pytest.mark.edge_case
    def test_config_missing_optional_fields(self, config_engine, temp_config_dir):
        """Test config works with missing optional fields."""
        config_file = temp_config_dir / "config.yaml"
        config_file.write_text("""
global:
  setup_name: Minimal Config
  enabled_roles: []
""")
        config = config_engine.load(config_file)
        assert config['global']['setup_name'] == "Minimal Config"

    @pytest.mark.edge_case
    def test_config_with_empty_strings(self, config_engine, temp_config_dir):
        """Test config handles empty strings gracefully."""
        config_file = temp_config_dir / "config.yaml"
        config_file.write_text("""
global:
  setup_name: ""
  setup_environment: development
""")
        # Should handle empty values
        config = config_engine.load(config_file)
        assert config['global']['setup_name'] == ""

    @pytest.mark.edge_case
    def test_config_with_comments_preserved(self, config_engine, temp_config_dir):
        """Test config preserves comments (if using ruamel.yaml)."""
        config_file = temp_config_dir / "config.yaml"
        config_file.write_text("""
# Main configuration
global:
  # Setup name
  setup_name: Test Setup
""")
        config = config_engine.load(config_file)
        assert config['global']['setup_name'] == "Test Setup"

    @pytest.mark.security
    def test_config_prevents_injection(self, config_engine, temp_config_dir):
        """Test that config prevents code injection."""
        config_file = temp_config_dir / "config.yaml"
        # Try YAML injection
        config_file.write_text("""
global:
  setup_name: "{{ __import__('os').system('whoami') }}"
""")
        config = config_engine.load(config_file)
        # Should be treated as literal string, not executed
        assert "import" in config['global']['setup_name']
```

**Coverage CI Workflow:**

```yaml
# .github/workflows/coverage.yml (new)

name: Coverage Report

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests with coverage
        run: |
          pytest --cov=cli --cov-report=xml --cov-report=html

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false

      - name: Generate coverage badge
        run: |
          coverage-badge -o coverage.svg -f
          git add coverage.svg || true

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: py-cov-action/python-coverage-comment-action@v3
        with:
          GITHUB_TOKEN: ${{ github.token }}
```

**Acceptance Criteria:**
- ✅ pytest configured
- ✅ Coverage reporting set up
- ✅ 80%+ code coverage
- ✅ Edge cases tested
- ✅ Security tests included
- ✅ CI integration

**Effort:** 5 hours
**Owner:** QA/Testing lead

---

**Phase 4 Summary:**
- **Total Duration:** 6 days
- **Total Effort:** 9 hours
- **Deliverables:** Better errors + comprehensive tests

---

## Phase 5: Performance Optimization

**Duration:** Week 4-5 (6 days)
**Priority:** 🟡 MEDIUM
**Impact:** 20-30% faster installations

### Task 5.1: Parallel Installation Implementation

**Objective:** Parallelize package installation where possible

**Deliverables:**
- Batch installation logic
- Parallel package processing
- Performance monitoring
- Before/after benchmarks

**Files to Create/Modify:**
```
cli/installer.py                      # New - installation orchestrator
ansible/roles/core/tasks/main.yml     # Update - parallel installation
scripts/benchmark.sh                  # New - performance testing
docs/PERFORMANCE.md                   # New
```

**Implementation:**

```python
# cli/installer.py (new)

import concurrent.futures
import subprocess
from typing import List, Dict, Callable
import logging
import time

class Installer:
    """Handles parallel package installation."""

    def __init__(
        self,
        max_workers: int = 8,
        timeout: int = 600,
        logger: logging.Logger = None
    ):
        self.max_workers = max_workers
        self.timeout = timeout
        self.logger = logger or self._setup_logger()
        self.results = {}

    def install_packages_parallel(
        self,
        packages: List[str],
        install_cmd: Callable[[str], str],
        batch_size: int = 10
    ) -> Dict[str, bool]:
        """
        Install packages in parallel batches.

        Args:
            packages: List of package names
            install_cmd: Function that returns install command for a package
            batch_size: Number of packages per batch

        Returns:
            Dict mapping package names to success status
        """
        results = {}

        # Process in batches
        for i in range(0, len(packages), batch_size):
            batch = packages[i:i + batch_size]
            self.logger.info(f"Installing batch {i//batch_size + 1}: {', '.join(batch)}")

            # Install batch in parallel
            batch_results = self._install_batch_parallel(batch, install_cmd)
            results.update(batch_results)

        return results

    def _install_batch_parallel(
        self,
        batch: List[str],
        install_cmd: Callable[[str], str]
    ) -> Dict[str, bool]:
        """Install a batch of packages in parallel."""
        results = {}

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(self._install_package, pkg, install_cmd): pkg
                for pkg in batch
            }

            for future in concurrent.futures.as_completed(futures):
                pkg = futures[future]
                try:
                    success = future.result(timeout=self.timeout)
                    results[pkg] = success
                    if success:
                        self.logger.info(f"✓ {pkg}")
                    else:
                        self.logger.warning(f"⚠ {pkg} - installation failed")
                except concurrent.futures.TimeoutError:
                    self.logger.error(f"✗ {pkg} - timeout")
                    results[pkg] = False
                except Exception as e:
                    self.logger.error(f"✗ {pkg} - {e}")
                    results[pkg] = False

        return results

    def _install_package(
        self,
        package: str,
        install_cmd: Callable[[str], str]
    ) -> bool:
        """Install a single package."""
        try:
            cmd = install_cmd(package)
            subprocess.run(
                cmd,
                shell=True,
                check=True,
                capture_output=True,
                timeout=self.timeout
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.debug(f"{package}: {e.stderr.decode()}")
            return False
        except Exception as e:
            self.logger.debug(f"{package}: {e}")
            return False

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("devkit.installer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(message)s")
            )
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
```

**Ansible Optimization:**

```yaml
# ansible/roles/core/tasks/main.yml (updated)

---
- name: Install core packages in parallel
  hosts: all
  vars:
    package_batch_size: 15
    max_parallel_tasks: 8

  tasks:
    - name: Read Brewfile
      ansible.builtin.set_fact:
        brewfile_packages: "{{ lookup('file', playbook_dir + '/Brewfile').split('\n') | select('match', '^brew') | list }}"

    - name: Install packages in parallel batches
      ansible.builtin.shell: |
        brew install {{ item }}
      loop: "{{ brewfile_packages }}"
      async: 600
      poll: 0
      register: brew_jobs
      changed_when: true

    - name: Wait for all installations to complete
      ansible.builtin.async_status:
        jid: "{{ item.ansible_job_id }}"
      register: job_result
      until: job_result.finished
      retries: 60
      delay: 10
      loop: "{{ brew_jobs.results }}"
```

**Benchmarking Script:**

```bash
#!/bin/bash
# scripts/benchmark.sh

set -euo pipefail

ITERATIONS=${1:-3}
RESULTS_FILE="benchmark-results.txt"

echo "🎯 Devkit Performance Benchmark"
echo "================================"
echo "Running $ITERATIONS iterations..."
echo

{
    echo "Benchmark Date: $(date)"
    echo "Devkit Version: $(cat VERSION)"
    echo "System: $(uname -a)"
    echo "Iterations: $ITERATIONS"
    echo
} > "$RESULTS_FILE"

for i in $(seq 1 $ITERATIONS); do
    echo "Iteration $i of $ITERATIONS..."

    # Clean environment
    rm -rf ~/.devkit

    # Measure setup time
    START=$(date +%s)
    timeout 600 ./bootstrap.sh --skip-gui 2>/dev/null || true
    END=$(date +%s)
    DURATION=$((END - START))

    echo "  Time: ${DURATION}s" | tee -a "$RESULTS_FILE"
done

# Calculate average
AVERAGE=$(grep "Time:" "$RESULTS_FILE" | grep -oE '[0-9]+' | awk '{sum+=$1} END {print sum/NR}')

echo
echo "================================"
echo "Results Summary"
echo "================================"
cat "$RESULTS_FILE"
echo
echo "Average installation time: ${AVERAGE}s"
```

**Acceptance Criteria:**
- ✅ Parallel installation working
- ✅ Batch size configurable
- ✅ 20-30% performance improvement
- ✅ Benchmarks documented
- ✅ Safe error handling in parallel

**Effort:** 6 hours
**Owner:** Performance/Backend engineer

---

### Task 5.2: Caching & Offline Mode

**Objective:** Enable offline/cached installations

**Deliverables:**
- Package cache system
- Offline installation mode
- Cache management CLI
- Cache documentation

**Implementation:**

```python
# cli/cache_manager.py (new)

import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict
import logging

class CacheManager:
    """Manages downloaded packages for offline/cached installation."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        logger: logging.Logger = None
    ):
        self.cache_dir = cache_dir or Path.home() / ".devkit" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or self._setup_logger()
        self.manifest_file = self.cache_dir / ".manifest.json"

    def get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / url_hash

    def is_cached(self, url: str) -> bool:
        """Check if URL is cached."""
        return self.get_cache_path(url).exists()

    def get_cached(self, url: str) -> Optional[bytes]:
        """Get cached content."""
        cache_path = self.get_cache_path(url)
        if cache_path.exists():
            return cache_path.read_bytes()
        return None

    def cache(self, url: str, content: bytes, metadata: Dict = None) -> None:
        """Cache downloaded content."""
        cache_path = self.get_cache_path(url)
        cache_path.write_bytes(content)

        # Update manifest
        manifest = self._load_manifest()
        manifest[str(cache_path)] = {
            "url": url,
            "size": len(content),
            "hash": hashlib.sha256(content).hexdigest(),
            "timestamp": str(Path.ctime(cache_path)),
            **(metadata or {})
        }
        self._save_manifest(manifest)

        self.logger.debug(f"Cached {url} ({len(content)} bytes)")

    def clear_cache(self, older_than_days: int = 30) -> int:
        """Clear old cache entries."""
        import time
        now = time.time()
        deleted = 0

        for cache_file in self.cache_dir.glob("*"):
            if cache_file.name == ".manifest.json":
                continue

            age_days = (now - cache_file.stat().st_mtime) / (24 * 3600)
            if age_days > older_than_days:
                cache_file.unlink()
                deleted += 1
                self.logger.debug(f"Deleted cache: {cache_file}")

        self.logger.info(f"Cleared {deleted} cache entries")
        return deleted

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())
        file_count = len(list(self.cache_dir.glob("*"))) - 1  # Exclude manifest

        return {
            "cache_dir": str(self.cache_dir),
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }

    def _load_manifest(self) -> Dict:
        """Load cache manifest."""
        if self.manifest_file.exists():
            return json.loads(self.manifest_file.read_text())
        return {}

    def _save_manifest(self, manifest: Dict) -> None:
        """Save cache manifest."""
        self.manifest_file.write_text(json.dumps(manifest, indent=2))

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("devkit.cache")
        return logger
```

**Acceptance Criteria:**
- ✅ Cache system working
- ✅ Offline mode functional
- ✅ Cache CLI tools
- ✅ Cache management

**Effort:** 5 hours
**Owner:** Backend engineer

---

**Phase 5 Summary:**
- **Total Duration:** 6 days
- **Total Effort:** 11 hours
- **Deliverables:** 20-30% performance improvement + offline mode

---

## Phase 6: Monitoring & Observability

**Duration:** Week 5-6 (5 days)
**Priority:** 🟡 MEDIUM
**Impact:** Visibility into setup status

### Task 6.1: Health Check System

**Objective:** Verify setup completeness and health

**Deliverables:**
- Comprehensive health check script
- Health status dashboard
- Metrics collection
- Health check CI job

**Implementation:**

```bash
#!/bin/bash
# scripts/health-check.sh (new)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check() {
    local name=$1
    local cmd=$2
    local required=${3:-true}

    if eval "$cmd" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $name"
        ((CHECKS_PASSED++))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $name (required)"
            ((CHECKS_FAILED++))
        else
            echo -e "${YELLOW}⚠${NC} $name (optional)"
            ((CHECKS_WARNING++))
        fi
        return 1
    fi
}

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Devkit Health Check${NC}"
echo -e "${BLUE}============================================${NC}"
echo

echo "Critical Tools:"
check "Bash" "bash --version" true
check "Git" "git --version" true
check "Homebrew" "brew --version" true
check "Ansible" "ansible --version" true
check "Python 3" "python3 --version" true

echo
echo "Development Tools:"
check "Node.js" "node --version" false
check "Go" "go version" false
check "Ruby" "ruby --version" false

echo
echo "Editors:"
check "Neovim" "nvim --version" false
check "VS Code" "code --version" false

echo
echo "Container Tools:"
check "Docker" "docker --version" false
check "kubectl" "kubectl version --client" false

echo
echo -e "${BLUE}============================================${NC}"
echo -e "Results: ${GREEN}✓$CHECKS_PASSED${NC} ${RED}✗$CHECKS_FAILED${NC} ${YELLOW}⚠$CHECKS_WARNING${NC}"
echo -e "${BLUE}============================================${NC}"

if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}❌ Health check failed - $CHECKS_FAILED required tools missing${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Health check passed${NC}"
exit 0
```

**Acceptance Criteria:**
- ✅ Health check script complete
- ✅ Detailed output with version info
- ✅ Critical vs optional tools distinguished
- ✅ Suggested fixes for missing tools

**Effort:** 3 hours

---

### Task 6.2: Logging & Metrics System

**Objective:** Collect setup metrics and logs

**Deliverables:**
- Structured logging
- Metrics collection
- Log rotation
- Metrics dashboard

**Implementation:**

```python
# cli/logger.py (new)

import logging
import json
from pathlib import Path
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for machine parsing."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "custom_fields"):
            log_data.update(record.custom_fields)

        return json.dumps(log_data)

def setup_logging(
    log_dir: Path = None,
    level: str = "INFO",
    json_output: bool = False
) -> logging.Logger:
    """Setup logging with file and console handlers."""
    log_dir = log_dir or Path.home() / ".devkit" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("devkit")
    logger.setLevel(getattr(logging, level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    logger.addHandler(console_handler)

    # File handler
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    file_handler = logging.FileHandler(log_file)

    if json_output:
        file_handler.setFormatter(JSONFormatter())
    else:
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )

    logger.addHandler(file_handler)

    return logger
```

**Acceptance Criteria:**
- ✅ Structured logging implemented
- ✅ Metrics collected
- ✅ Log rotation working
- ✅ JSON export available

**Effort:** 4 hours

---

**Phase 6 Summary:**
- **Total Duration:** 5 days
- **Total Effort:** 7 hours
- **Deliverables:** Health monitoring + logging/metrics

---

## Phase 7: Enterprise Features (Optional)

**Duration:** Week 6-8 (8 days)
**Priority:** 🟢 LOW (nice-to-have)
**Impact:** Enterprise readiness

### Task 7.1: Audit Logging

**Objective:** Track all setup changes for compliance

**Deliverables:**
- Audit log system
- Change tracking
- Compliance reporting
- Role-based access control

### Task 7.2: Web Dashboard (Optional)

**Objective:** Visual fleet management

**Deliverables:**
- Flask-based dashboard
- Fleet status view
- Setup history
- Configuration UI

---

## Implementation Timeline

```
WEEK 1: Phase 1 - Critical Security Fixes
├─ Mon: Bootstrap checksum + config permissions
├─ Tue-Wed: Plugin system hardening
├─ Thu-Fri: Testing & documentation
│
WEEK 2: Phase 2 & 3 - Versioning & Governance
├─ Mon-Tue: Semantic versioning + CI
├─ Wed-Thu: Contributing guide + issue templates
├─ Fri: Release process automation
│
WEEK 3: Phase 4 - Quality Improvements
├─ Mon-Tue: Enhanced error messages
├─ Wed-Fri: Comprehensive test suite
│
WEEK 4-5: Phase 5 - Performance
├─ Mon-Tue: Parallel installation
├─ Wed-Thu: Caching system
├─ Fri: Benchmarking & optimization
│
WEEK 6: Phase 6 - Monitoring
├─ Mon-Tue: Health check system
├─ Wed-Fri: Logging & metrics
│
WEEK 7-8: Phase 7 - Enterprise (Optional)
├─ Audit logging
├─ Web dashboard
└─ Enterprise documentation
```

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Security vulnerabilities | 0 | 3 |
| Test coverage | 85%+ | ~70% |
| Setup time | <8 min | ~10 min |
| Error resolution | Auto-fix 80% | ~50% |
| Documentation | 100% | ~85% |
| CI/CD coverage | All tests pass | Yes |
| Release automation | 100% | ~60% |

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Breaking changes | Medium | Feature flags, beta releases |
| Performance regression | Low | Benchmarking before/after |
| Documentation gaps | Low | Review by QA before release |
| Dependency conflicts | Medium | Thorough testing on all platforms |

---

## Conclusion

This remediation plan comprehensively addresses all audit findings across 7 phases:

1. **Phase 1:** Fixes critical security vulnerabilities
2. **Phase 2:** Establishes versioning and release process
3. **Phase 3:** Creates governance and contribution frameworks
4. **Phase 4:** Improves code quality and testing
5. **Phase 5:** Optimizes performance
6. **Phase 6:** Adds observability and monitoring
7. **Phase 7:** Enables enterprise features (optional)

**Total investment:** 6-8 weeks
**Impact:** Production-ready, maintainable, secure system
