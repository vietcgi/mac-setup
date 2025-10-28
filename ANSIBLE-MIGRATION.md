# Ansible Modernization Guide

**Migrating from complex multi-role Ansible to simplified modern setup.**

## What Changed?

### Before (Old Setup)

```yaml
mac-setup/
├── bootstrap.sh                 # Complex bootstrap
├── main.yml                     # Main playbook
├── defaults/main.yml            # 200+ lines of config
├── config.yml                   # User overrides
├── requirements.yml             # 8 external roles
├── tasks/                       # Multiple task files
│   ├── extra-packages.yml
│   ├── sudoers.yml
│   ├── exportrc.yml
│   ├── gdircolors.yml
│   └── osx.yml
├── inventory                    # Inventory file
├── ansible.cfg                  # Ansible config
└── .ansible/                    # Downloaded roles (bloat)
```

**Problems:**

- [NO] 10+ files to maintain
- [NO] 8 external role dependencies
- [NO] Complex YAML hierarchy
- [NO] Slow (downloads roles every time)
- [NO] Hard to customize

### After (New Setup)

```yaml
mac-setup/
├── setup.yml                    # Single clean playbook (~250 lines)
├── bootstrap-ansible.sh         # Simple bootstrap
├── Brewfile                     # All packages (Homebrew's native format)
├── .mise.toml                   # Tool versions (mise's native format)
└── dotfiles/                    # Managed by chezmoi
    └── .zshrc
```

**Benefits:**

- [OK] 3 main files (setup.yml, Brewfile, .mise.toml)
- [OK] Zero external roles
- [OK] Simple, readable YAML
- [OK] Fast (no role downloads)
- [OK] Easy to customize

## What Moved Where?

| Old Location | New Location | Tool |
|--------------|--------------|------|
| `defaults/main.yml:homebrew_installed_packages` | `Brewfile` | Homebrew |
| `defaults/main.yml:homebrew_cask_apps` | `Brewfile` (casks) | Homebrew |
| `requirements.yml` (nvm/rbenv roles) | `.mise.toml` | mise |
| `tasks/exportrc.yml` | `dotfiles/.zshrc` | chezmoi |
| `defaults/main.yml:vim_plugins` | `setup.yml` (vim-plug) | vim-plug |
| `defaults/main.yml:visual_studio_code_extensions` | `setup.yml` (vars) | Ansible  |
| `requirements.yml:geerlingguy.mac.homebrew` | `setup.yml` (bundle) | Built-in |
| `requirements.yml:ansible-vim` | `setup.yml` (get_url vim-plug) | Built-in |
| `requirements.yml:ansible-tmux` | Not migrated yet | Manual |
| `requirements.yml:ansible_role_antigen` | `setup.yml` (Oh My Zsh) | Built-in |
| `requirements.yml:geerlingguy.mac.dock` | `setup.yml` (dockutil) | Built-in |

## Migration Steps

### Step 1: Backup Current Setup (Optional)

```bash
# Backup everything (just in case)
cp -r ~/mac-setup ~/mac-setup-backup
```

**Note**: The old Ansible files have been removed in v3.0.0. If you're
still using the old setup, backup your repo before upgrading.

### Step 2: Review What You've Customized

**If you had custom configuration**, note your changes:

```yaml

If it's mostly empty (just comments), you're using defaults → Easy migration!

If you have customizations, note them down. We'll add them to the new setup.
```

### Step 3: Run the New Setup

```bash
# Make bootstrap executable (if not already)
chmod +x bootstrap-ansible.sh

# Run it!
./bootstrap-ansible.sh
```

This will:

1. Install Homebrew (if needed)
2. Install Ansible (if needed)
3. Run the new simplified playbook
4. Install all packages, configure shell, vim, etc.

### Step 4: Verify Everything Works

```bash
# Check installed tools
brew list
mise list
code --list-extensions

# Check shell
echo $SHELL
ls -la ~/.oh-my-zsh

# Check dotfiles
chezmoi managed
```

### Step 5: Clean Up Old Files (Optional)

```bash
# After confirming new setup works
rm -rf .ansible/  # Old downloaded roles
```

## Customization Guide

### Adding/Removing Packages

**Old way:**

```yaml
# defaults/main.yml
homebrew_installed_packages:
  - git
  - kubectl
  - new-package  # ← Add here
```

**New way:**

```ruby
# Brewfile
brew "git"
brew "kubectl"
brew "new-package"  # ← Add here
```

Then run:

```bash
brew bundle install
# or
ansible-playbook setup.yml
```

### Changing Tool Versions

**Old way:**

```bash
# Install nvm, then manually:
nvm install 20
```

**New way:**

```toml
# .mise.toml
[tools]
node = "20"     # ← Change version here
go = "latest"
python = "3.12"
```

Then run:

```bash
mise install
# or
ansible-playbook setup.yml
```

### Adding VS Code Extensions

**Old way:**

```yaml
# defaults/main.yml
visual_studio_code_extensions:
  - ms-python.python
  - new-extension  # ← Add here
```

**New way:**

```yaml
# setup.yml
vars:
  vscode_extensions:
    - ms-python.python
    - new-extension  # ← Add here
```

Then run:

```bash
ansible-playbook setup.yml
```

### Customizing Shell Config

**Old way:**

```yaml
# defaults/main.yml
exportrc: |
  export PATH="..."
  alias ls="lsd"
```

**New way:**

```bash
# Edit dotfiles/.zshrc directly
# Then manage with chezmoi

chezmoi edit ~/.zshrc
chezmoi apply
```

### macOS Dock Configuration

**Old way:**

```yaml
# defaults/main.yml
dockitems_persist:
  - name: Messages
    path: "/Applications/Messages.app/"
```

