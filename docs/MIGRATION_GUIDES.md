# Migration Guides

This document provides detailed migration guides for upgrading between Devkit versions.

## Overview

Devkit follows [Semantic Versioning](https://semver.org/), so:

- **PATCH versions** (3.1.X): Safe to upgrade, no breaking changes
- **MINOR versions** (3.X.0): Safe to upgrade, new features only
- **MAJOR versions** (X.0.0): May have breaking changes

## Migration from 2.x to 3.0

### Breaking Changes

1. **Config Directory Migration**
   - Old: `~/.devkit/`
   - New: `~/.devkit/`

2. **Python Version Requirement**
   - Old: Python 3.8+
   - New: Python 3.9+

3. **Ansible Requirement**
   - Old: Ansible 2.10+
   - New: Ansible 2.15+

4. **Git Branch Rename**
   - Old: `MASTER` branch
   - New: `main` branch

### Migration Steps

```bash
# 1. Backup your setup
cp -r ~/.devkit ~/.devkit.v2.backup

# 2. Update repository
cd devkit
git remote set-url origin https://github.com/vietcgi/devkit.git
git checkout main
git pull origin main

# 3. Run new bootstrap
./bootstrap.sh

# 4. Reconfigure custom settings
# Edit ~/.devkit/config.yaml with your preferences

# 5. Migrate custom plugins (if any)
cp ~/.devkit.v2.backup/plugins/* ~/.devkit/plugins/ 2>/dev/null || true

# 6. Verify installation
./verify-setup.sh
```

### Migrating Custom Roles

If you have custom roles in `~/.devkit/roles/`:

```bash
# Copy custom roles to new location
cp -r ~/.devkit.v2.backup/roles/* ~/.devkit/roles/

# Update role paths in config.yaml
sed -i 's|~/.devkit|~/.devkit|g' ~/.devkit/config.yaml

# Verify roles still work
ansible-playbook ~/.devkit/roles/custom-role/tasks/main.yml
```

### Troubleshooting v2 → v3 Migration

**Issue: Old plugins don't work**

- **Cause**: Plugin structure changed
- **Solution**: See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md)

**Issue: Environment variables not recognized**

- **Cause**: Shell config not updated for new paths
- **Solution**: Update shell profile:

  ```bash
  sed -i 's|~/.devkit|~/.devkit|g' ~/.zshrc ~/.bashrc
  source ~/.zshrc
  ```

**Issue: Old casks won't auto-install**

- **Cause**: Brewfile references updated
- **Solution**: Re-run bootstrap:

  ```bash
  ./bootstrap.sh
  ```

## Migration from 3.0 to 3.1

### What Changed

- Configuration security hardening
- Plugin system validation
- Bootstrap checksum verification
- Enhanced documentation

### Migration Steps

```bash
# 1. Update code
cd devkit
git pull origin main

# 2. Re-run bootstrap (auto-migrates config)
./bootstrap.sh

# 3. Verify upgrade
./verify-setup.sh
```

**Auto-migrations that happen:**

- Config file permissions fixed to 0600
- Plugin manifests validated
- Security settings applied

### New Features Available

After upgrading to 3.1, you can use:

```bash
# Health checks
./verify-setup.sh

# Performance metrics
devkit health --json

# Audit logs
ls ~/.devkit/audit/
```

## Migration from 3.1 to 3.2 (Future)

Future versions will have clear migration paths documented here.

## Version-Specific Issues

### Python Package Conflicts

If you encounter Python package conflicts:

```bash
# Check Python version
python3 --version  # Must be 3.9+

# Upgrade Python
brew install python@3.12
brew link python@3.12

# Verify
python3 --version
./bootstrap.sh
```

### Ansible Incompatibility

If Ansible playbooks fail:

```bash
# Check Ansible version
ansible --version  # Must be 2.15+

# Upgrade Ansible
brew upgrade ansible

# Verify
ansible --version
./bootstrap.sh
```

### Homebrew Path Issues

If Homebrew isn't found after migration:

```bash
# Check Homebrew location
which brew

# If not found, add to PATH
# For M1/M2/M3 Macs
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# For Intel Macs
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# Verify
brew --version
./bootstrap.sh
```

## Downgrade / Rollback

If you need to downgrade to a previous version:

```bash
# 1. Backup current state
cp -r ~/.devkit ~/.devkit.backup.v3.1

# 2. Checkout previous version
cd devkit
git checkout v3.0.0

# 3. Re-run bootstrap
./bootstrap.sh

# 4. Verify downgrade
./verify-setup.sh
```

**Note:** Some features from newer versions won't be available after downgrading.

## Testing Migrations

Before upgrading production machines:

```bash
# Test in a virtual machine
multipass launch ubuntu:22.04 --name test-devkit

# Run migration steps in VM
multipass exec test-devkit -- bash ~/devkit/migrate.sh

# Verify it works
multipass exec test-devkit -- bash ~/devkit/verify-setup.sh

# If successful, upgrade real machine
# If failed, debug in VM before real upgrade
```

## Getting Help

- **Detailed logs**: `cat ~/.devkit/logs/setup.log`
- **Issues**: [GitHub Issues](https://github.com/vietcgi/devkit/issues)
- **FAQ**: [FAQ.md](../FAQ.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Having migration issues?** Check the logs first:

```bash
tail -50 ~/.devkit/logs/setup.log
```

If you find an issue, [file a bug report](https://github.com/vietcgi/devkit/issues/new?template=bug.yml) with:

- Your current version
- Your previous version
- Relevant log lines
- Steps to reproduce
