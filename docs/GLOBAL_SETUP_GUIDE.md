# Global Setup Guide - Enforcement Across All Repositories

## Question: Will This Work With All Repos?

**Answer:** It depends on how you set it up:

### Option 1: Current (Per-Repository) Setup
```bash
git config core.hooksPath=/Users/kevin/devkit/.git-templates/hooks
```
**Scope:** Only this repository (`/Users/kevin/devkit`)
**Issue:** Other repos won't have the hooks
**Need to:** Configure each repo separately

### Option 2: Global Setup (Recommended) ✓
```bash
git config --global init.templateDir ~/.git-templates
git config --global core.hooksPath ~/.git-templates/hooks
```
**Scope:** ALL repositories on this machine
**Benefit:** Works automatically for every repo
**No:** Need to configure each repo individually

---

## How It Works: Git Template Directory

When you run `git init` in a new repository:

```
git init
  ↓
Git checks: Does ~/.git-templates exist?
  ↓
YES: Copy all files from ~/.git-templates to new repo's .git/
     (including hooks in .git-templates/hooks)
  ↓
Result: Hooks are automatically available in new repo
```

**Key Point:** Git automatically copies templates when initializing repos.

---

## Global Setup Instructions

### Step 1: Create Global Templates Directory

```bash
mkdir -p ~/.git-templates/hooks
mkdir -p ~/.devkit/git
```

### Step 2: Copy Hooks to Global Location

```bash
# Copy from devkit repo to global location
cp /Users/kevin/devkit/.git-templates/hooks/pre-commit ~/.git-templates/hooks/
cp /Users/kevin/devkit/.git-templates/hooks/post-commit ~/.git-templates/hooks/
cp /Users/kevin/devkit/.git-templates/hooks/commit-msg ~/.git-templates/hooks/
cp /Users/kevin/devkit/.git-templates/hooks/prepare-commit-msg ~/.git-templates/hooks/

# Make them executable
chmod +x ~/.git-templates/hooks/*
```

### Step 3: Configure Git Globally

```bash
# Set global template directory
git config --global init.templateDir ~/.git-templates

# Set global hooks path
git config --global core.hooksPath ~/.git-templates/hooks

# Verify
git config --global --list | grep -E "init.templateDir|core.hooksPath"
```

**Output:**
```
init.templateDir=/Users/kevin/.git-templates
core.hooksPath=/Users/kevin/.git-templates/hooks
```

### Step 4: Test With Existing Repositories

For existing repositories that were cloned before the global setup:

```bash
# Option A: Manually set hooks path (one-time per repo)
cd /path/to/repo
git config core.hooksPath ~/.git-templates/hooks

# Option B: Use Ansible role to automate (recommended)
ansible-playbook ansible/site.yml -t git

# Option C: Create small script to apply to all repos
# See "Batch Setup" section below
```

---

## Verification

### Check Current Configuration

```bash
# Check global settings
git config --global core.hooksPath
# Output: /Users/kevin/.git-templates/hooks

# Check per-repo settings (if overridden)
git config --local core.hooksPath
# Output: (empty, using global)

# View all git config
git config --list | grep hooksPath
```

### Verify Hooks Are Accessible

```bash
# List global hooks
ls -la ~/.git-templates/hooks/

# Check hook is executable
test -x ~/.git-templates/hooks/pre-commit && echo "✓ Executable" || echo "✗ Not executable"
```

### Test In a Repository

```bash
cd /path/to/any/repo
git config --list | grep hooksPath  # Should show global path
ls -la .git/hooks/pre-commit        # Should exist
```

---

## How It Works Across Repositories

### New Repository (after global setup)

```bash
cd /tmp
mkdir new-project
cd new-project
git init
  ↓
Git automatically copies ~/.git-templates to .git/
  ↓
Result: .git/hooks/pre-commit exists automatically
         No configuration needed!
```

### Existing Repository (before global setup)

