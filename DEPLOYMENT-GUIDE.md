# Deployment Guide

## Quick Start

### Standard Development Setup

```bash
ansible-playbook -i inventory.yml setup.yml --limit development
```

**Result**: Base setup with 98 packages + 38 VS Code extensions

### Full SRE/DevOps Setup

```bash
ansible-playbook -i inventory.yml setup.yml --limit sre
```

**Result**: Extended SRE stack with 115 packages + 38 VS Code extensions

### Local Machine (Current Mac)

```bash
ansible-playbook -i inventory.yml setup.yml --limit localhost
```

---

## Pre-Deployment Checklist

### 1. Prerequisites

- [ ] macOS 13+ (Ventura or later)
- [ ] Command Line Tools installed: `xcode-select --install`
- [ ] Ansible installed: `brew install ansible`
- [ ] Git installed (for cloning roles/plugins)

### 2. Backup Current Config

```bash
# Backup existing dotfiles
cp ~/.zshrc ~/.zshrc.backup
cp ~/.tmux.conf ~/.tmux.conf.backup 2>/dev/null || true
cp ~/.config/nvim ~/.config/nvim.backup -r 2>/dev/null || true
```

### 3. Review Configuration

- [ ] Check `inventory.yml` - add your machines to appropriate groups
- [ ] Review `group_vars/all.yml` - verify feature flags
- [ ] Review `group_vars/development.yml` or `group_vars/sre.yml`

---

## Configuration Files Verification

### Core Files (All Created)

```text
- Brewfile (98 packages)
- Brewfile.sre (115 packages)
- setup.yml (main playbook)
- inventory.yml (with sre group)
- group_vars/all.yml
- group_vars/development.yml
- group_vars/sre.yml
```

### Dotfiles (All Created)

```text
- dotfiles/.zshrc (with 9 GNU PATH exports)
- dotfiles/.tmux.conf (with TPM + 6 plugins)
- dotfiles/.inputrc (readline configuration)
- dotfiles/.direnvrc (environment management)
- dotfiles/.gitconfig
- dotfiles/.vimrc
```

### Documentation (All Created)

```text
- README.md
- QUICKSTART-ANSIBLE.md
- DEPLOYMENT-GUIDE.md (this file)
- KNOWN-ISSUES.md
```

---

## Package Counts

### Base Brewfile (98 packages)

- **82 formulas** (CLI tools)
- **16 casks** (GUI applications)

**Includes SRE essentials**:

- stern, kustomize, dive, ctop (Kubernetes)
- yq, jq (data processing)
- gh, direnv, pre-commit (development)
- shellcheck, yamllint, hadolint, tflint, trivy (security)
- Rectangle, Postman (productivity)

### SRE Brewfile (115 packages)

- **101 formulas** (extended CLI tools)
- **14 casks** (specialized apps)

**Additional tools**:

- flux, argocd, skaffold (GitOps)
- azure-cli, vault (cloud)
- opentofu, terragrunt, packer, pulumi (IaC)
- prometheus, grafana, promtail (monitoring)
- checkov, cosign, syft, grype (advanced security)
- wireshark (network analysis)

### VS Code Extensions

- **22 common extensions** (all machines)
- **16 additional extensions** (dev/sre groups)
- **Total: 38 extensions** for development/sre roles

---

## Deployment Workflow

### Step 1: Syntax Check

```bash
ansible-playbook setup.yml --syntax-check
```

Expected output: `playbook: setup.yml`

### Step 2: Dry Run (Check Mode)

```bash
ansible-playbook -i inventory.yml setup.yml --check --limit localhost
```

Shows what would be changed without making changes.

### Step 3: Deploy to Current Machine

```bash
# Standard development setup
ansible-playbook -i inventory.yml setup.yml --limit development

# OR SRE setup
ansible-playbook -i inventory.yml setup.yml --limit sre
```

### Step 4: Deploy Specific Tags Only