**New way:**

```yaml
# setup.yml - edit the dock configuration task
- name: Configure Dock
  shell: |
    dockutil --add '/Applications/Messages.app' --no-restart
```

Then run:

```bash
ansible-playbook setup.yml --tags macos
```

## Running Updates

### Old Way

```bash
./bootstrap.sh
# → Downloads roles from Galaxy
# → Runs playbook
# → ~10 minutes
```

### New Way

```bash
# Option 1: Just update packages
brew bundle install

# Option 2: Re-run full playbook
ansible-playbook setup.yml

# Option 3: Run specific parts
ansible-playbook setup.yml --tags shell
ansible-playbook setup.yml --tags vim
```

**Time:** ~1-2 minutes (no role downloads!)

## Idempotency

Both old and new setups are idempotent.
You can run them multiple times safely.

**Test it:**

```bash
# Run twice in a row
ansible-playbook setup.yml
ansible-playbook setup.yml

# Second run should show:
# - "ok" for most tasks (no changes)
# - "changed" only if something actually changed
```

## What If Something Goes Wrong?

### Restore Old Setup

```bash
# If you kept the backup
cp -r ~/mac-setup-backup/* ~/mac-setup/

# Run old bootstrap
./bootstrap.sh
```

### Hybrid Approach

You can run **both** setups side-by-side:

```bash
# Old setup (archived)
cd ~/mac-setup-backup/
ansible-playbook main.yml

# New setup
cd ..
ansible-playbook setup.yml
```

They won't conflict - they install the same things in the same places.

## Feature Comparison

| Feature | Old Setup | New Setup |
|---------|-----------|-----------|
| **Files to maintain** | 10+ | 3 |
| **External dependencies** | 8 roles | 0 roles |
| **Homebrew packages** | [OK] | [OK] |
| **Homebrew casks** | [OK] | [OK] |
| **Tool versions (node/go/python)** | Manual (nvm/rbenv) | [OK] mise |
| **Oh My Zsh** | [OK] via role | [OK] built-in |
| **Powerlevel10k** | [OK] via role |. [OK] built-in |
| **Vim plugins** | [OK] via role | [OK] vim-plug |
| **VS Code extensions** | [OK] | [OK] |
| **Dotfiles management** | Manual sync | [OK] chezmoi |
| **Dock configuration** | [OK] via role | [OK] dockutil |
| **macOS defaults** | [OK] via role | [OK] osx_defaults |
| **Cross-platform (Linux)** | [NO] macOS only | [OK] Mac + Linux |
| **Speed** | ~10 min | ~2 min |
| **Idempotent** | [OK] | [OK] |

## Not Migrated Yet

These features from your old setup aren't in the new playbook yet (but easy to add):

### Tmux Configuration

**Old:** `requirements.yml` included `ansible-tmux` role

**To add to new setup:**

```yaml
# Add to setup.yml
- name: Install tmux plugin manager
  git:
    repo: https://github.com/tmux-plugins/tpm
    dest: "{{ home }}/.tmux/plugins/tpm"

- name: Copy tmux config
  copy:
    src: dotfiles/.tmux.conf
    dest: "{{ home }}/.tmux.conf"
```

### Sudoers Configuration

**Old:** `tasks/sudoers.yml`

**To add to new setup:**

```yaml
# Add to setup.yml
- name: Configure passwordless sudo
  become: true
  lineinfile:
    path: /etc/sudoers.d/{{ user }}
    line: "{{ user }} ALL=(ALL) NOPASSWD: ALL"
    create: true
    mode: '0440'
    validate: 'visudo -cf %s'
  when: is_macos  # Or configure for Linux too
```

### Mac App Store Apps

**Old:** `geerlingguy.mac.mas` role

**To add to new setup:**

```bash
# Add mas to Brewfile
brew "mas"

# Then in setup.yml:
- name: Install Mac App Store apps
  shell: mas install {{ item }}
  loop:
    - 497799835  # Xcode
    # Add more app IDs
  when: is_macos
```

## Getting Help

### New Playbook Issues

```bash
# Run with verbose output
ansible-playbook setup.yml -vvv

# Check syntax
ansible-playbook setup.yml --syntax-check

# Dry run (check mode)
ansible-playbook setup.yml --check
```

### Brewfile Issues

```bash
# Check Brewfile syntax
brew bundle check

# Install specific package
brew install <package>

# List what would be installed
brew bundle list
```

### mise Issues

```bash
# Check what's installed
mise list

# Install specific tool
mise use node@20

# Debug
mise doctor
```

## FAQ

### Q: Can I keep my old setup and run both?

**A:** Yes! They won't conflict. But pick one to maintain going forward.

### Q: Will this work on Linux?

**A:** Yes! The new setup is cross-platform (macOS + Linux). The old one was macOS-only.

### Q: What if I have custom roles?

**A:** Review them and either:

1. Convert to tasks in `setup.yml`
2. Keep as separate role and import it
3. Write equivalent shell scripts

### Q: Is it faster?

**A:** Yes! ~2 minutes vs ~10 minutes (no role downloads)

### Q: Can I go back?

**A:** Yes, just restore from backup and run old `bootstrap.sh`

### Q: Do I need to uninstall anything?

**A:** No! Both setups install to the same locations. Just stop using the old playbook.

## Next Steps

1. [OK] Run `./bootstrap-ansible.sh`
2. [OK] Verify everything works
3. [OK] Customize `Brewfile` and `.mise.toml` as needed
4. [OK] Set up dotfiles with chezmoi
5. [OK] Clean up old files if needed
6. Enjoy your modern, simplified setup!

---

**Questions?** Check the main README.md or open an issue.