**Without global hooks:**
```bash
cd /path/to/existing/repo
ls .git/hooks/pre-commit  # Not there
```

**After setting global hooks:**
```bash
git config core.hooksPath ~/.git-templates/hooks
  ↓
.git/hooks/pre-commit     # Still not copied, but hooks path is set
                          # Git looks in ~/.git-templates/hooks instead
```

---

## Batch Setup for Multiple Existing Repositories

If you have many existing repositories:

### Script 1: Apply to All Repos in a Directory

```bash
#!/bin/bash
# apply-hooks-to-repos.sh

REPOS_DIR="$HOME/projects"
HOOKS_PATH="$HOME/.git-templates/hooks"

echo "Applying global hooks to all repos in $REPOS_DIR"

for repo_dir in $REPOS_DIR/*/; do
    if [ -d "$repo_dir/.git" ]; then
        echo "Setting hooks for: $repo_dir"
        cd "$repo_dir"
        git config core.hooksPath "$HOOKS_PATH"
        echo "  ✓ Done"
    fi
done
```

Usage:
```bash
chmod +x apply-hooks-to-repos.sh
./apply-hooks-to-repos.sh
```

### Script 2: Use find to Get All Repos

```bash
#!/bin/bash
# apply-hooks-all-repos.sh

echo "Finding all git repositories..."
find ~ -name ".git" -type d 2>/dev/null | while read git_dir; do
    repo_dir=$(dirname "$git_dir")
    echo "Setting hooks for: $repo_dir"
    git -C "$repo_dir" config core.hooksPath ~/.git-templates/hooks
done
```

---

## Automation with Ansible

The Ansible `git` role can automate this setup:

### Using the Git Role

```bash
# Deploy to machine
ansible-playbook -i inventory/localhost.yml site.yml -t git

# Specifies:
# - init.templateDir = ~/.git-templates
# - core.hooksPath = ~/.git-templates/hooks
# - Copies all hook templates
# - Makes hooks executable
```

### Configuration

**File:** `group_vars/all.yml`

```yaml
# Git global configuration
git_global_config: true
git_template_dir: "{{ home_dir }}/.git-templates"
git_hooks_path: "{{ home_dir }}/.git-templates/hooks"

# This applies to ALL repositories on the machine
```

---

## How Hooks Are Applied

### Scenario 1: New Repository

```
git init
  ↓
Git sees: init.templateDir = ~/.git-templates
  ↓
Git copies: ~/.git-templates/* → .git/
  ↓
Result: Hooks are in .git/hooks/
         Pre-commit hook runs on every commit
```

### Scenario 2: Existing Repository Without Hooks Path

```
git commit (pre-commit hook not found in .git/hooks/)
  ↓
Git checks: core.hooksPath setting
  ↓
Found: core.hooksPath = ~/.git-templates/hooks
  ↓
Git runs: ~/.git-templates/hooks/pre-commit
  ↓
Pre-commit validation happens (even though hook not copied)
```

### Scenario 3: Repository-Specific Override

```
git config core.hooksPath  # Set locally in repo
  ↓
Git uses: Local setting (ignores global)
  ↓
Can use different hooks for specific repo if needed
```

---

## Multiple Hook Versions

You can have different hooks for different purposes:

### Example: Multiple Environments

```
~/.git-templates/hooks/pre-commit          # Strict (production)
~/strict-hooks/pre-commit                  # Extra strict
~/dev-hooks/pre-commit                     # Less strict
```

**Configure per repository:**

```bash
# Production repo
cd ~/production-app
git config core.hooksPath ~/.git-templates/hooks

# Development repo
cd ~/experimental
git config core.hooksPath ~/dev-hooks
```

---

## Troubleshooting

### Hooks Not Running

**Problem:** Pre-commit hook not executing

**Solutions:**

