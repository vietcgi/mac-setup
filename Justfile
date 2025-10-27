# Cross-Platform Mac/Linux Setup Automation
# Requires: just (brew install just)
# Usage: just <recipe>

# Default recipe - show available commands
default:
    @just --list

# Detect OS
os := if os() == "macos" { "darwin" } else { "linux" }
brew_prefix := if os() == "macos" { "/opt/homebrew" } else { "/home/linuxbrew/.linuxbrew" }

# ============================================================================
# Main Workflows
# ============================================================================

# Complete system bootstrap (run this first!)
bootstrap: install-homebrew install-tools setup-shell setup-vim setup-vscode macos-settings
    @echo "[OK] Bootstrap complete!"
    @echo "Please restart your terminal to activate changes"

# Quick update (packages + dotfiles)
update: brew-update mise-update
    @echo "[OK] System updated!"

# ============================================================================
# Homebrew
# ============================================================================

# Install Homebrew (if not present)
install-homebrew:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v brew &> /dev/null; then
        echo "[INSTALL] Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add to PATH for this session
        if [ "{{ os }}" = "linux" ]; then
            eval "$({{ brew_prefix }}/bin/brew shellenv)"
        fi
    else
        echo "[OK] Homebrew already installed"
    fi

# Install all packages from Brewfile
brew-install: install-homebrew
    @echo "[INSTALL] Installing packages from Brewfile..."
    brew bundle install --file=Brewfile

# Update all Homebrew packages
brew-update:
    @echo "[INSTALL] Updating Homebrew packages..."
    brew update
    brew upgrade
    brew cleanup

# ============================================================================
# Development Tools
# ============================================================================

# Install all tools (mise, packages, etc.)
install-tools: install-homebrew brew-install install-mise
    @echo "[OK] All tools installed"

# Install mise and tool versions
install-mise:
    #!/usr/bin/env bash
    set -euo pipefail
    if ! command -v mise &> /dev/null; then
        echo "[INSTALL] Installing mise..."
        brew install mise
    fi
    echo "[INSTALL] Installing tool versions from .mise.toml..."
    mise install

# Update mise tools
mise-update:
    @echo "[INSTALL] Updating mise tools..."
    mise upgrade
    mise prune

# ============================================================================
# Shell Configuration
# ============================================================================

# Setup Zsh with Oh My Zsh + Powerlevel10k
setup-shell:
    #!/usr/bin/env bash
    set -euo pipefail

    # Install Oh My Zsh
    if [ ! -d "$HOME/.oh-my-zsh" ]; then
        echo "[SHELL] Installing Oh My Zsh..."
        sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    fi

    # Install Powerlevel10k theme
    if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k" ]; then
        echo "🎨 Installing Powerlevel10k theme..."
        git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
            ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
    fi

    # Install zsh plugins
    echo "[PLUGIN] Installing zsh plugins..."

    # zsh-syntax-highlighting
    if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ]; then
        git clone https://github.com/zsh-users/zsh-syntax-highlighting.git \
            ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    fi

    # zsh-autosuggestions
    if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" ]; then
        git clone https://github.com/zsh-users/zsh-autosuggestions \
            ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    fi

    # zsh-completions
    if [ ! -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-completions" ]; then
        git clone https://github.com/zsh-users/zsh-completions \
            ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-completions
    fi

    echo "[OK] Shell setup complete!"
    echo "[NOTE] Copy dotfiles/.zshrc to ~/.zshrc or use chezmoi"

# ============================================================================
# Vim Configuration
# ============================================================================

# Setup Vim with plugins
setup-vim:
    #!/usr/bin/env bash
    set -euo pipefail

    # Install vim-plug
    if [ ! -f "$HOME/.vim/autoload/plug.vim" ]; then
        echo "[NOTE] Installing vim-plug..."
        curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
            https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
    fi

    echo "[OK] Vim setup complete!"
    echo "[NOTE] Run :PlugInstall in vim to install plugins"

# ============================================================================
# VS Code Configuration
# ============================================================================

# Install VS Code extensions
setup-vscode:
    #!/usr/bin/env bash
    set -euo pipefail

    if ! command -v code &> /dev/null; then
        echo "⚠️  VS Code not found. Install it first."
        exit 1
    fi

    echo "[PLUGIN] Installing VS Code extensions..."

    # Extensions list from group_vars/all.yml
    extensions=(
        "streetsidesoftware.code-spell-checker"
        "wholroyd.jinja"
        "ms-python.python"
        "esbenp.prettier-vscode"
        "eamodio.gitlens"
        "donjayamanne.githistory"
        "idleberg.icon-fonts"
        "vscode-icons-team.vscode-icons"
        "wayou.vscode-todo-highlight"
        "johnpapa.vscode-peacock"
        "christian-kohler.path-intellisense"
        "yzhang.markdown-all-in-one"
        "aaron-bond.better-comments"
        "zhuangtongfa.Material-theme"
        "wesbos.theme-cobalt2"
        "redhat.vscode-yaml"
        "redhat.ansible"
        "ms-kubernetes-tools.vscode-kubernetes-tools"
        "dbaeumer.vscode-eslint"
        "ms-azuretools.vscode-docker"
        "github.vscode-pull-request-github"
        "ibm.output-colorizer"
        "hashicorp.terraform"
        "oderwat.indent-rainbow"
        "pkief.material-icon-theme"
    )

    for ext in "${extensions[@]}"; do
        if ! code --list-extensions | grep -q "^$ext$"; then
            echo "Installing $ext..."
            code --install-extension "$ext"
        else
            echo "[OK] $ext already installed"
        fi
    done

    echo "[OK] VS Code extensions installed!"

# ============================================================================
# macOS-Specific
# ============================================================================

# Configure macOS system settings (macOS only)
macos-settings:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "{{ os }}" != "darwin" ]; then
        echo "[SKIP]  Skipping macOS settings (not on macOS)"
        exit 0
    fi

    echo "[CONFIG]  Configuring macOS settings..."
    # Add your macOS defaults here
    # Example:
    # defaults write com.apple.dock autohide -bool true
    # killall Dock

    echo "[OK] macOS settings configured!"

