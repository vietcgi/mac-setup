# Devkit - Modern Development Environment Setup

**Fast, cross-platform, reproducible development environment for desktop machines.**

![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-blue)
![Setup Time](https://img.shields.io/badge/setup%20time-~10%20min-green)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

---

## Quick Start (One Command)

**Set up your entire development environment in ~10 minutes:**

```bash
./bootstrap.sh
```

**Done!** Your desktop is now configured with:

- 100+ development tools & utilities
- Shell environment (zsh + Oh My Zsh + Powerlevel10k)
- Modern editors (Neovim with LSP, VS Code with extensions)
- Version managers (mise for node/go/python)
- Dotfiles (managed with chezmoi)
- macOS configuration (Dock, defaults)

**Clone and run:**

```bash
git clone https://github.com/vietcgi/devkit.git
cd devkit
./bootstrap.sh
```

**Verify your setup:**

```bash
./verify-setup.sh
```

**For detailed guide:** See [QUICKSTART.md](QUICKSTART.md)

---

## System Requirements

### Supported Platforms

**macOS**:

- macOS 13.0 (Ventura) or later
- macOS 14.0 (Sonoma) - Recommended
- macOS 15.0 (Sequoia) - Supported
- Both Intel (x86_64) and Apple Silicon (M1/M2/M3/M4) architectures

**Linux**:

- Ubuntu 20.04 LTS or later
- Debian 11+ (Bullseye or later)
- Other Debian-based distributions (should work, but not extensively tested)
- Note: GUI apps (casks) require manual installation on Linux

### Hardware Requirements

**Minimum**:

- **CPU**: Any modern 64-bit processor (Intel or ARM)
- **RAM**: 8 GB
- **Disk**: 10 GB free space
- **Network**: Stable internet connection for downloads

**Recommended**:

- **CPU**: Multi-core processor (Apple Silicon M1+ or Intel i5+)
- **RAM**: 16 GB or more
- **Disk**: 20 GB+ free space (especially for SRE setup)
- **Network**: Broadband connection (will download ~5GB of packages)

### Software Prerequisites

**Automatically installed if missing**:

- Xcode Command Line Tools (macOS)
- Homebrew
- Ansible

**Required for full functionality**:

- Git (usually pre-installed)
- Zsh (usually pre-installed on modern systems)
- Admin/sudo access (for initial Homebrew install only)

### Network Requirements

- **Internet access** required for:
  - Downloading packages from Homebrew
  - Cloning Git repositories (Oh My Zsh, plugins, etc.)
  - Installing mise tool versions
  - VS Code extension downloads
- **Firewall/Proxy**: If behind a corporate firewall, ensure access to:
  - github.com (Git repositories)
  - raw.githubusercontent.com (install scripts)
  - Homebrew CDN domains
  - VS Code marketplace

### Performance Expectations

| Configuration | Hardware | Time |
|---------------|----------|------|
| Base Setup | Apple M2 | ~1-2 min |
| Base Setup | Intel i5 | ~2-3 min |
| SRE Setup | Apple M2 | ~3-4 min |
| SRE Setup | Intel i5 | ~4-5 min |

*Times vary based on internet speed and system performance.*

---

## Project Documentation

### Essential Guides (Start Here)

- **[QUICKSTART-ANSIBLE.md](QUICKSTART-ANSIBLE.md)** - Complete setup guide
- **[KNOWN-ISSUES.md](KNOWN-ISSUES.md)** - Troubleshooting & common problems
- **[verify-setup.sh](verify-setup.sh)** - Verify your installation

### Production & Migration

- **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Production deployment &
  fleet management for 20+ machines
- **[ANSIBLE-MIGRATION.md](ANSIBLE-MIGRATION.md)** - Migrate from old Ansible setup
- **[CHANGELOG.md](CHANGELOG.md)** - Version history & breaking changes

### Community & Support

- **[SUPPORT.md](SUPPORT.md)** - How to get help and ask questions
- **[SECURITY.md](SECURITY.md)** - Security policy and vulnerability reporting
- **[update.sh](update.sh)** - Update all packages and tools

---

## What's Included

### Core Tools

- **Package Management**: Homebrew with Brewfile (100+ packages)
- **Version Management**: mise (unified manager for node, go, python, ruby)
- **Shell**: zsh + Oh My Zsh + Powerlevel10k + 10+ plugins
- **Terminal**: Ghostty (GPU-accelerated, cross-platform) + iTerm2 (macOS alternative)
- **Editors**: Neovim (Lua-based with LSP) + VS Code (60+ extensions)
- **Dotfiles**: chezmoi (Git-based sync)
- **Task Runner**: Just (cross-platform Makefile alternative)
- **Testing**: Multipass (lightweight Ubuntu VMs)

### Development

- Languages: Node.js, Go, Python, PHP, Ruby
- Kubernetes: kubectl, helm, k9s, kind, kustomize, stern
- Cloud: AWS CLI, eksctl, aws-iam-authenticator
- Containers: Docker Desktop, dive, ctop
- Utilities: bat, lsd, fzf, jq, yq, httpie, htop

### SRE/DevOps (Brewfile.sre)

- IaC: Terraform (via tenv), Terragrunt, Packer, Pulumi
- Monitoring: Prometheus, Grafana, Promtail
- Security: Trivy, Checkov, Cosign, Syft, Grype
- GitOps: Flux, ArgoCD, Skaffold
- Cloud: Azure CLI, Vault

---

## Architecture

### Single Bootstrap Design

```
devkit/
├── bootstrap.sh               # PRIMARY ENTRY POINT - Zero-dependency bootstrap
├── setup.yml                  # Main Ansible playbook
├── inventory.yml              # Ansible inventory
├── verify-setup.sh            # Post-setup verification
├── Brewfile                   # All packages (Homebrew's native format)
├── Brewfile.sre              # SRE-specific additions
├── .mise.toml                # Tool version management
├── group_vars/               # Group-specific configuration
│   ├── all.yml              # Global settings
│   ├── development.yml      # Dev machines
│   └── sre.yml              # SRE machines
├── host_vars/               # Host-specific overrides
├── config/                   # Configuration files
│   ├── config.yaml          # User configuration
│   └── schema.yaml          # Configuration schema
└── dotfiles/                # Managed by chezmoi
    ├── .zshrc
    ├── .tmux.conf
    └── nvim/
```

### Why This Approach?

| Feature | This Setup | Old Ansible | Shell Scripts |
|---------|------------|-------------|---------------|
| **Setup Time** | ~2 min | ~10 min | ~2 min |
| **External Dependencies** | 0 roles | 8 roles | 0 |
| **Platforms** | Mac + Linux | Mac only | Mac + Linux |
| **Fleet Management** | Yes | No | No |
| **Idempotent** | Yes | Yes | Partial |
| **Package Format** | Native Brewfile | YAML lists | Native Brewfile |
| **Maintainability** | 5/5 | 2/5 | 4/5 |

---

## Features

### Cross-Platform

- Automatically detects macOS vs Linux
- Adjusts paths and packages accordingly
- macOS: Full GUI app support via Homebrew Cask
- Linux: CLI tools + manual GUI app installation

### Fleet Management

Manage different machine types with inventory groups:

- **workstations**: GUI apps, Docker, VS Code
- **development**: Dev tools, databases, debuggers
- **sre**: Monitoring, IaC, security scanners
- **qa**: Testing tools
- **design**: Design tools instead of dev tools

### Idempotent & Safe

- Run multiple times without issues
- Skips already-installed components
- Backs up existing configs before overwriting
- Feature flags to enable/disable components

### Modern Tool Integration

- **Homebrew**: Native Brewfile format (not YAML)
- **mise**: Replaces nvm, rbenv, pyenv with unified tool
- **chezmoi**: Purpose-built dotfile manager
- **Just**: Cross-platform task runner

---

## Setup Options

### Option 1: Standard Setup (Recommended)

**→ `./bootstrap.sh`**

Perfect for:

- Desktop machines (Mac/Linux)
- GUI app installation
- Most developers
- Zero Python dependency in bootstrap

Includes: 100+ development tools, shell config, editors

### Option 2: Interactive Setup

**→ `./bootstrap.sh --interactive`**

Perfect for:

- First-time users
- Customized installations
- Choosing specific roles
- Learning what gets installed

### Option 3: SRE/DevOps Setup

**→ Use `Brewfile.sre` instead of `Brewfile`**

Perfect for:

- Platform engineers
- SRE teams
- DevOps workstations
- Extended monitoring & IaC tools

See [DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md) for SRE setup instructions.

### Option 4: Verification Only

**→ `./bootstrap.sh --verify-only`**

Perfect for:

- Checking prerequisites
- System compatibility test
- Dry-run before full setup

---

## Customization

### Feature Flags

Control what gets installed via `group_vars/all.yml`:

```yaml
install_shell_tools: true
install_neovim: true
install_vscode: true
install_gui_apps: true
install_dev_tools: true
configure_dotfiles: true
configure_dock: true           # macOS only
configure_macos_defaults: true # macOS only
```

### Per-Machine Customization

```bash
# group_vars/sre.yml - all SRE machines
brewfile_name: Brewfile.sre
install_monitoring_tools: true
install_security_scanners: true

# host_vars/my-laptop.yml - specific machine
install_gui_apps: false
vscode_extensions_extra:
  - ms-vscode-remote.remote-ssh
```

---

## Testing & Verification

### Verify Setup

```bash
# Run verification script
./verify-setup.sh

# Check specific components
ansible-playbook -i inventory.yml setup.yml --tags homebrew --check
ansible-playbook -i inventory.yml setup.yml --tags mise --check
```

### Idempotency Test

```bash
# Run twice - second run should show no changes
ansible-playbook -i inventory.yml setup.yml
ansible-playbook -i inventory.yml setup.yml
```

### Testing on Linux (using Multipass)

Test the setup on Ubuntu without affecting your main system:

```bash
# Launch Ubuntu VM
multipass launch --name test-setup ubuntu:22.04 --cpus 2 --memory 4G --disk 20G

# Transfer setup files
multipass transfer bootstrap-ansible.sh test-setup:/home/ubuntu/

# Run setup in VM
multipass exec test-setup -- bash /home/ubuntu/bootstrap-ansible.sh

# Test specific components
multipass exec test-setup -- bash -c "brew list | wc -l"
multipass exec test-setup -- bash -c "mise list"

# SSH into VM for manual testing
multipass shell test-setup

# Clean up when done
multipass delete test-setup
multipass purge
```

**Test different Ubuntu versions**:

```bash
# Ubuntu 20.04 LTS
multipass launch ubuntu:20.04 --name test-focal

# Ubuntu 22.04 LTS (Jammy)
multipass launch ubuntu:22.04 --name test-jammy

# Ubuntu 24.04 LTS (Noble)
multipass launch ubuntu:24.04 --name test-noble
```

---

## Contributing

### Pre-commit Hooks

```bash
# Install pre-commit
brew install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Testing Changes

```bash
# Test on local machine
ansible-playbook -i inventory.yml setup.yml --check

# Test specific tags
ansible-playbook -i inventory.yml setup.yml --tags shell --check

# Verify with script
./verify-setup.sh
```

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

---

## Getting Help

### Further Documentation

- **[KNOWN-ISSUES.md](KNOWN-ISSUES.md)** - Common problems & solutions
- **[QUICKSTART-ANSIBLE.md](QUICKSTART-ANSIBLE.md)** - Detailed setup guide
- **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** - Advanced deployment

### Run Verification

```bash
./verify-setup.sh
```

### Check Logs

```bash
# Run with verbose output
ansible-playbook -i inventory.yml setup.yml -vvv
```

---

### Made with care for developers, by developers
