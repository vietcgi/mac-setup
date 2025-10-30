# Mac-Setup - No Python Installation Guide

**For systems without Python installed or Python-less setup**

---

## Overview

Mac-setup can be used without Python installed. All essential functionality is available through:

1. **Pure Bash Scripts** - Configuration management without Python
2. **Bootstrap Script** - Installs all prerequisites automatically
3. **Ansible Playbooks** - Core system configuration (no Python CLI needed)

---

## Quickest Setup (No Python Required)

### Option 1: One-Command Bootstrap (Recommended)

```bash
# Downloads and runs bootstrap script
curl -fsSL https://raw.githubusercontent.com/user/devkit/main/bootstrap.sh | bash
```

**What happens:**
1. ✅ Detects OS and architecture
2. ✅ Installs Homebrew (if needed)
3. ✅ Installs Python 3 (optional)
4. ✅ Installs Ansible
5. ✅ Creates default configuration
6. ✅ Runs Ansible setup

**Requirements:**
- bash (built-in)
- curl (built-in on most systems)
- Internet connection

---

### Option 2: Step-by-Step Bootstrap

```bash
# Clone the repository
git clone https://github.com/user/devkit.git
cd devkit

# Make bootstrap script executable
chmod +x bootstrap.sh

# Run with options
./bootstrap.sh                    # Full setup
./bootstrap.sh --interactive      # Interactive setup
./bootstrap.sh --verify-only      # Just check prerequisites
./bootstrap.sh --skip-python      # Setup without Python
```

---

## Minimal Setup (Pure Bash, No Python)

If you don't want Python installed at all:

```bash
# 1. Bootstrap (skip Python)
./bootstrap.sh --skip-python

# 2. Edit configuration (if needed)
nano ~/.devkit/config.yaml

# 3. Run Ansible manually
ansible-playbook -i inventory.yml setup.yml
```

---

## Configuration Without Python

### Using the Bash Config Tool

All configuration management available in pure Bash:

```bash
# List enabled roles
./cli/config.sh list

# Get a value
./cli/config.sh get global.logging.level

# Set a value
./cli/config.sh set global.logging.level debug

# Validate configuration
./cli/config.sh validate

# Export configuration
./cli/config.sh export yaml
```

### Manual Configuration Editing

Edit the configuration file directly:

```bash
# Edit config
nano ~/.devkit/config.yaml

# Validate manually
grep "^global:" ~/.devkit/config.yaml
```

### Configuration File Location

```
~/.devkit/config.yaml
```

**Basic structure:**

```yaml
global:
  setup_environment: development
  enabled_roles:
    - core
    - shell
    - editors
  logging:
    level: info
```

---

## Running Setup Without Python CLI

### Direct Ansible Execution

All Python tools are optional. You can run setup with pure Ansible:

```bash
# Full setup
ansible-playbook -i inventory.yml setup.yml

# Specific roles only
ansible-playbook -i inventory.yml setup.yml --tags "core,shell"

# Dry run (check what will happen)
ansible-playbook -i inventory.yml setup.yml --check

# Verbose output
ansible-playbook -i inventory.yml setup.yml -vvv
```

### Requirements

- bash
- Ansible (installed by bootstrap script)
- Homebrew (installed by bootstrap script on macOS)

---

## Workflow: No Python Edition

### Step 1: Bootstrap System

```bash
curl -fsSL https://raw.githubusercontent.com/user/devkit/main/bootstrap.sh | bash --skip-python
```

**Installs:**
- Homebrew
- Ansible
- Essential tools

**Does NOT install:**
- Python 3
- Python tools (config engine, setup wizard, test suite)

### Step 2: Configure (Optional)

```bash
# Review configuration
cat ~/.devkit/config.yaml

# Edit if needed
nano ~/.devkit/config.yaml

# Validate with Bash tool
./cli/config.sh validate
```

### Step 3: Run Ansible

```bash
# Run the setup
ansible-playbook -i inventory.yml setup.yml
```

### Step 4: Verify

```bash
# Check logs
tail -f ~/.devkit/logs/setup.log

# Verify installed tools
which git
which brew
ansible --version
```

---

## Comparison: With vs Without Python

### With Python (Default)

| Feature | Available |
|---------|-----------|
| Bootstrap script | ✅ |
| Configuration management | ✅ (Python + Bash) |
| Interactive setup wizard | ✅ |
| Ansible setup | ✅ |
| Plugin system | ✅ |
| Test suite | ✅ |
| Bash config tool | ✅ |

**Pros:** Full functionality, interactive setup, plugin support
**Cons:** Additional Python dependency

### Without Python

| Feature | Available |
|---------|-----------|
| Bootstrap script | ✅ |
| Configuration management | ✅ (Bash only) |
| Interactive setup wizard | ❌ (Use --skip-python) |
| Ansible setup | ✅ |
| Plugin system | ❌ |
| Test suite | ❌ |
| Bash config tool | ✅ |

**Pros:** No Python dependency, lightweight, pure Bash
**Cons:** Limited to Ansible/Bash tools

---

## Troubleshooting

### Bootstrap Script Issues

```bash
# Run with verbose output
bash -x ./bootstrap.sh

# Check individual steps
./bootstrap.sh --verify-only

# Skip problematic steps
./bootstrap.sh --skip-python --skip-ansible
```

