# Quick Start - Modern Ansible Setup

**Get your Mac or Linux desktop configured in ~2 minutes.**

## TL;DR

```bash
# Clone or navigate to this repo
cd ~/devkit

# Run bootstrap
./bootstrap.sh

# Done! [OK]
```

## What Gets Installed?

### CLI Tools (from Brewfile)

- **Development:** git, node, go, python, php
- **Kubernetes:** kubectl, k9s, helm, eksctl, kubectx
- **AWS:** awscli, aws-iam-authenticator, aws-sso-util
- **Utilities:** bat, lsd, fzf, ripgrep, htop, jq, tree
- **GNU tools:** coreutils, grep, sed, tar, etc.

### Desktop Apps (macOS only - from Brewfile)

- Docker Desktop
- Google Chrome
- Firefox
- iTerm2
- Visual Studio Code
- Slack
- Sequel Ace
- And more...

### Development Tools (from .mise.toml)

- Node.js LTS
- Go latest
- Python latest

### Shell Setup

- Zsh
- Oh My Zsh
- Powerlevel10k theme
- Syntax highlighting
- Auto-suggestions
- Completions

### Editor Setup

- Vim with vim-plug
- VS Code with 25+ extensions

### Dotfiles

- Managed by chezmoi
- Initial .zshrc provided

## Detailed Setup

### Prerequisites

- **macOS:** 10.15+ (Catalina or newer)
- **Linux:** Ubuntu 20.04+, Debian 11+, Fedora 35+, or Arch
- **Internet connection**
- **~5GB disk space**

### Step 1: Get the Code

```bash
# If you don't have this repo yet
git clone <your-repo-url> ~/mac-setup
cd ~/devkit

# If you already have it
cd ~/devkit
git pull
```

### Step 2: Run Bootstrap

```bash
chmod +x bootstrap-ansible.sh
./bootstrap-ansible.sh
```

**What it does:**

1. Installs Homebrew (if not present)
2. Installs Ansible (via Homebrew)
3. Runs the Ansible playbook (`setup.yml`)

**Time:** ~2-5 minutes (depending on what's already installed)

### Step 3: Restart Terminal

```bash
# Close and reopen your terminal
# Or source your new config
source ~/.zshrc
```

### Step 4: Post-Setup (Optional)

```bash
# Configure Powerlevel10k theme
p10k configure

# Install Vim plugins
vim +PlugInstall +qall

# Check what's installed
brew list
mise list
code --list-extensions
```

## What Happens on Re-Run?

The setup is **idempotent** - safe to run multiple times:

```bash
# Run again
./bootstrap-ansible.sh

# Output will show:
# [OK] Already installed items (skipped)
#  New items (installed)
#  Changed items (updated)
```

**No harm in running it again!**

## Customization

### Add/Remove Packages

Edit `Brewfile`:

```ruby
# Add a package
brew "ripgrep"

# Add a desktop app (macOS)
cask "spotify"
```

Then run:

```bash
brew bundle install
# or
ansible-playbook setup.yml
```

### Change Tool Versions

Edit `.mise.toml`:

```toml
[tools]
node = "20"      # ← Change version
go = "1.22"      # ← Change version
python = "3.12"  # ← Change version
```

Then run:

```bash
mise install
# or
ansible-playbook setup.yml
```

### Add VS Code Extensions

Edit `setup.yml`:

```yaml
vscode_extensions:
  - ms-python.python
  - your-extension-here  # ← Add extension
```

Then run:

```bash
ansible-playbook setup.yml
```

### Modify Shell Config

```bash
# Edit your .zshrc
vim ~/.zshrc

# Or use chezmoi
chezmoi edit ~/.zshrc
chezmoi apply
```

## Common Commands

### Update Everything

```bash
# Update packages
brew update && brew upgrade

# Update tool versions
mise upgrade

# Or re-run full setup
ansible-playbook setup.yml
```

### Check Status

```bash
# What's installed
brew list
mise list
code --list-extensions

# Homebrew info
brew info

# mise info
mise doctor
```

### Dotfiles Management

```bash
# Edit dotfiles
chezmoi edit ~/.zshrc

# See what would change
chezmoi diff

# Apply changes
chezmoi apply

# See what's managed
chezmoi managed
```

## Platform Differences

### macOS

- [OK] All CLI tools install
- [OK] All desktop apps (casks) install
- [OK] Dock configuration runs
- [OK] macOS defaults apply

### Linux

- [OK] All CLI tools install
- [SKIP] Desktop apps (casks) skipped - install manually via your package manager
- [SKIP] Dock configuration skipped (not applicable)
- [SKIP] macOS defaults skipped

**Install desktop apps on Linux:**

```bash
# Ubuntu/Debian
sudo apt install code docker.io slack

# Fedora
sudo dnf install code docker slack

# Arch
sudo pacman -S code docker slack
```

## Troubleshooting

### "brew: command not found"

```bash
# Add Homebrew to PATH
# macOS:
eval "$(/opt/homebrew/bin/brew shellenv)"

# Linux:
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

### "ansible-playbook: command not found"

```bash
# Install Ansible via Homebrew
brew install ansible
```

### Ansible playbook fails

```bash
# Run with verbose output
ansible-playbook setup.yml -vvv

# Check syntax
ansible-playbook setup.yml --syntax-check
```

### Package install fails

```bash
# Update Homebrew
brew update

# Try installing package directly
brew install <package-name>

# Check Brewfile syntax
brew bundle check
```

## Files Overview

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `setup.yml` | Main Ansible playbook | Rarely (add new tasks) |
| `Brewfile` | Package definitions | Often (add/remove apps) |
| `.mise.toml` | Tool version config | Sometimes (update versions) |
| `dotfiles/.zshrc` | Shell configuration | Often (customize shell) |
| `bootstrap-ansible.sh` | Bootstrap script | Never (unless debugging) |

## Next Steps

1. [OK] Run `./bootstrap-ansible.sh`
2. [OK] Restart your terminal
3. [OK] Run `p10k configure` for theme setup
4. [OK] Customize `Brewfile` and `.mise.toml`
5. [OK] Set up dotfiles with `chezmoi`
6. Enjoy your modern setup!

## Getting Help

- **Ansible issues:** Run with `-vvv` flag for debugging
- **Homebrew issues:** `brew doctor`
- **mise issues:** `mise doctor`
- **chezmoi issues:** `chezmoi doctor`

## Comparison to Old Setup

| Aspect | Old Setup | New Setup |
|--------|-----------|-----------|
| **Files** | 10+ | 3 main files |
| **External roles** | 8 roles | 0 roles |
| **Speed** | ~10 min | ~2 min |
| **Complexity** | High | Low |
| **Platforms** | macOS only | macOS + Linux |
| **Maintenance** | Hard | Easy |

---

**That's it! You're all set.**

For more details, see:

- [ANSIBLE-MIGRATION.md](ANSIBLE-MIGRATION.md) - Migrating from old setup
- [README.md](README.md) - Full documentation