```bash
# Only install packages
ansible-playbook -i inventory.yml setup.yml --tags packages

# Only configure shell
ansible-playbook -i inventory.yml setup.yml --tags shell

# Only configure neovim
ansible-playbook -i inventory.yml setup.yml --tags neovim

# Only configure VS Code
ansible-playbook -i inventory.yml setup.yml --tags vscode

# Available tags: packages, shell, neovim, vscode, tmux, direnv,
#                 git, macos, dock, sudoers
```

---

## Post-Deployment Steps

### 1. Shell Configuration

```bash
# Reload shell configuration
source ~/.zshrc

# Verify Powerlevel10k theme loads
# You may need to configure it on first run: p10k configure
```

### 2. Tmux Plugin Installation

```bash
# Start tmux
tmux

# Press prefix + I (Ctrl+A then Shift+I) to install TPM plugins
# Plugins will download automatically
```

### 3. Neovim Plugin Installation

```bash
# Open neovim
nvim

# Plugins auto-install via lazy.nvim
# Wait for installation to complete
```

### 4. VS Code Extensions

Extensions install automatically. Verify:

```bash
code --list-extensions | wc -l
# Should show 38+ extensions
```

### 5. direnv Setup

```bash
# direnv is installed and hooked into zsh
# For each project with .envrc file:
cd /path/to/project
direnv allow

# Example .envrc for Kubernetes project:
# use mise
# export KUBECONFIG=$PWD/.kube/config
```

### 6. Cloud CLI Setup (SRE only)

**AWS**:

```bash
aws configure sso
aws sso login --profile production
```

**Azure**:

```bash
az login
az account set --subscription "Production"
```

### 7. kubectl Plugins (SRE only)

```bash
# Install recommended plugins
kubectl krew install ctx ns neat tree tail who-can access-matrix view-secret
```

---

## Verification Commands

### Package Installation

```bash
# Check Homebrew packages
brew list --formula | wc -l  # Should be 82+ (base) or 101+ (SRE)
brew list --cask | wc -l     # Should be 16+ (base) or 14+ (SRE)

# Check specific critical tools
command -v stern kubectl k9s helm gh direnv yq jq
```

### Shell Tools

```bash
# Verify GNU tools are in PATH
which sed     # Should show /opt/homebrew/opt/gnu-sed/...
which gsed    # Should show /opt/homebrew/opt/gsed/...
which tar     # Should show /opt/homebrew/opt/gnu-tar/...

# Verify aliases
alias | grep -E "(ls|cat|vim)"
# ls='lsd --color=always --sort=extension'
# cat='bat --paging=never'
# vim='nvim'
```

### Neovim

```bash
# Check neovim version
nvim --version  # Should be 0.9+

# Check plugin count
nvim +":Lazy" +qa
# Should show ~27 plugins installed
```

### VS Code

```bash
# List extensions
code --list-extensions

# Count extensions
code --list-extensions | wc -l
# Development: 38+ extensions
# SRE: 38+ extensions
```

### Tmux

```bash
# Check tmux version
tmux -V  # Should be 3.3+

# Check TPM installation
ls ~/.tmux/plugins/tpm  # Should exist

# List tmux plugins (inside tmux)
tmux list-keys | grep plugin
```

### Security Tools (SRE)

```bash
# Verify security scanners
command -v trivy checkov hadolint tflint shellcheck yamllint
```

---

## Troubleshooting

### Issue: "command not found" after installation

**Solution**: Reload shell configuration

```bash
source ~/.zshrc
# OR restart terminal
```

### Issue: Tmux plugins not loading

**Solution**: Install TPM plugins manually

```bash
tmux
# Press: Ctrl+A then Shift+I
```

### Issue: Neovim plugins missing

**Solution**: Force reinstall

```bash
nvim
:Lazy sync
:Lazy restore
```

### Issue: VS Code extensions not installing

**Solution**: Install manually

```bash
while IFS= read -r ext; do code --install-extension "$ext"; done < <(
  ansible-playbook -i inventory.yml setup.yml --list-tags 2>/dev/null | \
  grep vscode_extensions
)
```

### Issue: Homebrew packages fail to install

**Solution**: Update Homebrew and retry

```bash
brew update
brew upgrade
brew bundle install --file=Brewfile
```

### Issue: Permission denied on sudoers task

**Solution**: Run with sudo password

