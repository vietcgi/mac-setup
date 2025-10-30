# Git Configuration Role

Comprehensive Ansible role for managing git configuration, templates, hooks, and aliases across development machines.

## Features

### ✅ Configuration Management

- **Global gitconfig** - User info, core settings, performance tuning
- **Local gitconfig** - Machine-specific overrides, credentials, SSH configuration
- **Global gitattributes** - File handling rules (line endings, binary detection)
- **Global gitignore** - Common patterns across all repositories

### ✅ Git Hooks

- **Pre-commit** - Trailing whitespace, large file detection, syntax checks
- **Commit-msg** - Message format validation, conventional commits checking
- **Post-commit** - Logging, audit trail, custom hooks support
- **Prepare-commit-msg** - Auto-prefixing commit messages with branch names

### ✅ Aliases & Shortcuts

- 20+ built-in git aliases (s, st, co, br, etc.)
- Customizable per group/host
- Support for complex commands

### ✅ Advanced Features

- GPG signing support
- SSH signing support
- Git Large File Storage (LFS) configuration
- Worktree configuration
- Delta diff viewer support
- Credential helpers (OSXKeychain on macOS, cache on Linux)

### ✅ Reload Mechanisms

- Config changes trigger automatic reload
- Hooks are verified and made executable
- Audit logging of all configuration changes
- Change detection and reporting

## Variables

### Required Variables

```yaml
git_user_name: "Kevin Vu"              # Git user name
git_user_email: "vietcgi@gmail.com"    # Git user email
```

### Optional Variables

#### GPG Signing

```yaml
git_enable_gpg_signing: false          # Enable GPG signing
git_gpg_key_id: ""                     # GPG key ID
git_auto_sign_commits: false           # Auto-sign all commits
git_show_signature: false              # Show signature in logs
```

#### SSH Signing

```yaml
git_enable_ssh_signing: false          # Enable SSH signing
git_ssh_signing_key: ~/.ssh/id_ed25519 # SSH key for signing
```

#### Merge & Rebase

```yaml
git_pull_rebase: true                  # Rebase instead of merge on pull
git_rebase_auto_stash: true            # Auto stash before rebase
git_merge_conflict_style: "diff3"      # Conflict resolution style
```

#### Display & Formatting

```yaml
git_log_date_format: "iso"             # Date format in logs
git_core_pager: "less -F"              # Pager program
git_editor: "nvim"                     # Default editor
```

#### Custom Aliases

```yaml
git_aliases:
  s: "status"
  d: "diff"
  co: "checkout"
  loga: "log --all --graph --oneline"
  # ... add your own
```

#### Pre-commit Checks

```yaml
git_pre_commit_checks:
  trailing_whitespace: true   # Check for trailing whitespace
  large_files: true           # Check for files > 10MB
  syntax_check: false         # Validate Python syntax
```

#### Feature Flags

```yaml
git_setup_hooks: true                  # Deploy git hooks
git_setup_templates: true              # Use template directory
git_setup_global_gitignore: true       # Deploy gitignore
git_setup_attributes: true             # Deploy gitattributes
configure_git: true                    # Enable git configuration
```

## Usage

### Basic Setup

```yaml
- name: Configure Git
  hosts: all
  roles:
    - git
```

### With Custom Configuration

```yaml
- name: Configure Git
  hosts: development
  vars:
    git_user_name: "John Doe"
    git_user_email: "john@example.com"
    git_enable_gpg_signing: true
    git_gpg_key_id: "1234567890ABCDEF"
    git_aliases:
      s: "status --short"
      d: "diff --word-diff"
      co: "checkout"
  roles:
    - git
```

### Platform-Specific Configuration

```yaml
# group_vars/development.yml
git_user_email: "dev@company.com"
git_aliases_extra:
  prod: "checkout production"
  dev: "checkout develop"
```

## Directory Structure

```
~/.config/git/
├── ignore                    # Global gitignore file
└── (gitattributes handled via ~/.gitattributes)

~/.git-templates/
├── hooks/
│   ├── pre-commit           # Pre-commit hook
│   ├── commit-msg           # Commit message validation
│   ├── post-commit          # Post-commit hook
│   └── prepare-commit-msg   # Message preparation
└── scripts/                 # Custom hook scripts (optional)

~/.gitconfig                 # Main git configuration
~/.gitconfig.local          # Local machine overrides
~/.gitattributes            # File attributes

~/.devkit/git/
├── gitconfig.backup.*      # Backed up configurations
├── commits.log             # Commit audit trail
└── logs/
    ├── git.log             # Configuration changes
    └── commit-msg.log      # Message validation log
```

## Git Hooks

### Pre-Commit Hook

Runs before each commit. Can prevent commit if checks fail.

**Checks:**

- Trailing whitespace detection
- Large file detection (> 10MB)
- Python syntax validation (optional)
- Custom pre-commit scripts

**Configuration:**

```yaml
git_pre_commit_checks:
  trailing_whitespace: true
  large_files: true
  syntax_check: false
```

### Commit-Message Hook

Validates commit message format.

**Checks:**

- Message not empty
- First line ≤ 50 characters
- Second line is blank (if multi-line)
- Conventional commit format (optional)
- Imperative mood suggestion

