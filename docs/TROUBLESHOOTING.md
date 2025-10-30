# Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### "Command not found: brew"

**Cause:** Homebrew not installed or not in PATH

**Solution:**
```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://brew.sh/install.sh)"

# Add to PATH (macOS M1/M2/M3)
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
eval "$(/opt/homebrew/bin/brew shellenv)"

# Add to PATH (Linux)
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

# Verify
brew --version
```

#### "Insufficient disk space"

**Cause:** Not enough free space for packages (~5-10 GB needed)

**Solution:**
```bash
# Check disk usage
df -h

# Free up space
brew cleanup --all
rm -rf ~/Downloads/*
rm -rf ~/Library/Caches/*

# Check what's using space
du -sh ~/
du -sh /opt/homebrew/

# Try installation again
./bootstrap.sh
```

#### "Ansible not found"

**Cause:** Ansible not installed

**Solution:**
```bash
# Install Ansible
brew install ansible

# Verify
ansible --version

# Or let bootstrap install it
./bootstrap.sh
```

### Configuration Issues

#### "Configuration file not found"

**Cause:** Config directory doesn't exist

**Solution:**
```bash
# Recreate config directory
mkdir -p ~/.devkit

# Bootstrap will create default config
./bootstrap.sh
```

#### "Permission denied" on config file

**Cause:** Insecure file permissions

**Solution:**
```bash
# Fix permissions (done automatically now)
chmod 600 ~/.devkit/config.yaml

# Verify
ls -la ~/.devkit/config.yaml
# Should show: -rw------- (600)
```

#### "Invalid YAML in configuration"

**Cause:** Config file has YAML syntax errors

**Solution:**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('~/.devkit/config.yaml'))"

# Or use online validator: https://www.yamllint.com

# Fix the YAML and try again
./bootstrap.sh
```

### Plugin Issues

#### "Plugin validation failed"

**Cause:** Plugin missing manifest or invalid

**Solution:**
```bash
# Check plugin structure
ls -la ~/.devkit/plugins/your-plugin/
# Should have: manifest.json, __init__.py

# Validate manifest
python3 -c "from cli.plugin_validator import validate_plugin_manifest; validate_plugin_manifest(Path('manifest.json'))"

# Fix manifest and retry
./bootstrap.sh
```

#### "Plugin class not found"

**Cause:** Plugin doesn't implement Plugin interface

**Solution:**
```bash
# Check plugin implementation
cat ~/.devkit/plugins/your-plugin/__init__.py

# Must have:
# - import PluginInterface
# - class Plugin(PluginInterface)
# - Required methods: initialize, get_roles, get_hooks, validate
```

### Performance Issues

#### "Setup is slow"

**Cause:** Network or system bottleneck

**Solution:**
```bash
# Check network speed
time curl -o /dev/null https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh

# Check disk speed
time dd if=/dev/zero of=/tmp/test bs=1m count=100

# Skip unnecessary components
./bootstrap.sh --skip-gui  # Skip GUI apps
```

### Permission Issues

#### "Permission denied" on scripts

**Cause:** Scripts not executable

**Solution:**
```bash
# Make scripts executable
chmod +x bootstrap.sh
chmod +x scripts/*.sh

# Or run with bash explicitly
bash bootstrap.sh
```

#### "sudo: password required"

**Cause:** Passwordless sudo is disabled

**Solution:**
```bash
# Enter your password when prompted
# Or enable passwordless sudo (requires security understanding):
# See SECURITY.md for information
```

### Version Issues

#### "Git tag already exists"

**Cause:** Trying to create release for already-released version

**Solution:**
```bash
# Bump version
scripts/bump-version.sh minor  # or major/patch

# Update CHANGELOG.md
# Commit changes
git add VERSION CHANGELOG.md
git commit -m "chore: bump version"

# Create new tag
git tag -a v$(cat VERSION) -m "Release v$(cat VERSION)"
git push origin v$(cat VERSION)
```

#### "Version mismatch"

**Cause:** Git tag version doesn't match VERSION file

**Solution:**
```bash
# Check both
git describe --tags
cat VERSION

# They must match exactly (without 'v' prefix)
# If wrong, recreate tag:
git tag -d v3.1.0
git tag -a v3.1.0 -m "Release v3.1.0"
git push origin --delete v3.1.0
git push origin v3.1.0
```

### Verification Issues

#### "Verification failed"

**Cause:** Setup incomplete or misconfigured

**Solution:**
```bash
# Run verification with verbose output
./verify-setup.sh

# Fix any missing tools
# For each missing tool, run:
brew install tool-name

# Re-verify
./verify-setup.sh
```

#### "Some tools missing"

**Cause:** Tools not installed or not in PATH

**Solution:**
```bash
# List what's missing
./verify-setup.sh

# Install missing tools
brew install tool1 tool2 tool3

# Update PATH if needed
source ~/.zshrc  # or ~/.bashrc

# Re-verify
./verify-setup.sh
```

## Getting More Help

### Check Logs

```bash
# View setup logs
cat ~/.devkit/logs/setup.log

# View recent errors
grep ERROR ~/.devkit/logs/setup.log

# View bootstrap output
./bootstrap.sh 2>&1 | tee setup.log
```

### Find Documentation

- **Security issues:** [SECURITY.md](../SECURITY.md)
- **Installation:** [README.md](../README.md)
- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Upgrade:** [UPGRADE.md](../UPGRADE.md)
- **Support:** [SUPPORT.md](../SUPPORT.md)

### Report Issues

1. Check [existing issues](https://github.com/vietcgi/devkit/issues)
2. Include logs and version info
3. Describe steps to reproduce
4. For security issues, see [SECURITY.md](../SECURITY.md)

### Useful Commands

```bash
# Get system info
uname -a
cat /etc/os-release  # Linux only

# Check versions
brew --version
ansible --version
python3 --version
git --version

# Check PATH
echo $PATH

# Check installed packages
brew list

# Check logs
tail -100f ~/.devkit/logs/setup.log
```

## Prevention Tips

1. **Keep backups:**
   ```bash
   cp -r ~/.devkit ~/.devkit.backup
   ```

2. **Check before major upgrades:**
   ```bash
   ./verify-setup.sh
   ```

3. **Review logs after installation:**
   ```bash
   cat ~/.devkit/logs/setup.log
   ```

4. **Test in VM first:**
   ```bash
   multipass launch ubuntu:22.04 --name test
   ```

---

**Can't find your issue?** Check [SUPPORT.md](../SUPPORT.md) or open an issue on GitHub.
