# Git Configuration Management Guide

Comprehensive guide to the git configuration system in devkit.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start](#quick-start)
3. [Configuration Hierarchy](#configuration-hierarchy)
4. [Git Hooks System](#git-hooks-system)
5. [Dynamic Reloading](#dynamic-reloading)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

## Architecture Overview

The git configuration system is built around these core concepts:

### **Three-Layer Configuration**

```
Layer 1: Global Config (~/.gitconfig)
├── User identity
├── Core settings
├── Performance tuning
└── Aliases

Layer 2: Local Config (~/.gitconfig.local)
├── Machine-specific overrides
├── Credentials & tokens
├── SSH/GPG keys
└── Sensitive info (git-ignored)

Layer 3: Repository Config (.git/config)
└── Per-repo specific settings
```

### **File Structure**

```
~/.gitconfig              ← Main configuration (version controlled via devkit)
~/.gitconfig.local        ← Local overrides (NOT version controlled)
~/.config/git/ignore      ← Global gitignore
~/.gitattributes          ← File type handling rules
~/.git-templates/         ← Templates for new repositories
  hooks/                    ← Global hooks
    pre-commit
    commit-msg
    post-commit
    prepare-commit-msg
~/.devkit/git/            ← Backups and logs
  gitconfig.backup.*
  logs/
    git.log
    commits.log
```

## Quick Start

### 1. Initial Setup

```bash
# Run the git role
ansible-playbook setup.yml --tags git

# Verify configuration
git config --list --show-origin | head -20
```

### 2. Customize User Info

Edit `~/.gitconfig.local`:

```ini
[user]
    name = Your Name
    email = your@email.com
```

### 3. Add Custom Aliases

Edit `~/.gitconfig.local`:

```ini
[alias]
    myalias = "commit -m"
```

### 4. Enable GPG Signing

In `group_vars/all.yml`:

```yaml
git_enable_gpg_signing: true
git_gpg_key_id: "1234567890ABCDEF"
git_auto_sign_commits: true
```

Then reload:

```bash
ansible-playbook setup.yml --tags git
```

## Configuration Hierarchy

Git reads configuration in this order (highest to lowest priority):

### **1. Local Repository Config** (`.git/config`)

```bash
git config --local key value
```

### **2. User Local Config** (`~/.gitconfig.local`)

```bash
# Manually edit or:
git config --file ~/.gitconfig.local key value
```

### **3. System Config** (`~/.gitconfig`)

```bash
# Deployed by Ansible
# Don't edit directly - modify via variables
```

### **4. System-wide Config** (`/etc/gitconfig`)

```bash
# Admin level - rarely used
```

**Example:** User email resolution

```yaml
Priority: .git/config > ~/.gitconfig.local > ~/.gitconfig > /etc/gitconfig

If .git/config has user.email, use that ✓
Else if ~/.gitconfig.local has it, use that ✓
Else if ~/.gitconfig has it, use that ✓
Else if /etc/gitconfig has it, use that ✓
Else git will error ✗
```

## Git Hooks System

### **Lifecycle of a Commit with Hooks**

```
git commit
    ↓
1. pre-commit hook runs
   ├─ Check for trailing whitespace
   ├─ Check for large files
   ├─ Run syntax checks
   └─ Can prevent commit if fails ✗
    ↓
2. If pre-commit passes, editor opens
   └─ User edits commit message
    ↓
3. prepare-commit-msg hook runs
   └─ Auto-prefix with branch name (optional)
    ↓
4. prepare-commit-msg hook finishes, user continues editing
    ↓
5. User writes/confirms message
    ↓
6. commit-msg hook runs
   ├─ Validate message format
   ├─ Check line length
   └─ Can prevent commit if fails ✗
    ↓
7. Commit is created
    ↓
8. post-commit hook runs
   ├─ Log commit to audit trail
   ├─ Can't prevent commit
   └─ Used for notifications/logging
```

### **Hook Configuration**

#### Pre-Commit Hook

**What it does:**

- Prevents committing code with trailing whitespace
- Prevents accidentally committing large files (>10MB)
- Optionally checks Python syntax

**Configuration:**

```yaml
# In defaults/main.yml or group_vars
git_pre_commit_checks:
  trailing_whitespace: true
  large_files: true
  syntax_check: false
```

**Custom checks:**

Create custom scripts in `~/.git-templates/scripts/`:

```bash
# ~/.git-templates/scripts/pre-commit-linting.sh
#!/bin/bash
# Your custom pre-commit logic
```

#### Commit-Msg Hook

**What it does:**

- Validates commit message format
- Checks conventional commit format
- Ensures first line is ≤ 50 characters
- Suggests imperative mood

**Configuration:**

```yaml
git_commit_msg_maxline: 50
git_commit_msg_check_scope: true
git_commit_msg_check_type: true
```

**Conventional Commit Format:**

```
type(scope): subject

body

footer
```

**Valid types:** feat, fix, docs, style, refactor, test, chore, perf, ci, build, revert

**Example:**

```
feat(auth): add two-factor authentication

Implement TOTP-based 2FA for user accounts.

Fixes #123
```

#### Prepare-Commit-Msg Hook

**What it does:**

- Auto-prefixes commit message with branch name
- Useful for ticket tracking (GH-123, JIRA-456)

**Example:**

```
Branch: feature/GH-123-fix-bug
Commit: Initial message

Auto-becomes:
GH-123: Initial message
```

#### Post-Commit Hook

**What it does:**

- Logs commit information to audit trail
- Sends notifications (optional)
- Can't prevent commits (non-blocking)

### **Testing Hooks**

```bash
# Create test repository
mkdir test-repo && cd test-repo
git init

# Test pre-commit hook
git add .
git commit -m "Test" 2>&1 | head -10

# Check hook logs
cat ~/.devkit/git/logs/commit-msg.log
```

## Dynamic Reloading

### **Why Reloading is Important**

When you change git configuration (especially hooks or templates), git needs to know about the changes. The reload mechanism:

1. ✅ Validates configuration syntax
2. ✅ Makes hooks executable
3. ✅ Updates git to use new config
4. ✅ Logs all changes

### **Manual Reload via Ansible**

```bash
# Full reload
ansible-playbook setup.yml --tags git

# Reload only hooks
ansible-playbook setup.yml --tags git,hooks

# Reload only config
ansible-playbook setup.yml --tags git,config
```

### **Quick Reload via Python Manager**

```bash
# Full reload (with backup)
python3 cli/git_config_manager.py

# Dry-run (validate without changes)
python3 cli/git_config_manager.py --dry-run

# Reload specific component
python3 cli/git_config_manager.py --component config
python3 cli/git_config_manager.py --component hooks
python3 cli/git_config_manager.py --component credentials
```

### **Automatic Reload Triggers**

When you change these files, reload is automatically triggered:

```
Changed File                     → Reload Action
──────────────────────────────────────────────────
~/.gitconfig                     → Reload git config
~/.gitconfig.local               → Reload git config
~/.git-templates/hooks/*         → Make executable, verify
~/.config/git/ignore             → Update core.excludesFile
~/.gitattributes                 → No reload needed
```

### **What Gets Reloaded**

```bash
1. Configuration Files
   ├─ Parse YAML/INI syntax
   ├─ Validate against schema
   └─ Detect changes

2. Hooks
   ├─ Make executable (chmod +x)
   ├─ Check syntax (bash -n)
   └─ Verify readability

3. Credentials
   ├─ Verify helper is installed
   ├─ Test authentication
   └─ Update credentials cache

4. Audit Trail
   ├─ Log all changes
   ├─ Timestamp each action
   └─ Record success/failure
```

## Common Tasks

### **Task 1: Change Git User Email**

```bash
# Option A: Edit local config
echo "[user]" >> ~/.gitconfig.local
echo "    email = new@example.com" >> ~/.gitconfig.local

# Reload
python3 cli/git_config_manager.py

# Option B: Use git command
git config --global user.email "new@example.com"

# Verify
git config --get user.email
```

### **Task 2: Add Custom Alias**

```bash
# Edit ~/.gitconfig.local
[alias]
    amend = "commit --amend --no-edit"
    unstage = "reset HEAD --"

# Reload
ansible-playbook setup.yml --tags git,config

# Use
git amend
git unstage
```

### **Task 3: Enable GPG Signing**

```bash
# 1. Create or import GPG key
gpg --list-secret-keys --with-colons

# 2. Get key ID (output will be like "1234567890ABCDEF")

# 3. Update group_vars/all.yml
git_enable_gpg_signing: true
git_gpg_key_id: "1234567890ABCDEF"
git_auto_sign_commits: true

# 4. Reload
ansible-playbook setup.yml --tags git

# 5. Test
git commit -m "Signed commit"
git log --show-signature -1
```

### **Task 4: Setup SSH Key Signing**

```bash
# 1. Create SSH key if needed
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

# 2. Add to group_vars/all.yml
git_enable_ssh_signing: true
git_ssh_signing_key: "{{ home_dir }}/.ssh/id_ed25519"

# 3. Reload
ansible-playbook setup.yml --tags git

# 4. Test
git commit -m "SSH signed commit"
git log --show-signature -1
```

### **Task 5: Customize Hook Behavior**

**Skip pre-commit checks for a commit:**

```bash
# Bypass pre-commit hook
git commit --no-verify -m "Skip checks"

# Bypass all hooks
git commit --no-verify --no-edit
```

**Create custom pre-commit check:**

```bash
# Create custom hook script
mkdir -p ~/.git-templates/scripts
cat > ~/.git-templates/scripts/pre-commit-mycheck.sh << 'EOF'
#!/bin/bash
# Custom pre-commit logic
if grep -r "TODO FIXME" --include="*.py"; then
    echo "Error: TODO FIXME markers not allowed"
    exit 1
fi
EOF

chmod +x ~/.git-templates/scripts/pre-commit-mycheck.sh

# Reload hooks
python3 cli/git_config_manager.py --component hooks
```

### **Task 6: Setup Credential Helper**

**macOS (using OSXKeychain):**

```bash
git config --global credential.helper osxkeychain

# First push will prompt for credentials
# Credentials are stored in Keychain
```

**Linux (using credentials cache):**

```bash
# Edit ~/.gitconfig
[credential]
    helper = cache --timeout=3600

# Or use pass/secretservice
git config --global credential.helper pass
```

### **Task 7: View Configuration Origins**

```bash
# See where each setting comes from
git config --list --show-origin

# See only global settings
git config --list --show-origin | grep "global:"

# See only local settings
git config --list --show-origin | grep "local:"

# See config from specific file
git config --file ~/.gitconfig --list
git config --file ~/.gitconfig.local --list
```

## Troubleshooting

### **Problem: Hooks Not Running**

**Symptoms:**

- Pre-commit checks not happening
- Commit messages not being validated

**Solutions:**

```bash
# 1. Verify hooks are executable
ls -la ~/.git-templates/hooks/
# Should show: -rwxr-xr-x (755 permissions)

# 2. Check core.hooksPath is set
git config --get core.hooksPath
# Should output: /Users/username/.git-templates/hooks

# 3. Verify hook syntax
bash -n ~/.git-templates/hooks/pre-commit
bash -n ~/.git-templates/hooks/commit-msg

# 4. Make executable and reload
chmod +x ~/.git-templates/hooks/*
python3 cli/git_config_manager.py --component hooks

# 5. Test hooks
cd /tmp && mkdir test-repo && cd test-repo && git init
# Try a commit to test
```

### **Problem: Config Not Reloading**

**Symptoms:**

- Changes to ~/.gitconfig don't take effect
- New aliases not available

**Solutions:**

```bash
# 1. Validate config syntax
git config --list
# If error appears, there's a syntax issue

# 2. Check file permissions
ls -la ~/.gitconfig ~/.gitconfig.local

# 3. Clear git cache
git gc

# 4. Reload manually
python3 cli/git_config_manager.py --dry-run

# 5. Re-run role
ansible-playbook setup.yml --tags git --check
```

### **Problem: Pre-commit Hook Failing**

**Symptoms:**

- Can't commit any code
- Hook error message appears

**Solutions:**

```bash
# 1. Check hook output
bash -x ~/.git-templates/hooks/pre-commit

# 2. See what's being committed
git diff --cached

# 3. Fix the issues (e.g., trailing whitespace)
# Look for trailing spaces with:
git diff --cached | grep -E '\s+$'

# 4. Or bypass if needed
git commit --no-verify -m "Message"

# 5. Check hook logs
tail -50 ~/.devkit/git/logs/git.log
```

### **Problem: Commit Message Hook Failing**

**Symptoms:**

- Commit messages rejected
- Error about message format

**Solutions:**

```bash
# 1. Check hook requirements
cat ~/.git-templates/hooks/commit-msg | head -20

# 2. Use conventional commit format
# Format: type(scope): message
# Types: feat, fix, docs, style, refactor, test, chore

# Example valid message:
# feat(auth): add two-factor authentication

# 3. Check message length
# First line should be ≤ 50 characters

# 4. Bypass if needed (use caution!)
git commit --no-verify -m "Your message"
```

### **Problem: Credential Helper Not Working**

**Symptoms:**

- Git keeps asking for password
- Can't access GitHub/GitLab

**Solutions:**

```bash
# 1. Check credential helper is set
git config --get credential.helper

# 2. For macOS - install keychain helper
git config --global credential.helper osxkeychain

# 3. For Linux - use cache helper
git config --global credential.helper cache

# 4. Test by pushing (will prompt once)
git push origin main

# 5. Verify credentials were stored
git config --show-origin --get credential.helper
```

### **Problem: GPG Signing Not Working**

**Symptoms:**

- Commit signing fails
- "Error: Cannot sign" message

**Solutions:**

```bash
# 1. Check GPG is installed
which gpg
gpg --version

# 2. List available keys
gpg --list-secret-keys --with-colons

# 3. Verify key ID in config
git config --get user.signingKey

# 4. Test GPG directly
echo "test" | gpg --sign

# 5. Add key to GPG agent
gpg --import-ownertrust

# 6. Set GPG TTY (for terminal input)
export GPG_TTY=$(tty)
```

## Best Practices

### ✅ Do

- Keep sensitive data in `~/.gitconfig.local` (git-ignored)
- Use conventional commit format for consistency
- Enable hook validation for large team projects
- Backup config before major changes
- Review hooks before accepting new ones
- Use GPG or SSH signing for important commits

### ❌ Don't

- Store credentials in `~/.gitconfig` (version controlled)
- Disable hooks globally (use `--no-verify` carefully)
- Share `~/.gitconfig.local` across machines
- Edit hooks without understanding them
- Skip commit message validation on main branch
- Use weak commit messages

## References

- [Git Configuration Documentation](https://git-scm.com/docs/git-config)
- [Git Hooks](https://git-scm.com/docs/githooks)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Pro Git Book](https://git-scm.com/book)
- [GitHub Security Best Practices](https://docs.github.com/en/authentication)