**Configuration:**

```yaml
git_commit_msg_maxline: 50
git_commit_msg_check_scope: true
git_commit_msg_check_type: true
```

### Post-Commit Hook

Runs after successful commit. Logs commit information.

**Actions:**

- Logs commit hash, author, message
- Runs custom post-commit scripts
- Displays commit summary

### Prepare-Commit-Message Hook

Prepares message before user edits it.

**Features:**

- Auto-prefixes with branch ticket ID
- Skips main/master branches
- Doesn't override existing prefixes

## Configuration Reload

When configuration changes are made:

1. ✅ Files are validated for syntax
2. ✅ Handlers detect changes
3. ✅ Git config is reloaded (via handlers)
4. ✅ Hooks are verified and made executable
5. ✅ Changes are logged to audit trail

### Manual Reload

To manually reload git configuration:

```bash
# Option 1: Re-run the role
ansible-playbook setup.yml --tags git

# Option 2: Just reload git hooks
ansible-playbook setup.yml --tags git,hooks

# Option 3: Just reload config
ansible-playbook setup.yml --tags git,config
```

## Aliases Reference

| Alias | Command | Use Case |
|-------|---------|----------|
| `s` | `status` | Quick status check |
| `st` | `status` | Verbose status |
| `d` | `diff` | See changes |
| `dc` | `diff --cached` | See staged changes |
| `a` | `add` | Stage files |
| `co` | `checkout` | Switch branch |
| `br` | `branch` | List branches |
| `c` | `commit` | Make commit |
| `ca` | `commit --amend` | Fix last commit |
| `cm` | `commit -m` | Quick commit with message |
| `logs` | `log --oneline` | Recent commits |
| `loga` | `log --all --graph --oneline` | Full commit graph |
| `graph` | `log --all --decorate --oneline --graph` | Visual graph |
| `unstage` | `reset HEAD --` | Unstage files |
| `cleanup` | Delete merged branches | Clean old branches |
| `sync` | `fetch --all --prune` | Sync with remotes |

## Conditional Features

### GPG Signing

When enabled, requires GPG to be installed and key ID to be configured:

```bash
# List available keys
gpg --list-secret-keys --with-colons

# Sign a commit
git commit -S -m "Signed commit"

# Verify signatures
git log --show-signature
```

### SSH Signing

Alternative to GPG using SSH keys:

```bash
# Configure SSH signing key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519

# All commits will be signed with SSH key
git commit -m "SSH signed commit"
```

### Delta Diff Viewer

Enable for colored, side-by-side diffs:

```yaml
git_use_delta: true
```

Requires `delta` to be installed:

```bash
brew install git-delta  # macOS
apt install git-delta   # Linux
```

## Troubleshooting

### Hooks Not Running

- Check hook permissions: `ls -la ~/.git-templates/hooks/`
- Verify hook path: `git config core.hooksPath`
- Check hook syntax: `bash -n ~/.git-templates/hooks/pre-commit`

### Git Config Not Reloading

- Check file ownership: `ls -la ~/.gitconfig`
- Verify syntax: `git config --list`
- Check logs: `cat ~/.devkit/git/git.log`

### Permission Denied

- Make hooks executable: `chmod +x ~/.git-templates/hooks/*`
- Check directory permissions: `chmod 755 ~/.git-templates/hooks/`

### Commit Message Hook Failing

- Check message format against conventional commits
- See validation logs: `cat ~/.devkit/git/logs/commit-msg.log`

## Backup & Recovery

Configuration backups are automatically created:

```bash
# View backups
ls -la ~/.devkit/git/gitconfig.backup.*

# Restore backup
cp ~/.devkit/git/gitconfig.backup.TIMESTAMP ~/.gitconfig
```

## Security Considerations

1. **Sensitive Information**
   - Don't store credentials in `~/.gitconfig`
   - Use `~/.gitconfig.local` for machine-specific settings
   - Use credential helpers (osxkeychain, cache, etc.)

2. **Hook Security**
   - Hooks are user-editable (intentional)
   - Review hooks before accepting them
   - Set `core.hooksPath` to prevent bypass

3. **GPG/SSH Keys**
   - Store key passphrases in keychain
   - Use Ed25519 keys (more secure than RSA)
   - Never commit private keys

## Related Roles

- `core` - Base system setup (required)
- `shell` - Shell environment (can integrate with git aliases)
- `editors` - Editor setup (Git integration)

## Testing

To test the git role:

```bash
# Syntax check
ansible-playbook setup.yml --syntax-check --tags git

# Dry run
ansible-playbook setup.yml --check --tags git

# Verify configuration
git config --list --show-origin

# Test hooks
cd /tmp && git init test-repo && cd test-repo
# Try commits to test hooks
```

## References

- [Pro Git Book - Configuration](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Attributes](https://git-scm.com/docs/gitattributes)

## Changelog

### Version 1.0.0 (Initial)

- Complete git configuration management
- Git hooks (pre-commit, commit-msg, post-commit, prepare-commit-msg)
- Global gitignore and gitattributes
- 20+ git aliases
- GPG and SSH signing support
- Comprehensive reload mechanisms
- Audit logging and backups