# Configure macOS Dock (macOS only)
setup-dock:
    #!/usr/bin/env bash
    set -euo pipefail

    if [ "{{ os }}" != "darwin" ]; then
        echo "[SKIP]  Skipping Dock setup (not on macOS)"
        exit 0
    fi

    if ! command -v dockutil &> /dev/null; then
        echo "[INSTALL] Installing dockutil..."
        brew install dockutil
    fi

    echo "[DOCK] Configuring Dock..."
    # Add your dock configuration here
    # Example:
    # dockutil --remove 'TV' --no-restart
    # dockutil --add '/Applications/iTerm.app' --no-restart

    killall Dock
    echo "[OK] Dock configured!"

# ============================================================================
# Chezmoi (Dotfiles)
# ============================================================================

# Initialize chezmoi and apply dotfiles
dotfiles-init:
    #!/usr/bin/env bash
    set -euo pipefail

    if ! command -v chezmoi &> /dev/null; then
        echo "[INSTALL] Installing chezmoi..."
        brew install chezmoi
    fi

    if [ ! -d "$HOME/.local/share/chezmoi" ]; then
        echo "🏗️  Initializing chezmoi..."
        chezmoi init

        # Copy initial dotfiles
        echo "[NOTE] Adding dotfiles..."
        cp dotfiles/.zshrc ~/.zshrc
        chezmoi add ~/.zshrc
    else
        echo "[OK] chezmoi already initialized"
    fi

# Apply dotfiles from chezmoi
dotfiles-apply:
    @echo "[NOTE] Applying dotfiles..."
    chezmoi apply

# Edit dotfiles with chezmoi
dotfiles-edit file:
    chezmoi edit {{ file }}

# ============================================================================
# Cleanup
# ============================================================================

# Clean up caches and old files
clean:
    @echo "[CLEAN] Cleaning up..."
    brew cleanup
    mise cache clear
    @echo "[OK] Cleanup complete!"

# ============================================================================
# Info
# ============================================================================

# Show system information
info:
    @echo "[SYSTEM]  System: {{ os }}"
    @echo "[INSTALL] Homebrew prefix: {{ brew_prefix }}"
    @command -v brew &> /dev/null && echo "[OK] Homebrew: $(brew --version | head -n1)" || echo "[ERROR] Homebrew: not installed"
    @command -v mise &> /dev/null && echo "[OK] mise: $(mise --version)" || echo "[ERROR] mise: not installed"
    @command -v chezmoi &> /dev/null && echo "[OK] chezmoi: $(chezmoi --version)" || echo "[ERROR] chezmoi: not installed"
    @command -v code &> /dev/null && echo "[OK] VS Code: installed" || echo "[ERROR] VS Code: not installed"
