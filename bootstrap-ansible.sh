#!/usr/bin/env bash

###############################################################################
# Modern Ansible Bootstrap Script
# Cross-platform bootstrap for macOS and Linux
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "darwin"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)

# Homebrew paths
if [[ "$OS" == "darwin" ]]; then
    HOMEBREW_PREFIX="/opt/homebrew"
else
    HOMEBREW_PREFIX="/home/linuxbrew/.linuxbrew"
fi

# Helper functions
print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

# Retry function for network operations
retry() {
    local max_attempts=3
    local timeout=5
    local attempt=1
    local exitCode=0

    while (( attempt <= max_attempts )); do
        if [[ $attempt -gt 1 ]]; then
            print_warning "Attempt $attempt of $max_attempts..."
            sleep $timeout
        fi

        "$@"
        exitCode=$?

        if [[ $exitCode -eq 0 ]]; then
            return 0
        fi

        attempt=$(( attempt + 1 ))
    done

    print_error "Failed after $max_attempts attempts"
    return $exitCode
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script must NOT be run as root (Homebrew requirement)"
    exit 1
fi

###############################################################################
# Main Bootstrap
###############################################################################

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║        Modern Ansible Mac/Linux Setup                         ║"
    echo "║        Simplified, Fast, Cross-Platform                       ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    print_info "Detected OS: $OS"

    # Pre-flight checks
    if [[ "$OS" == "unknown" ]]; then
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    # Step 1: Install Xcode Command Line Tools (macOS only)
    if [[ "$OS" == "darwin" ]]; then
        if ! xcode-select -p &> /dev/null; then
            print_info "Installing Xcode Command Line Tools..."
            xcode-select --install

            print_info "Waiting for Xcode Command Line Tools installation..."
            until xcode-select -p &> /dev/null; do
                sleep 5
            done
            print_success "Xcode Command Line Tools installed"
        else
            print_success "Xcode Command Line Tools already installed"
        fi
    fi

    # Step 2: Install Homebrew
    if command -v brew &> /dev/null; then
        print_success "Homebrew already installed"
    else
        print_info "Installing Homebrew..."
        if retry /bin/bash -c "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
            # Add Homebrew to PATH for this session
            eval "$($HOMEBREW_PREFIX/bin/brew shellenv)"
            print_success "Homebrew installed"
        else
            print_error "Failed to install Homebrew after retries"
            exit 1
        fi
    fi

    # Ensure brew is in PATH
    if ! command -v brew &> /dev/null; then
        eval "$($HOMEBREW_PREFIX/bin/brew shellenv)"
    fi

    # Step 3: Install Ansible
    if command -v ansible-playbook &> /dev/null; then
        print_success "Ansible already installed"
    else
        print_info "Installing Ansible..."
        if retry brew install ansible; then
            print_success "Ansible installed"
        else
            print_error "Failed to install Ansible after retries"
            exit 1
        fi
    fi

    # Step 4: Install Ansible community.general collection
    print_info "Ensuring Ansible collections are installed..."
    retry ansible-galaxy collection install community.general --force || print_warning "Could not install Ansible collections (non-critical)"

    # Step 5: Run the Ansible playbook
    echo ""
    print_info "Running Ansible playbook..."
    echo ""

    ansible-playbook -i inventory.yml setup.yml -v

    # Step 6: Done!
    echo ""
    print_success "Bootstrap complete!"
    echo ""
    print_info "Next steps:"
    echo "  1. Restart your terminal (or run: source ~/.zshrc)"
    echo "  2. Configure Powerlevel10k: p10k configure"
    echo "  3. Install Vim plugins: vim +PlugInstall +qall"
    echo ""
    print_info "To update in the future:"
    echo "  • Modify Brewfile to add/remove packages"
    echo "  • Modify .mise.toml to change tool versions"
    echo "  • Re-run: ansible-playbook setup.yml"
    echo ""
}

# Run main function
main "$@"
