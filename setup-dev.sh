#!/bin/bash
# Development Environment Setup Script
# Installs all required dependencies for code quality enforcement
#
# Usage: ./setup-dev.sh
# Or:    bash setup-dev.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

echo "=========================================="
echo "Setting up devkit development environment"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"
echo ""

# Upgrade pip
echo -e "${BLUE}Upgrading pip, setuptools, and wheel...${NC}"
python3 -m pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}✓${NC} pip/setuptools/wheel upgraded"
echo ""

# Install requirements
echo -e "${BLUE}Installing quality enforcement tools...${NC}"
echo "Installing from: ${REPO_ROOT}/requirements.txt"
echo ""

if [ -f "${REPO_ROOT}/requirements.txt" ]; then
    python3 -m pip install -r "${REPO_ROOT}/requirements.txt"
    echo ""
    echo -e "${GREEN}✓${NC} All dependencies installed successfully"
else
    echo -e "${YELLOW}Warning: requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Verify installations
echo -e "${BLUE}Verifying tool installations...${NC}"
echo ""

tools_installed=0
tools_required=0

check_tool() {
    local tool=$1
    local command=$2
    tools_required=$((tools_required + 1))

    if command -v "$command" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $tool installed"
        tools_installed=$((tools_installed + 1))
    else
        echo -e "${YELLOW}⚠${NC} $tool not found (but may still work via python -m)"
    fi
}

check_tool "pre-commit" "pre-commit"
check_tool "pytest" "pytest"
check_tool "coverage" "coverage"
check_tool "mypy" "mypy"
check_tool "pylint" "pylint"
check_tool "bandit" "bandit"
check_tool "black" "black"
check_tool "isort" "isort"

echo ""
echo -e "${BLUE}Installation Summary${NC}"
echo "=========================================="
echo -e "Tools found: ${GREEN}${tools_installed}${NC}/${tools_required}"
echo ""

# Test that we can import the modules
echo -e "${BLUE}Testing Python module imports...${NC}"
python3 -c "import pytest; import coverage; import mypy; import pylint; import bandit" 2>/dev/null && \
    echo -e "${GREEN}✓${NC} All Python modules import successfully" || \
    echo -e "${YELLOW}⚠${NC} Some modules may not be available"
echo ""

# Show git hook status
echo -e "${BLUE}Git Hook Configuration${NC}"
echo "=========================================="

if command -v git &> /dev/null; then
    HOOKS_PATH=$(git config --global core.hooksPath 2>/dev/null || echo "not set")
    if [ "$HOOKS_PATH" = "not set" ]; then
        echo -e "${YELLOW}⚠${NC} Global hooks path not configured"
        echo ""
        echo "To enable quality enforcement across all repositories:"
        echo "  git config --global core.hooksPath ~/.git-templates/hooks"
    else
        echo -e "${GREEN}✓${NC} Global hooks path configured: $HOOKS_PATH"
    fi
else
    echo -e "${YELLOW}⚠${NC} Git not found"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Verify tools work:"
echo "     pytest --version"
echo "     mypy --version"
echo "     pylint --version"
echo "     bandit --version"
echo ""
echo "  2. Make sure git hooks are enabled:"
echo "     git config --global core.hooksPath ~/.git-templates/hooks"
echo ""
echo "  3. Try making a test commit to see quality enforcement in action"
echo ""