```bash
ansible-playbook -i inventory.yml setup.yml --ask-become-pass
```

---

## Inventory Group Configuration

### Adding New Machines

**Development Machine**:

```yaml
# Add to inventory.yml under development group
development:
  hosts:
    dev-macbook-1:
      ansible_host: dev-macbook-1.local
```

**SRE Machine**:

```yaml
# Add to inventory.yml under sre group
sre:
  hosts:
    sre-macbook-1:
      ansible_host: sre-macbook-1.local
```

### Custom Configuration Per Machine

Create `host_vars/hostname.yml`:

```yaml
# host_vars/dev-macbook-1.yml
brewfile_name: Brewfile.sre  # Use SRE Brewfile on dev machine
vscode_extensions_extra:
  - custom.extension
  - another.extension
```

---

## Tag Reference

| Tag | Description | Example |
|-----|-------------|---------|
| `packages` | Install Homebrew packages | `--tags packages` |
| `shell` | Configure zsh, oh-my-zsh | `--tags shell` |
| `neovim` | Install/configure Neovim | `--tags neovim` |
| `tmux` | Install/configure tmux | `--tags tmux` |
| `direnv` | Setup direnv | `--tags direnv` |
| `vscode` | Install VS Code + extensions | `--tags vscode` |
| `git` | Configure git | `--tags git` |
| `macos` | macOS defaults | `--tags macos` |
| `dock` | Configure Dock | `--tags dock` |
| `sudoers` | Passwordless sudo | `--tags sudoers` |

---

## Quick Reference

### Deployment Commands

```bash
# Check syntax
ansible-playbook setup.yml --syntax-check

# Dry run
ansible-playbook -i inventory.yml setup.yml --check --limit localhost

# Deploy development setup
ansible-playbook -i inventory.yml setup.yml --limit development

# Deploy SRE setup
ansible-playbook -i inventory.yml setup.yml --limit sre

# Deploy to specific machine
ansible-playbook -i inventory.yml setup.yml --limit dev-macbook-1

# Deploy only packages
ansible-playbook -i inventory.yml setup.yml --tags packages

# Deploy with sudo password prompt
ansible-playbook -i inventory.yml setup.yml --ask-become-pass
```

### Post-Install Commands

```bash
# Reload shell
source ~/.zshrc

# Install tmux plugins (in tmux)
# Ctrl+A then Shift+I

# Sync neovim plugins
nvim +":Lazy sync" +qa

# Verify installations
brew list
code --list-extensions
command -v stern kubectl k9s helm
```

---

## Success Indicators

### Base Setup Complete When

- [ ] 82+ Homebrew formulas installed
- [ ] 16+ Homebrew casks installed
- [ ] Zsh configured with Powerlevel10k
- [ ] Neovim with ~27 plugins
- [ ] Tmux with 6 plugins
- [ ] VS Code with 38 extensions
- [ ] All GNU tools in PATH
- [ ] direnv configured and working

### SRE Setup Complete When

- [ ] All base requirements met
- [ ] 101+ Homebrew formulas installed
- [ ] Kubernetes tools available (stern, kustomize, k9s, helm)
- [ ] Cloud CLIs installed (aws, azure)
- [ ] IaC tools available (terraform, tenv, opentofu)
- [ ] Security scanners working (trivy, checkov, hadolint)
- [ ] Monitoring tools available (prometheus, grafana)
- [ ] direnv with project-specific environments

---

## Brewfile Maintenance & Synchronization

### Important: Brewfile.sre Must Be Manually Synced

**CRITICAL**: Due to Homebrew limitations, `Brewfile.sre` duplicates all base packages
from `Brewfile` plus SRE-specific additions. **These must be manually synchronized**
when updating packages.

### Why This Design?

Homebrew\'s Brewfile format doesn\'t support imports or includes, so we must:

1. Maintain a base `Brewfile` for all machines
2. Duplicate base packages in `Brewfile.sre` plus add SRE tools

### Updating Packages

When adding/removing packages, update **BOTH** files:

#### Example: Adding a new package

```bash
# 1. Add to Brewfile (base)
echo 'brew "ripgrep"  # Better grep' >> Brewfile

# 2. Add to Brewfile.sre at the same location
# Edit Brewfile.sre manually to add the same line
```

