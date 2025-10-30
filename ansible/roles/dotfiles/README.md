# Dotfiles Role

Manages deployment of configuration files (dotfiles) from the repository to user home directories.

## Purpose

This role ensures that all configuration files tracked in the `dotfiles/` directory are properly deployed to the correct locations in the user's home directory. It provides:

- **Idempotent deployment**: Files are only updated if they've changed
- **Backup creation**: Optional automatic backups before overwriting
- **Validation**: Syntax checking for configuration files
- **Auditing**: Detailed reporting of what was deployed
- **Cross-platform**: Works on macOS and Linux

## Configuration Files Deployed

### Files (root directory)
- `.tmux.conf` → tmux terminal multiplexer configuration
- `.zshrc` → Zsh shell configuration
- `.direnvrc` → direnv configuration
- `.inputrc` → readline configuration

### Directories
- `nvim/` → Neovim editor configuration
- `ghostty/` → Ghostty terminal configuration

## Variables

### Default Variables

```yaml
# Create backups before overwriting files
dotfiles_create_backups: true

# Validate configurations before deployment
dotfiles_validate: true

# List of files to deploy (can be overridden)
dotfiles_files_to_sync:
  - src: ".tmux.conf"
    dest: "{{ ansible_user_dir }}/.tmux.conf"
    mode: "0644"
    validate: false
  # ... more files ...

# Directories to deploy
dotfiles_dirs_to_sync:
  - src: "nvim"
    dest: "{{ ansible_user_dir }}/.config/nvim"
    delete: false
  # ... more directories ...
```

## Usage

### In a Playbook

```yaml
---
- hosts: all
  roles:
    - role: dotfiles
      tags: [dotfiles]
```

### Run Only This Role

```bash
ansible-playbook setup.yml --tags dotfiles
```

### Customize Deployment

```yaml
---
- hosts: all
  vars:
    # Create backups
    dotfiles_create_backups: true

    # Only deploy specific files
    dotfiles_files_to_sync:
      - src: ".tmux.conf"
        dest: "{{ ansible_user_dir }}/.tmux.conf"
        mode: "0644"
  roles:
    - role: dotfiles
```

## How It Works

1. **Validates source directory** exists in the repository
2. **Creates parent directories** if they don't exist
3. **Deploys files** with idempotent copy module
4. **Deploys directories** with preserved permissions
5. **Validates** configurations (e.g., shell syntax)
6. **Reports** what was deployed and what changed
7. **Triggers handlers** if changes were made

## Idempotency

This role is fully idempotent:
- Files are only copied if they've changed
- Directories are synced with preserved permissions
- Running multiple times has no additional effect
- Safe to run as part of regular provisioning

## Backups

When `dotfiles_create_backups: true` (default):
- Existing files are backed up before overwriting
- Backup files have timestamp suffix: `.backup.TIMESTAMP`
- Stored in the same directory as the original

## Validation

The role validates deployed configurations:
- **`.zshrc`**: Checks zsh syntax with `zsh -n`
- Reports warnings but doesn't fail if validation fails

## Handlers

When dotfiles are changed, a handler is triggered:
- Notifies user that shell configuration may need reloading

## Dependencies

- **core**: This role depends on the core role for basic setup
- Requires Ansible 2.10+

## Troubleshooting

### Files not syncing?
Check that the `dotfiles/` directory exists in the playbook directory:
```bash
ls -la /path/to/playbook/dotfiles/
```

### Validation failing?
If `.zshrc` validation fails, check the syntax:
```bash
zsh -n ~/.zshrc
```

### Backups being created repeatedly?
If backups are being created on every run, the file permissions or content may have changed. Check with:
```bash
diff /path/to/repo/dotfiles/.tmux.conf ~/.tmux.conf
```

## Best Practices

1. **Keep dotfiles in version control** - Track changes to `.tmux.conf`, `.zshrc`, etc.
2. **Use meaningful commit messages** - Document why configuration changed
3. **Test changes locally first** - Validate configs work before committing
4. **Review diffs before syncing** - Know what's being deployed
5. **Use tags** - Run `ansible-playbook setup.yml --tags dotfiles` for quick updates

## Examples

### Deploy dotfiles only
```bash
ansible-playbook setup.yml --tags dotfiles
```

### Deploy with verbose output
```bash
ansible-playbook setup.yml --tags dotfiles -v
```

### Deploy to specific host
```bash
ansible-playbook setup.yml --tags dotfiles --limit production
```

### Dry-run without making changes
```bash
ansible-playbook setup.yml --tags dotfiles --check
```

## Notes

- This role assumes dotfiles are in `{{ playbook_dir }}/dotfiles/`
- File permissions are preserved from repository
- Directory syncing does NOT delete extra files by default
- Backups are created in the home directory

## Contributing

When adding new dotfiles:

1. Add file/directory to `dotfiles/` in repository
2. Update `defaults/main.yml` with entry
3. Test deployment with `--check` flag
4. Commit changes to git
5. Run playbook to deploy
