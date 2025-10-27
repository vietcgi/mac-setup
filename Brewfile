# Homebrew Bundle file for Mac/Linux Setup
# Cross-platform package definitions
# Usage: brew bundle [install]
#
# Notes:
# - All 'brew' packages work on both macOS and Linux
# - 'cask' packages are macOS-only (ignored on Linux)
# - Linux users: some GUI apps need manual installation

# Taps (repositories)
# Note: Core taps are no longer needed (deprecated as of 2025)

# CLI Tools - Development
brew "git"
brew "node"
brew "go"
brew "php"
brew "postgresql"
brew "neovim"                   # Modern vim replacement

# CLI Tools - Kubernetes & Cloud
brew "kubectl"
brew "kind"
brew "k9s"
brew "helm"
brew "eksctl"
brew "kubectx"
brew "krew"
brew "stern"                    # Kubernetes log tailing
brew "kustomize"                # Kubernetes config management
brew "dive"                     # Docker image layer explorer
brew "ctop"                     # Container top
brew "aws-iam-authenticator"
brew "awscli"
brew "aws-sso-util"

# CLI Tools - Utilities
brew "bat"                      # Better cat
brew "ccat"
brew "lsd"                      # Better ls
brew "tree"
brew "fzf"                      # Fuzzy finder
brew "jq"                       # JSON processor
brew "yq"                       # YAML processor
brew "thefuck"                  # Command correction
brew "httpie"                   # HTTP client
brew "grpcurl"                  # gRPC curl
brew "htop"                     # Process viewer
brew "bottom"                   # Modern system monitor (btm)
brew "procs"                    # Modern ps replacement
brew "ncdu"                     # Disk usage analyzer
brew "mtr"                      # Network diagnostics
brew "tmux"                     # Terminal multiplexer
brew "nmap"                     # Network scanner
brew "iperf"                    # Network bandwidth
brew "pv"                       # Progress viewer
brew "wrk"                      # HTTP benchmarking
brew "cowsay"                   # Fun utility
brew "ansible-lint"
brew "grc"                      # Generic colouriser

# CLI Tools - Build & Dev Dependencies
brew "autoconf"
brew "bash-completion"
brew "doxygen"
brew "gettext"
brew "gifsicle"
brew "gpg"
brew "libevent"
brew "libtool"
brew "sqlite"
brew "readline"
brew "openssl"

# GNU Utilities (replace macOS defaults)
brew "coreutils"
brew "diffutils"
brew "findutils"
brew "gawk"
brew "gnu-indent"
brew "gnu-sed"
brew "gnu-tar"
brew "gnu-which"
brew "gnutls"
brew "grep"
brew "gzip"
brew "watch"
brew "wget"

# Linting & Security
brew "shellcheck"               # Shell script linter
brew "yamllint"                 # YAML linter
brew "hadolint"                 # Dockerfile linter
brew "tflint"                   # Terraform linter
brew "trivy"                    # Container/IaC security scanner

# Shell Enhancements
brew "zsh-history-substring-search"

# Dotfiles Management
brew "chezmoi"                  # Dotfiles manager with Git sync

# Version Managers
brew "mise"                     # Modern unified tool version manager (manages node, go, python, ruby, etc.)
brew "tenv"                     # Terraform/Terragrunt/OpenTofu version manager

# Development Tools
brew "gh"                       # GitHub CLI
brew "direnv"                   # Environment variable management
brew "pre-commit"               # Git hooks framework

# SSH Utilities
brew "ssh-copy-id"

# ============================================================================
# macOS-Only Applications (casks)
# Linux users: Install these manually via your package manager
# ============================================================================
cask "docker-desktop"
cask "google-chrome"
cask "firefox"
cask "ghostty"                 # Modern cross-platform terminal (GPU-accelerated)
cask "iterm2"                  # Alternative terminal (macOS-only)
cask "multipass"               # Lightweight Ubuntu VMs for testing
cask "visual-studio-code"
cask "slack"
cask "sequel-ace"              # MySQL/MariaDB database management
cask "transmit"                # FTP/SFTP client
cask "dropbox"
cask "vagrant"
cask "handbrake-app"           # Video transcoder
cask "licecap"                 # GIF screen recorder

# Productivity & DevOps
cask "rectangle"               # Window management
cask "postman"                 # API testing

# Drivers
cask "chromedriver"

# Fonts (for Powerlevel10k)
cask "font-meslo-lg-nerd-font"

# Mac App Store CLI
brew "mas"

# Mac App Store apps
# Note: Uncomment and add app IDs as needed
# Find app IDs: mas search "app name"
# Example: mas "Xcode", id: 497799835
# mas_installed_apps: []