```bash
# 1. Check configuration
git config core.hooksPath
git config init.templateDir

# 2. Verify hook exists and is executable
ls -la ~/.git-templates/hooks/pre-commit
chmod +x ~/.git-templates/hooks/pre-commit

# 3. Set explicitly if needed
git config --global core.hooksPath ~/.git-templates/hooks

# 4. Test manually
bash ~/.git-templates/hooks/pre-commit
```

### Hooks Exist But Not Running in New Repo

**Problem:** New repo initialized but hook not running

**Solution:** Git only copies templates on `git init`, not on clone:

```bash
# For cloned repos, set hooks path
cd /cloned/repo
git config core.hooksPath ~/.git-templates/hooks

# Or set globally and new repos will have it automatically
git config --global core.hooksPath ~/.git-templates/hooks
```

### Permission Issues

**Problem:** `Permission denied` when hook runs

**Solution:**

```bash
# Make all hooks executable
chmod +x ~/.git-templates/hooks/*

# Verify
ls -la ~/.git-templates/hooks/
# Should show: -rwxr-xr-x for each hook
```

---

## Current Status

### Already Configured Globally

✅ Global template directory created: `~/.git-templates`
✅ Global hooks path configured: `~/.git-templates/hooks`
✅ Hooks copied to global location:
   - pre-commit
   - post-commit
   - commit-msg
   - prepare-commit-msg
✅ All hooks executable

### Verification

```bash
$ git config --global --get core.hooksPath
/Users/kevin/.git-templates/hooks

$ ls -la ~/.git-templates/hooks/
-rwxr-xr-x  pre-commit
-rwxr-xr-x  post-commit
-rwxr-xr-x  commit-msg
-rwxr-xr-x  prepare-commit-msg
```

---

## What This Means

### For Existing Repositories

✓ Set hooks path once: `git config core.hooksPath ~/.git-templates/hooks`
✓ Works immediately: Next commit uses hooks
✓ Hooks run automatically: No per-repo setup needed

### For New Repositories

✓ After `git init`: Hooks automatically available
✓ After `git clone`: Set path once or use global config
✓ Global config applies: All future repos use hooks automatically

### For Team Distribution

✓ Commit this configuration to your dotfiles
✓ Teams clone dotfiles during setup
✓ All team members get same hooks
✓ Consistent quality standards across team

---

## Best Practice: Universal Application

### Option A: Global Config + Ansible Role

**Most reliable:**

```bash
# 1. Set global git config
git config --global core.hooksPath ~/.git-templates/hooks

# 2. Deploy via Ansible to set up all repos
ansible-playbook site.yml -t git

# 3. Verify in all repos
git config core.hooksPath  # All show global path
```

**Result:** Consistent hooks across machine and all repositories

### Option B: Git Hooks Directory Only (without config)

Not recommended - requires per-repo setup

### Option C: Include in Dotfiles

**Best for teams:**

```bash
# dotfiles/git/hooks/pre-commit
# dotfiles/git/hooks/post-commit
# dotfiles/git/config.global
[init]
    templateDir = ~/.git-templates
[core]
    hooksPath = ~/.git-templates/hooks
```

When team clones dotfiles, hooks automatically apply.

---

## Summary

| Question | Answer |
|----------|--------|
| **Will it work with all repos?** | Yes, if configured globally |
| **Need per-repo setup?** | No, global setup covers all |
| **New repos get hooks?** | Yes, automatically via `git init` |
| **Existing repos need config?** | Yes, one-time: `git config core.hooksPath ~/.git-templates/hooks` |
| **Can I override per-repo?** | Yes, local config takes precedence |
| **How to apply to many repos?** | Use batch script or Ansible role |
| **Current status?** | ✅ Global setup complete |

---

## Next Steps

1. ✅ Global configuration is complete
2. ✅ Hooks are in place at `~/.git-templates/hooks`
3. For existing repos, apply: `git config core.hooksPath ~/.git-templates/hooks`
4. For new repos: Hooks apply automatically
5. (Optional) Use Ansible role for automatic application

**Result:** Quality enforcement works across ALL repositories on this machine.
