# Upgrade Guide

## Overview

This guide explains how to upgrade Devkit between versions.

Devkit follows [Semantic Versioning](https://semver.org/):

- **PATCH** (3.1.X): No breaking changes - safe to upgrade
- **MINOR** (3.X.0): New features - backward compatible
- **MAJOR** (X.0.0): Breaking changes - may require manual steps

## Quick Upgrade

```bash
# Update Devkit
cd devkit
git fetch origin
git pull origin main

# Re-run setup
./bootstrap.sh

# Verify
./verify-setup.sh
```

## Version-Specific Upgrades

### Upgrading to 3.1.x from 3.0.x

**What Changed:**

- Configuration security hardening
- Plugin system validation
- Bootstrap checksum verification
- Enhanced documentation

**Migration:**

```bash
# No manual migration needed - automatic on first run
./bootstrap.sh

# Existing configs automatically secured
# Permissions fixed to 0600 if needed
```

**Backward Compatibility:** ✅ Full (auto-migrations on first run)

### Upgrading to 3.0.x from 2.x

⚠️ **Major Breaking Changes - Manual Migration Required**

**What Changed:**

- Config directory: `~/.devkit` → `~/.devkit`
- Python requirement: 3.9+
- Ansible requirement: 2.15+
- Main branch renamed: MASTER → main

**Migration Steps:**

```bash
# 1. Backup your setup
cp -r ~/.devkit ~/.devkit.v2.backup

# 2. Update to main branch
git remote set-url origin https://github.com/vietcgi/devkit.git
git checkout main
git pull origin main

# 3. Run new bootstrap
./bootstrap.sh

# 4. Reconfigure custom settings
# Edit ~/.devkit/config.yaml with your preferences

# 5. Copy custom plugins (if any)
cp ~/.devkit.v2.backup/plugins/* ~/.devkit/plugins/ 2>/dev/null || true

# 6. Verify installation
./verify-setup.sh
```

**Known Issues:**

- Old casks may not auto-install (re-run Brewfile)
- Custom roles need path updates
- Some environment variables may need reconfiguring

## Rollback Procedure

If something goes wrong after upgrade:

```bash
# Restore from backup
rm -rf ~/.devkit
cp -r ~/.devkit.backup ~/.devkit

# Revert code to previous version
git checkout v3.0.0  # or desired version
./bootstrap.sh

# Verify restored
./verify-setup.sh
```

## Finding Your Current Version

```bash
# Show current version
cat VERSION

# See recent releases
git log --oneline | grep -i release | head -5

# List all versions
git tag | grep "^v" | sort -V
```

## Checking What Changed

Before upgrading, see what's new:

```bash
# View changelog
cat CHANGELOG.md | head -50

# See specific version changes
git show v3.1.0:CHANGELOG.md

# See commits since your version
git log v3.0.0..v3.1.0 --oneline
```

## Testing Before Upgrade

For major version upgrades, test first:

```bash
# Create test VM/container
multipass launch ubuntu:22.04 --name test-devkit

# Transfer Devkit to test machine
multipass transfer devkit test-devkit:/home/ubuntu/

# Test the upgrade
multipass exec test-devkit -- bash ~/devkit/bootstrap.sh

# Verify it works
multipass exec test-devkit -- bash ~/devkit/verify-setup.sh

# If good, upgrade on real machine
# If bad, debug before real upgrade
```

## Troubleshooting

### "git: Command not found"

- Reinstall git: `brew install git`
- Update PATH: Check shell config

### "Permission denied" on scripts

- Make scripts executable: `chmod +x bootstrap.sh`
- Or use bash explicitly: `bash bootstrap.sh`

### "Python version mismatch"

- Check version: `python3 --version`
- Upgrade if needed: `brew install python@3.12`

### "Config file conflicts"

- Manually merge configs: `diff ~/.devkit/config.yaml ~/.devkit/config.yaml`
- Or start fresh: `rm ~/.devkit/config.yaml` then re-run

### "Missing dependencies"

- Reinstall: `brew install ansible`
- Update mise: `mise upgrade`
- Check pre-requisites: `./verify-setup.sh`

## Support

- See [SUPPORT.md](SUPPORT.md) for support options
- Check [FAQ](#faq) below
- Report issues: <https://github.com/vietcgi/devkit/issues>

## FAQ

**Q: Is it safe to upgrade?**
A: Yes, PATCH and MINOR upgrades are safe. MAJOR upgrades may require manual steps.

**Q: Will I lose my configuration?**
A: No, your config is preserved. Backups are created automatically.

**Q: Can I downgrade?**
A: Yes, see Rollback Procedure section.

**Q: How often should I upgrade?**
A: Upgrade at least monthly for security patches. Use your judgment for major versions.

**Q: What if upgrade fails?**
A: Use Rollback Procedure to restore previous version, then investigate.

**Q: Do I need to update manually?**
A: Yes, automatic updates are not enabled. Manual upgrade gives you control.

---

For more help, see [SUPPORT.md](SUPPORT.md) or open an issue on GitHub.