### Homebrew Not Installing

```bash
# Manual installation
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation
brew --version
```

### Ansible Not Found

```bash
# Install manually
brew install ansible

# Verify
ansible-playbook --version
```

### Configuration Errors

```bash
# Validate configuration
./cli/config.sh validate

# Check file manually
cat ~/.devkit/config.yaml

# Check specific sections
grep "enabled_roles:" ~/.devkit/config.yaml
```

### Ansible Playbook Issues

```bash
# Dry run to see what will happen
ansible-playbook setup.yml --check

# Run with verbose output
ansible-playbook setup.yml -vvv

# Run specific role only
ansible-playbook setup.yml --tags core

# Show available variables
ansible-playbook setup.yml -e ansible_verbosity=3
```

---

## Advanced: Custom Ansible Execution

### Run Specific Roles Only

```bash
# Core and shell only (fast)
ansible-playbook setup.yml --tags "core,shell"

# Everything except security (skip asking for sudo)
ansible-playbook setup.yml --skip-tags "security"
```

### Run with Environment Variables

```bash
# Set variables
export ANSIBLE_VERBOSITY=3
export HOMEBREW_NO_AUTO_UPDATE=1

# Run setup
ansible-playbook setup.yml
```

### Check Mode (Dry Run)

```bash
# See what will be changed without making changes
ansible-playbook setup.yml --check

# More verbose check
ansible-playbook setup.yml --check -vv
```

---

## When You Eventually Need Python

If you later want Python tools (wizard, plugins, tests):

```bash
# Install Python
./bootstrap.sh --python-only

# Now you can use Python tools
python3 cli/config_engine.py --validate
python3 cli/setup_wizard.py
python3 tests/test_suite.py
```

---

## Migration from No-Python to Full Setup

If you started without Python and want to upgrade:

```bash
# Step 1: Install Python
brew install python3

# Step 2: Install Python dependencies
pip3 install pyyaml

# Step 3: Run full setup
python3 cli/setup_wizard.py
```

---

## System Requirements (No Python)

### Minimum

- bash 4.0+
- curl
- Internet connection

### Recommended

- bash 4.3+
- curl with SSL support
- git (optional, for cloning)
- 10 GB free disk space

### Supported Systems

- macOS 13.0+ (Ventura, Sonoma, Sequoia)
- Linux (Ubuntu 20.04+, Debian 11+)
- Both Intel and Apple Silicon

---

## Quick Reference

### Bootstrap Script

```bash
./bootstrap.sh --help              # Show options
./bootstrap.sh                     # Full setup with Python
./bootstrap.sh --skip-python       # Setup without Python
./bootstrap.sh --interactive       # Interactive questions
./bootstrap.sh --verify-only       # Check prerequisites
```

### Bash Config Tool

```bash
./cli/config.sh list               # List roles
./cli/config.sh validate           # Validate config
./cli/config.sh get <key>          # Get value
./cli/config.sh set <key> <val>    # Set value
./cli/config.sh export yaml        # Export config
```

### Ansible Direct

```bash
ansible-playbook setup.yml         # Full setup
ansible-playbook setup.yml --check # Dry run
ansible-playbook setup.yml --tags core,shell  # Specific roles
```

---

## Logs and Debugging

### Setup Logs

```bash
# Real-time log
tail -f ~/.devkit/logs/setup.log

# View full log
cat ~/.devkit/logs/setup.log

# Search log for errors
grep -i "error\|failed" ~/.devkit/logs/setup.log
```

### Bootstrap Logs

```bash
# Run with verbose output
bash -x ./bootstrap.sh 2>&1 | tee setup.log

# Check for errors
grep -i error setup.log
```

---

## FAQ

**Q: Can I use mac-setup without any Python?**
A: Yes! Use `./bootstrap.sh --skip-python` and interact with Ansible directly.

**Q: What tools won't work without Python?**
A: Setup wizard, plugin system, and test suite. Everything else works.

**Q: How do I configure without the wizard?**
A: Edit `~/.devkit/config.yaml` directly or use `./cli/config.sh set`.

**Q: Can I add Python later?**
A: Yes, just run `brew install python3` and then `pip3 install pyyaml`.

**Q: What if bootstrap fails?**
A: Run `./bootstrap.sh --verify-only` to check what's missing, then install manually.

**Q: Do I need git?**
A: Only if cloning from GitHub. You can download the zip file instead.

**Q: Is it secure without Python?**
A: Yes! All Bash and Ansible are secure. Python tools add convenience but not security.

---

## Support

### Get Help

```bash
# Bootstrap help
./bootstrap.sh --help

# Config tool help
./cli/config.sh help

# Ansible help
ansible-playbook --help
```

### Manual Installation

If automated bootstrap doesn't work:

```bash
# 1. Install Homebrew manually
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Ansible
brew install ansible

# 3. Clone repo
git clone https://github.com/user/devkit.git
cd devkit

# 4. Run setup
ansible-playbook setup.yml
```

---

**Version**: 2.0.0
**Updated**: October 30, 2025
**Status**: Fully Tested

For more information, see [MODULAR_README.md](MODULAR_README.md) and [MODULAR_ARCHITECTURE.md](docs/MODULAR_ARCHITECTURE.md)
