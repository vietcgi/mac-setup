#!/usr/bin/env python3
"""
Mac-Setup Interactive Setup Wizard

Provides an interactive CLI interface for configuring and running mac-setup.
Includes progress tracking, validation, and real-time feedback.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import time
from datetime import datetime

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Styles
    SUCCESS = f"{GREEN}{BOLD}"
    ERROR = f"{RED}{BOLD}"
    WARNING = f"{YELLOW}{BOLD}"
    INFO = f"{BLUE}{BOLD}"
    PROMPT = f"{CYAN}{BOLD}"


class ProgressBar:
    """Simple progress bar for terminal."""

    def __init__(self, total: int, description: str = ""):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def update(self, amount: int = 1) -> None:
        """Update progress."""
        self.current = min(self.current + amount, self.total)
        self._display()

    def _display(self) -> None:
        """Display the progress bar."""
        percent = (self.current / self.total) * 100
        filled = int(50 * self.current // self.total)
        bar = f"{'█' * filled}{'░' * (50 - filled)}"

        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        remaining = (self.total - self.current) / rate if rate > 0 else 0

        status = f"{percent:6.1f}% [{bar}] {self.current}/{self.total}"
        time_info = f" [{self._format_time(elapsed)} / {self._format_time(remaining)}]"

        print(f"\r{self.description}: {status}{time_info}", end="", flush=True)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format seconds to readable time."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m"
        else:
            return f"{int(seconds // 3600)}h"

    def finish(self) -> None:
        """Mark progress as complete."""
        self.current = self.total
        self._display()
        print()  # Newline


class SetupWizard:
    """Interactive setup wizard for mac-setup."""

    def __init__(self, project_root: Optional[str] = None):
        """
        Initialize wizard.

        Args:
            project_root: Path to mac-setup project root
        """
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.config = {}
        self.logger = self._setup_logger()
        self._step = 0
        self._total_steps = 8

    def _setup_logger(self) -> logging.Logger:
        """Setup logger."""
        logger = logging.getLogger("mac-setup.wizard")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def run(self) -> Dict[str, Any]:
        """
        Run the interactive setup wizard.

        Returns:
            Configuration dictionary
        """
        self._print_header()

        self._step = 1
        self._ask_environment()

        self._step = 2
        self._ask_enabled_roles()

        self._step = 3
        self._ask_shell()

        self._step = 4
        self._ask_editors()

        self._step = 5
        self._ask_security()

        self._step = 6
        self._ask_backup()

        self._step = 7
        self._ask_verification()

        self._step = 8
        self._confirm_settings()

        return self.config

    def _print_header(self) -> None:
        """Print wizard header."""
        print(f"\n{Colors.INFO}╔════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.INFO}║  Mac-Setup Interactive Configuration  ║{Colors.RESET}")
        print(f"{Colors.INFO}╚════════════════════════════════════════╝{Colors.RESET}\n")

        print("This wizard will help you configure mac-setup for your system.\n")
        print(f"Total steps: {self._total_steps}\n")

    def _step_header(self, title: str) -> None:
        """Print step header."""
        print(f"\n{Colors.INFO}Step {self._step}/{self._total_steps}: {title}{Colors.RESET}\n")

    def _ask_environment(self) -> None:
        """Ask for environment type."""
        self._step_header("Environment Selection")

        print("What environment are you setting up?\n")
        options = [
            ("development", "Development (default tools, all features)"),
            ("production", "Production (minimal, hardened)"),
            ("staging", "Staging (balanced)"),
        ]

        for i, (value, desc) in enumerate(options, 1):
            print(f"  {i}. {desc}")

        while True:
            choice = input(f"\n{Colors.PROMPT}Select (1-{len(options)}): {Colors.RESET}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                self.config["environment"] = options[int(choice) - 1][0]
                print(f"{Colors.SUCCESS}✓ Selected: {self.config['environment']}{Colors.RESET}")
                break
            print(f"{Colors.ERROR}Invalid choice. Please try again.{Colors.RESET}")

    def _ask_enabled_roles(self) -> None:
        """Ask which roles to enable."""
        self._step_header("Role Selection")

        print("Which modules would you like to install?\n")

        roles = [
            ("core", "Core (Homebrew, base system)"),
            ("shell", "Shell (Zsh, Fish)"),
            ("editors", "Editors (Neovim, VS Code)"),
            ("languages", "Languages (Node, Python, Go, Ruby)"),
            ("development", "Development (Git, Docker, formatters)"),
            ("containers", "Containers (Docker, Kubernetes)"),
            ("cloud", "Cloud (AWS, Azure, GCP tools)"),
            ("security", "Security (SSH, GPG, audit)"),
            ("databases", "Databases (PostgreSQL, MongoDB, Redis)"),
        ]

        enabled = []
        for i, (value, desc) in enumerate(roles, 1):
            print(f"  {i}. {desc}")

        print(f"\n{Colors.DIM}Enter role numbers separated by commas (e.g., 1,2,3):{Colors.RESET}")
        print(f"{Colors.DIM}Press Enter for defaults (1,2,3,4,5):{Colors.RESET}")

        while True:
            choice = input(f"\n{Colors.PROMPT}Select roles: {Colors.RESET}").strip()

            if not choice:
                # Use defaults
                enabled = [r[0] for r in roles[:5]]
                break

            try:
                indices = [int(x.strip()) for x in choice.split(",")]
                if all(1 <= i <= len(roles) for i in indices):
                    enabled = [roles[i - 1][0] for i in indices]
                    break
                else:
                    print(f"{Colors.ERROR}Invalid numbers. Please try again.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.ERROR}Invalid input. Please enter numbers separated by commas.{Colors.RESET}")

        self.config["enabled_roles"] = enabled
        print(f"{Colors.SUCCESS}✓ Selected {len(enabled)} roles{Colors.RESET}")

    def _ask_shell(self) -> None:
        """Ask for shell preference."""
        self._step_header("Shell Configuration")

        print("Which shell would you like to use?\n")
        options = [
            ("zsh", "Zsh (recommended, with Oh My Zsh)"),
            ("fish", "Fish (friendly, modern)"),
            ("none", "None (skip shell setup)"),
        ]

        for i, (value, desc) in enumerate(options, 1):
            print(f"  {i}. {desc}")

        while True:
            choice = input(f"\n{Colors.PROMPT}Select (1-{len(options)}): {Colors.RESET}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                self.config["shell"] = options[int(choice) - 1][0]
                print(f"{Colors.SUCCESS}✓ Selected: {self.config['shell']}{Colors.RESET}")
                break
            print(f"{Colors.ERROR}Invalid choice. Please try again.{Colors.RESET}")

    def _ask_editors(self) -> None:
        """Ask for editor preferences."""
        self._step_header("Editor Configuration")

        print("Which editors would you like to install?\n")

        editors = [
            ("neovim", "Neovim (modern Vim with Lua)"),
            ("vscode", "VS Code (lightweight, extensible)"),
            ("jetbrains", "JetBrains IDEs (IntelliJ, PyCharm, etc)"),
        ]

        selected = []
        for editor, desc in editors:
            response = input(f"{Colors.PROMPT}Install {desc}? (y/n): {Colors.RESET}").strip().lower()
            if response in ("y", "yes"):
                selected.append(editor)

        self.config["editors"] = selected if selected else ["neovim"]
        print(f"{Colors.SUCCESS}✓ Selected {len(self.config['editors'])} editors{Colors.RESET}")

    def _ask_security(self) -> None:
        """Ask for security options."""
        self._step_header("Security Configuration")

        print("Security features enhance system hardening.\n")

        security_options = {
            "ssh_setup": "Setup SSH keys (ed25519)",
            "gpg_setup": "Setup GPG keys",
            "audit_logging": "Enable audit logging",
        }

        security_config = {}
        for key, desc in security_options.items():
            response = input(f"{Colors.PROMPT}{desc}? (y/n): {Colors.RESET}").strip().lower()
            security_config[key] = response in ("y", "yes")

        self.config["security"] = security_config
        print(f"{Colors.SUCCESS}✓ Security configuration complete{Colors.RESET}")

    def _ask_backup(self) -> None:
        """Ask for backup settings."""
        self._step_header("Backup Configuration")

        response = input(f"{Colors.PROMPT}Enable automatic backups? (y/n): {Colors.RESET}").strip().lower()
        self.config["backup_enabled"] = response in ("y", "yes")

        if self.config["backup_enabled"]:
            location = input(f"{Colors.PROMPT}Backup location (default ~/.mac-setup/backups): {Colors.RESET}").strip()
            self.config["backup_location"] = location or "~/.mac-setup/backups"
            print(f"{Colors.SUCCESS}✓ Backups enabled at {self.config['backup_location']}{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}⚠ Backups disabled{Colors.RESET}")

    def _ask_verification(self) -> None:
        """Ask for verification settings."""
        self._step_header("Verification Configuration")

        response = input(f"{Colors.PROMPT}Run verification after setup? (y/n): {Colors.RESET}").strip().lower()
        self.config["verify_after_setup"] = response in ("y", "yes")

        if self.config["verify_after_setup"]:
            print(f"{Colors.SUCCESS}✓ Verification will run after setup{Colors.RESET}")
        else:
            print(f"{Colors.WARNING}⚠ Verification skipped{Colors.RESET}")

    def _confirm_settings(self) -> None:
        """Confirm final settings."""
        self._step_header("Confirm Configuration")

        print(f"{Colors.BOLD}Configuration Summary:{Colors.RESET}\n")

        print(f"  Environment:       {Colors.CYAN}{self.config.get('environment', 'N/A')}{Colors.RESET}")
        print(f"  Enabled Roles:     {Colors.CYAN}{', '.join(self.config.get('enabled_roles', []))}{Colors.RESET}")
        print(f"  Shell:             {Colors.CYAN}{self.config.get('shell', 'N/A')}{Colors.RESET}")
        print(f"  Editors:           {Colors.CYAN}{', '.join(self.config.get('editors', []))}{Colors.RESET}")
        print(f"  Backups:           {Colors.CYAN}{'Enabled' if self.config.get('backup_enabled') else 'Disabled'}{Colors.RESET}")
        print(f"  Verification:      {Colors.CYAN}{'Enabled' if self.config.get('verify_after_setup') else 'Disabled'}{Colors.RESET}\n")

        response = input(f"{Colors.PROMPT}Proceed with setup? (y/n): {Colors.RESET}").strip().lower()

        if response not in ("y", "yes"):
            print(f"{Colors.WARNING}Setup cancelled.{Colors.RESET}")
            sys.exit(1)

        print(f"{Colors.SUCCESS}✓ Configuration confirmed. Starting setup...{Colors.RESET}\n")

    def save_config(self, file_path: Optional[str] = None) -> str:
        """
        Save configuration to file.

        Args:
            file_path: Path to save config

        Returns:
            Path to saved config file
        """
        if not file_path:
            file_path = str(Path.home() / ".mac-setup" / "config.yaml")

        import yaml
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

        self.logger.info(f"Configuration saved to {path}")
        return str(path)


def main():
    """Run setup wizard."""
    import argparse

    parser = argparse.ArgumentParser(description="Mac-Setup Interactive Wizard")
    parser.add_argument("--skip-wizard", action="store_true", help="Skip interactive wizard")
    parser.add_argument("--config", help="Custom config file")
    parser.add_argument("--project-root", default=str(Path(__file__).parent.parent))

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    # Create wizard
    wizard = SetupWizard(args.project_root)

    if args.skip_wizard:
        print("Using default configuration...")
        # Use default config
    else:
        # Run interactive wizard
        config = wizard.run()
        config_file = wizard.save_config(args.config)
        print(f"\n{Colors.SUCCESS}Configuration saved to {config_file}{Colors.RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
