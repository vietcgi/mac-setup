#  Copyright (c) 2024 Devkit Contributors
#  SPDX-License-Identifier: MIT
"""Git Configuration Manager.

Handles dynamic reloading of git configuration without requiring
full Ansible playbook re-runs.

Features:
- Detect configuration changes
- Validate git config syntax
- Reload git hooks
- Apply credential helper updates
- Log all changes to audit trail
"""

import argparse
import logging
import subprocess  # noqa: S404
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from cli.utils import Colors


class GitConfigManager:
    """Manage git configuration and reload mechanisms."""

    def __init__(self, home_dir: Optional[str] = None) -> None:
        """Initialize git config manager.

        Args:
            home_dir: Home directory (defaults to $HOME)
        """
        self.home_dir = Path(home_dir or Path.home())
        self.git_config_dir = self.home_dir / ".config" / "git"
        self.git_templates_dir = self.home_dir / ".git-templates"
        self.git_hooks_dir = self.git_templates_dir / "hooks"
        self.git_global_config = self.home_dir / ".gitconfig"
        self.git_local_config = self.home_dir / ".gitconfig.local"
        self.devkit_git_dir = self.home_dir / ".devkit" / "git"
        self.log_dir = self.home_dir / ".devkit" / "logs"

        self.setup_logging()

    def setup_logging(self) -> None:
        """Setup logging for git config changes."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "git_config_reload.log"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def print_status(self, message: str, level: str = "INFO") -> None:
        """Print colored status message.

        Args:
            message: Status message
            level: Log level (INFO, SUCCESS, WARNING, ERROR)
        """
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
        }
        _color = colors.get(level, Colors.RESET)
        _symbol = {
            "INFO": "[i]",
            "SUCCESS": "[+]",
            "WARNING": "[!]",
            "ERROR": "[-]",
        }.get(level, "•")

        self.logger.log(getattr(logging, level, logging.INFO), message)

    def validate_git_config_syntax(self) -> bool:
        """Validate git config file syntax.

        Returns:
            True if valid, False otherwise
        """
        self.print_status("Validating git config syntax...")

        try:
            # Check global config
            if self.git_global_config.exists():
                result = subprocess.run(  # noqa: S603
                    ["git", "config", "--list"],  # noqa: S607
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode != 0:
                    self.print_status(f"Git config validation failed: {result.stderr}", "ERROR")
                    return False

            self.print_status("Git config syntax valid", "SUCCESS")
            return True  # noqa: TRY300

        except subprocess.TimeoutExpired:
            self.print_status("Config validation timed out", "ERROR")
            return False
        except OSError as e:
            self.print_status(f"Config validation error: {e}", "ERROR")
            return False

    def get_current_config(self) -> dict[str, str]:
        """Get current git configuration.

        Returns:
            Dictionary of git config key-value pairs
        """
        try:
            result = subprocess.run(  # noqa: S603
                ["git", "config", "--list", "--null"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            config = {}
            if result.returncode == 0:
                for line in result.stdout.split("\0"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        config[key] = value

            return config  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Error reading config: {e}", "ERROR")
            return {}

    def detect_config_changes(self) -> dict[str, str]:
        """Detect what git config values have changed.

        Returns:
            Dictionary of changed config keys and their new values
        """
        self.print_status("Detecting configuration changes...")

        current_config = self.get_current_config()

        # Read the gitconfig file to compare
        changed: dict[str, str] = {}

        if not self.git_global_config.exists():
            self.print_status("No gitconfig found", "WARNING")
            return changed

        try:
            result = subprocess.run(  # noqa: S603
                [  # noqa: S607
                    "git",
                    "config",
                    "--file",
                    str(self.git_global_config),
                    "--list",
                    "--null",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\0"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        if current_config.get(key) != value:
                            changed[key] = value

            if changed:
                self.print_status(f"Found {len(changed)} configuration changes", "WARNING")
                for key, value in list(changed.items())[:5]:
                    pass
                if len(changed) > 5:
                    pass
            else:
                self.print_status("No configuration changes detected", "SUCCESS")

            return changed  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Error detecting changes: {e}", "ERROR")
            return {}

    def reload_git_config(self) -> bool:
        """Reload git configuration.

        Returns:
            True if successful, False otherwise
        """
        self.print_status("Reloading git configuration...")

        try:
            # Git reads config from files on each invocation
            # We just need to verify it's readable
            result = subprocess.run(  # noqa: S603
                ["git", "config", "--list"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                self.print_status("Git configuration reloaded", "SUCCESS")
                self.logger.info("Git configuration reloaded successfully")
                return True
            self.print_status(f"Reload failed: {result.stderr}", "ERROR")
            return False  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Reload error: {e}", "ERROR")
            return False

    def verify_hooks(self) -> bool:
        """Verify and make git hooks executable.

        Returns:
            True if all hooks are valid, False otherwise
        """
        self.print_status("Verifying git hooks...")

        if not self.git_hooks_dir.exists():
            self.print_status("Hooks directory not found", "WARNING")
            return False

        hooks = ["pre-commit", "commit-msg", "post-commit", "prepare-commit-msg"]
        all_valid = True

        for hook in hooks:
            hook_path = self.git_hooks_dir / hook

            if not hook_path.exists():
                self.print_status(f"  Hook not found: {hook}", "WARNING")
                all_valid = False
                continue

            # Make executable
            try:
                hook_path.chmod(0o755)

                # Verify it's executable
                stat_info = hook_path.stat()
                if not (stat_info.st_mode & 0o111):  # pylint: disable=superfluous-parens
                    self.print_status(f"  Hook not executable: {hook}", "ERROR")
                    all_valid = False
                else:
                    self.print_status(f"  Hook valid: {hook}", "SUCCESS")

            except OSError as e:
                self.print_status(f"  Error with hook {hook}: {e}", "ERROR")
                all_valid = False

        return all_valid

    def create_backup(self) -> Optional[Path]:
        """Create backup of git configuration.

        Returns:
            Path to backup file, None if failed
        """
        if not self.git_global_config.exists():
            return None

        try:
            self.devkit_git_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(tz=UTC).strftime("%Y%m%d_%H%M%S")
            backup_path = self.devkit_git_dir / f"gitconfig.backup.{timestamp}"

            # SECURITY FIX: Enforce 0600 permissions on backup file
            # Git config may contain API keys, SSH keys, auth tokens
            backup_path.write_text(
                self.git_global_config.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            backup_path.chmod(0o600)

            # Verify permissions are correctly set
            stat_info = backup_path.stat()
            if stat_info.st_mode & 0o077:  # Check if world/group readable
                raise PermissionError(
                    f"Backup file has insecure permissions: {oct(stat_info.st_mode)}",
                )

            self.print_status(f"Configuration backed up: {backup_path.name}", "SUCCESS")
            return backup_path  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Backup failed: {e}", "ERROR")
            return None

    def reload_hooks(self) -> bool:
        """Reload git hooks configuration.

        Returns:
            True if successful, False otherwise
        """
        self.print_status("Reloading git hooks...")

        try:
            # Make hooks executable
            if not self.verify_hooks():
                return False

            # Verify hooks can be executed
            test_hook = self.git_hooks_dir / "pre-commit"
            if test_hook.exists():
                result = subprocess.run(  # noqa: S603
                    ["bash", "-n", str(test_hook)],  # noqa: S607
                    capture_output=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode != 0:
                    self.print_status("Hook syntax error", "ERROR")
                    return False

            self.print_status("Hooks reloaded successfully", "SUCCESS")
            self.logger.info("Git hooks reloaded successfully")
            return True  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Hook reload error: {e}", "ERROR")
            return False

    def reload_credential_helpers(self) -> bool:
        """Reload credential helper configuration.

        Returns:
            True if successful, False otherwise
        """
        self.print_status("Reloading credential helpers...")

        try:
            # Get configured credential helper
            result = subprocess.run(  # noqa: S603
                ["git", "config", "--get", "credential.helper"],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                helper = result.stdout.strip()
                self.print_status(f"Credential helper: {helper}", "INFO")
            else:
                self.print_status("Credential helpers verified", "SUCCESS")

            return True  # noqa: TRY300

        except OSError as e:
            self.print_status(f"Credential helper error: {e}", "ERROR")
            return False

    def generate_report(self) -> dict[str, Any]:
        """Generate detailed reload report.

        Returns:
            Dictionary with reload status details
        """
        config = self.get_current_config()

        return {
            "timestamp": datetime.now(tz=UTC).isoformat(),
            "config_status": {
                "user_name": config.get("user.name", "NOT SET"),
                "user_email": config.get("user.email", "NOT SET"),
                "default_editor": config.get("core.editor", "NOT SET"),
                "pull_rebase": config.get("pull.rebase", "false"),
            },
            "hooks_status": {
                "pre_commit": (self.git_hooks_dir / "pre-commit").exists(),
                "commit_msg": (self.git_hooks_dir / "commit-msg").exists(),
                "post_commit": (self.git_hooks_dir / "post-commit").exists(),
                "prepare_commit_msg": (self.git_hooks_dir / "prepare-commit-msg").exists(),
            },
            "directories": {
                "config_dir": str(self.git_config_dir),
                "templates_dir": str(self.git_templates_dir),
                "hooks_dir": str(self.git_hooks_dir),
            },
        }

    def display_report(self, report: dict[str, Any]) -> None:  # noqa: PLR6301
        """Display formatted reload report.

        Args:
            report: Report dictionary from generate_report()
        """
        print(f"\n{Colors.BLUE}Configuration Status:{Colors.RESET}")
        for key, value in report["config_status"].items():
            formatted_key = key.replace("_", " ").title()
            print(f"  {formatted_key}: {Colors.GREEN}{value}{Colors.RESET}")

        print(f"\n{Colors.BLUE}Git Hooks Status:{Colors.RESET}")
        for hook, exists in report["hooks_status"].items():
            formatted_hook = hook.replace("_", " ").title()
            status = f"{Colors.GREEN}✓ Present{Colors.RESET}" if exists else f"{Colors.RED}✗ Missing{Colors.RESET}"
            print(f"  {formatted_hook}: {status}")

        print(f"\n{Colors.BLUE}Directory Paths:{Colors.RESET}")
        for key, path in report["directories"].items():
            formatted_key = key.replace("_", " ").title()
            print(f"  {formatted_key}: {Colors.CYAN}{path}{Colors.RESET}")

    def reload_all(self, dry_run: bool = False) -> bool:  # noqa: FBT001, FBT002
        """Perform complete git configuration reload.

        Args:
            dry_run: If True, only validate without making changes

        Returns:
            True if reload successful, False otherwise
        """
        success = True

        # Validation
        if not self.validate_git_config_syntax():
            return False

        if dry_run:
            self.detect_config_changes()
            self.verify_hooks()
        else:
            # Backup current config
            self.create_backup()

            # Detect changes
            self.detect_config_changes()

            # Reload components
            if not self.reload_git_config():
                success = False

            if not self.reload_hooks():
                success = False

            if not self.reload_credential_helpers():
                success = False

        # Generate and display report
        report = self.generate_report()
        self.display_report(report)

        if success:
            self.print_status("Git configuration reload completed successfully", "SUCCESS")
        else:
            self.print_status("Git configuration reload completed with errors", "ERROR")

        return success

    def reload_component(self, component: str) -> bool:
        """Reload specific git component.

        Args:
            component: Component to reload (config, hooks, credentials)

        Returns:
            True if successful, False otherwise
        """
        if component == "config":
            return self.reload_git_config()
        if component == "hooks":
            return self.reload_hooks()
        if component == "credentials":
            return self.reload_credential_helpers()
        self.print_status(f"Unknown component: {component}", "ERROR")
        return False


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Manage git configuration reload")
    parser.add_argument("--dry-run", action="store_true", help="Validate without making changes")
    parser.add_argument(
        "--component",
        choices=["config", "hooks", "credentials"],
        help="Reload specific component",
    )
    parser.add_argument("--home", help="Home directory (defaults to $HOME)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    manager = GitConfigManager(home_dir=args.home)

    if args.component:
        success = manager.reload_component(args.component)
    else:
        success = manager.reload_all(dry_run=args.dry_run)

    return 0 if success else 1


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "Colors",
    "GitConfigManager",
    "main",
]


if __name__ == "__main__":
    sys.exit(main())