#### Example: Removing a package

```bash
# 1. Remove from Brewfile
sed -i '' '/brew "htop"/d' Brewfile

# 2. Remove from Brewfile.sre
sed -i '' '/brew "htop"/d' Brewfile.sre
```

### Verification Script

Check for sync issues between Brewfiles:

```bash
# Create verification script
cat > verify-brewfiles.sh << 'EOF'
#!/usr/bin/env bash
# Verify Brewfile synchronization

BASE_PKGS=$(grep '^brew "' Brewfile | sort)
SRE_PKGS=$(grep '^brew "' Brewfile.sre | sort)

echo "Checking for packages in Brewfile but missing from Brewfile.sre..."
comm -23 <(echo "$BASE_PKGS") <(echo "$SRE_PKGS")

if [ $? -eq 0 ]; then
  echo "[PASS] All base packages are in Brewfile.sre"
else
  echo "[WARN] Some base packages are missing from Brewfile.sre"
fi
EOF

chmod +x verify-brewfiles.sh
./verify-brewfiles.sh
```

### Best Practices

1. **Use Comments**: Add descriptive comments to both files

    ```ruby
    brew "ripgrep"  # Better grep (search tool)
    ```

2. **Group by Category**: Keep related packages together

    ```ruby
    # CLI Tools - Utilities
    brew "bat"
    brew "lsd"
    brew "fzf"
    ```

3. **Version Control**: Always commit both files together

    ```bash
    git add Brewfile Brewfile.sre
    git commit -m "feat: add ripgrep to both Brewfiles"
    ```

4. **Test Both**: After changes, test both Brewfiles

    ```bash
    # Test base
    brew bundle check --file=Brewfile

    # Test SRE
    brew bundle check --file=Brewfile.sre
    ```

### SRE-Specific Packages

These packages should ONLY be in `Brewfile.sre`:

**Infrastructure as Code**:

- `opentofu/tap/opentofu`
- `terragrunt`
- `packer`
- `pulumi`

**Monitoring & Observability**:

- `prometheus`
- `grafana`
- `promtail`

**Security Scanners**:

- `checkov`
- `cosign`
- `syft`
- `grype`

**GitOps & Advanced Kubernetes**:

- `flux`
- `argocd`
- `skaffold`

**Cloud Providers**:

- `azure-cli`
- `hashicorp/tap/vault`

**Load Testing**:

- `vegeta`
- `wrk`

**Networking**:

- `mosh`
- `wireguard-tools`
- `wireshark` (cask)

### Automated Sync (Future Enhancement)

Consider creating a script to auto-generate `Brewfile.sre` from `Brewfile`:\n\n```bash

# !/usr/bin/env bash

# generate-sre-brewfile.sh (example - not yet implemented)

# Copy base Brewfile

cp Brewfile Brewfile.sre.new

# Append SRE-specific packages

cat >> Brewfile.sre.new << 'EOF'

# ============================================================================

# SRE-Specific Additions

# ============================================================================

# Infrastructure as Code

tap "opentofu/tap"
brew "opentofu/tap/opentofu"
brew "terragrunt"

# ... (add all SRE-specific packages)

EOF

# Replace old file

mv Brewfile.sre.new Brewfile.sre

```

---

## Support

### Documentation

- Main README: `README.md`
- Quick Start: `QUICKSTART-ANSIBLE.md`
- Troubleshooting: `KNOWN-ISSUES.md`
- Brewfile Sync: See "Brewfile Maintenance" section above
- SRE Tools: See inline comments in `Brewfile.sre`

### Common Issues

Check Ansible logs:

```bash
ansible-playbook -i inventory.yml setup.yml --limit localhost -vvv
```

### Rollback

If issues occur, restore backups:

```bash
cp ~/.zshrc.backup ~/.zshrc
cp ~/.tmux.conf.backup ~/.tmux.conf
cp -r ~/.config/nvim.backup ~/.config/nvim
```

---

**Last Updated**: 2025-10-26
**Setup Version**: 2.0 (SRE Enhanced)
