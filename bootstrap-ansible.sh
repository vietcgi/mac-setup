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

# Detect Linux package manager
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v yum &> /dev/null; then
        echo "yum"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
PKG_MGR=$(detect_package_manager)

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

    # Step 2: Install package manager and tools
    if [[ "$OS" == "darwin" ]]; then
        # macOS: Install Homebrew
        if command -v brew &> /dev/null; then
            print_success "Homebrew already installed"
        else
            print_info "Installing Homebrew..."
            if retry bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
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

        # Step 3: Install Ansible via Homebrew
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
    else
        # Linux: Detect and use appropriate package manager
        print_info "Detected package manager: $PKG_MGR"

        case "$PKG_MGR" in
            apt)
                # Debian/Ubuntu
                print_info "Updating package lists..."
                if retry sudo apt-get update -y; then
                    print_success "Package lists updated"
                else
                    print_error "Failed to update package lists"
                    exit 1
                fi

                print_info "Installing build essentials and dependencies..."
                if retry sudo apt-get install -y build-essential curl git software-properties-common; then
                    print_success "Build essentials installed"
                else
                    print_error "Failed to install build essentials"
                    exit 1
                fi

                if command -v ansible-playbook &> /dev/null; then
                    print_success "Ansible already installed"
                else
                    print_info "Installing Ansible..."
                    if retry sudo apt-get install -y ansible; then
                        print_success "Ansible installed"
                    else
                        print_error "Failed to install Ansible after retries"
                        exit 1
                    fi
                fi
                ;;

            dnf)
                # Fedora/RHEL 8+/CentOS Stream
                print_info "Updating package cache..."
                if retry sudo dnf check-update || [ $? -eq 100 ]; then
                    print_success "Package cache updated"
                else
                    print_warning "Package cache update returned non-zero (may be normal)"
                fi

                print_info "Installing Development Tools and dependencies..."
                if retry sudo dnf groupinstall -y "Development Tools"; then
                    print_success "Development Tools installed"
                else
                    print_error "Failed to install Development Tools"
                    exit 1
                fi

                if retry sudo dnf install -y curl git; then
                    print_success "Additional dependencies installed"
                else
                    print_error "Failed to install dependencies"
                    exit 1
                fi

                if command -v ansible-playbook &> /dev/null; then
                    print_success "Ansible already installed"
                else
                    print_info "Installing Ansible..."
                    if retry sudo dnf install -y ansible; then
                        print_success "Ansible installed"
                    else
                        print_error "Failed to install Ansible after retries"
                        exit 1
                    fi
                fi
                ;;

            yum)
                # RHEL 7/CentOS 7
                print_info "Updating package cache..."
                if retry sudo yum check-update || [ $? -eq 100 ]; then
                    print_success "Package cache updated"
                else
                    print_warning "Package cache update returned non-zero (may be normal)"
                fi

                print_info "Installing Development Tools and dependencies..."
                if retry sudo yum groupinstall -y "Development Tools"; then
                    print_success "Development Tools installed"
                else
                    print_error "Failed to install Development Tools"
                    exit 1
                fi

                if retry sudo yum install -y curl git; then
                    print_success "Additional dependencies installed"
                else
                    print_error "Failed to install dependencies"
                    exit 1
                fi

                if command -v ansible-playbook &> /dev/null; then
                    print_success "Ansible already installed"
                else
                    print_info "Installing Ansible..."
                    # EPEL may be needed for Ansible on RHEL/CentOS 7
                    retry sudo yum install -y epel-release || print_warning "EPEL not available or already installed"
                    if retry sudo yum install -y ansible; then
                        print_success "Ansible installed"
                    else
                        print_error "Failed to install Ansible after retries"
                        exit 1
                    fi
                fi
                ;;

            pacman)
                # Arch Linux/Manjaro
                print_info "Updating package database..."
                if retry sudo pacman -Sy --noconfirm; then
                    print_success "Package database updated"
                else
                    print_error "Failed to update package database"
                    exit 1
                fi

                print_info "Installing base-devel and dependencies..."
                if retry sudo pacman -S --noconfirm --needed base-devel curl git; then
                    print_success "Base development tools installed"
                else
                    print_error "Failed to install base-devel"
                    exit 1
                fi

                if command -v ansible-playbook &> /dev/null; then
                    print_success "Ansible already installed"
                else
                    print_info "Installing Ansible..."
                    if retry sudo pacman -S --noconfirm --needed ansible; then
                        print_success "Ansible installed"
                    else
                        print_error "Failed to install Ansible after retries"
                        exit 1
                    fi
                fi
                ;;

            zypper)
                # openSUSE
                print_info "Refreshing repositories..."
                if retry sudo zypper refresh; then
                    print_success "Repositories refreshed"
                else
                    print_error "Failed to refresh repositories"
                    exit 1
                fi

                print_info "Installing development patterns and dependencies..."
                if retry sudo zypper install -y -t pattern devel_basis; then
                    print_success "Development tools installed"
                else
                    print_error "Failed to install development tools"
                    exit 1
                fi

                if retry sudo zypper install -y curl git; then
                    print_success "Additional dependencies installed"
                else
                    print_error "Failed to install dependencies"
                    exit 1
                fi

                if command -v ansible-playbook &> /dev/null; then
                    print_success "Ansible already installed"
                else
                    print_info "Installing Ansible..."
                    if retry sudo zypper install -y ansible; then
                        print_success "Ansible installed"
                    else
                        print_error "Failed to install Ansible after retries"
                        exit 1
                    fi
                fi
                ;;

            *)
                print_error "Unsupported package manager: $PKG_MGR"
                print_error "This script supports: apt (Debian/Ubuntu), dnf (Fedora), yum (RHEL/CentOS), pacman (Arch), zypper (openSUSE)"
                exit 1
                ;;
        esac
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
